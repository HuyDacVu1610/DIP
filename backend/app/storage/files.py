"""Complete immutable artifacts before registering metadata; no image encoding."""
import os
import stat
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

BUCKETS = {'original':'sources','normalized':'sources','thumbnail':'sources',
    'render':'renders','preview':'renders','debug':'debug','pdf':'exports','export_image':'exports'}
EXTENSIONS = {'image/jpeg':'.jpg','image/png':'.png','application/pdf':'.pdf'}


class ArtifactFileError(ValueError):
    code = 'STORAGE_FAILED'


@dataclass(frozen=True, slots=True)
class StoredArtifact:
    id: UUID
    session_id: UUID
    page_id: UUID | None
    kind: str
    revision: int | None
    path: str  # relative to the trusted store root, never a client path
    mime: str
    byte_size: int
    sha256: str
    width: int | None
    height: int | None


def _uuid(value):
    if not isinstance(value,UUID) or value.version!=4:
        raise ArtifactFileError('ID lưu trữ phải là UUIDv4 do server cấp.')


def _relative(sid, aid, kind, mime):
    _uuid(sid)
    _uuid(aid)
    if kind not in BUCKETS or mime not in EXTENSIONS:
        raise ArtifactFileError('Loại artifact hoặc MIME không hỗ trợ.')
    return f'sessions/{sid}/{BUCKETS[kind]}/{aid}{EXTENSIONS[mime]}'


def _publish(source, destination):
    # Windows rename fails if destination exists. POSIX rename replaces it, so
    # use an atomic no-replace hard link there. Both stay on the same filesystem.
    if os.name=='nt':
        os.rename(source,destination)
    else:
        os.link(source,destination)
        source.unlink()


class ArtifactStore:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True,exist_ok=True)

    def _guard(self, path: Path) -> Path:
        """Reject traversal and symlink/junction/reparse children before I/O.

        Trusted local runtime root; not a sandbox against a hostile OS process
        concurrently replacing directories. API callers never supply paths.
        """
        if not path.is_relative_to(self.root) or not path.resolve().is_relative_to(self.root):
            raise ArtifactFileError('Đường dẫn artifact vượt thư mục lưu trữ.')
        current = self.root
        for part in (None,*path.relative_to(self.root).parts):
            if part is not None:
                current = current/part
            try:
                metadata = current.lstat()
            except FileNotFoundError:
                continue
            if stat.S_ISLNK(metadata.st_mode) or getattr(metadata,'st_file_attributes',0)&0x400:
                raise ArtifactFileError('Không theo symlink/junction trong thư mục artifact.')
        return path

    def path_for(self, stored: StoredArtifact) -> Path:
        expected = _relative(stored.session_id,stored.id,stored.kind,stored.mime)
        if stored.path!=expected:
            raise ArtifactFileError('Metadata không khớp đường dẫn UUID của artifact.')
        return self._guard(self.root/expected)

    def write_bytes(self, *, session_id: UUID, page_id: UUID | None, kind: str, mime: str,
                    payload: bytes, revision: int | None = None,
                    width: int | None = None, height: int | None = None) -> StoredArtifact:
        """Persist already-encoded bytes exactly once; no upload byte quota here.

        Encoding/decoding and MIME/content checks happen in processing/service
        before this call. This function never accepts an upload filename/path.
        """
        aid = uuid4()
        relative = _relative(session_id,aid,kind,mime)
        exported = kind in ('pdf','export_image')
        derived = kind in ('render','preview','debug')
        if page_id is not None:
            _uuid(page_id)
        if exported!=(page_id is None) or derived!=(revision is not None):
            raise ArtifactFileError('Owner hoặc revision không khớp loại artifact.')
        if revision is not None and (type(revision) is not int or revision<0):
            raise ArtifactFileError('Revision phải là số nguyên không âm.')
        if (mime=='application/pdf')!=(kind=='pdf') or (kind in ('normalized','thumbnail','render','preview','debug') and mime!='image/png'):
            raise ArtifactFileError('MIME không phù hợp loại artifact.')
        if type(payload) is not bytes or not payload:
            raise ArtifactFileError('Artifact cần payload bytes đã encode, không rỗng.')
        if (width is None)!=(height is None) or any(type(d) is not int or d<1 for d in (width,height) if d is not None):
            raise ArtifactFileError('Dimensions phải là cặp nguyên dương hoặc cả hai null.')
        final = self._guard(self.root/relative)
        temporary = None
        try:
            # Validate each ancestor before creating it; do not mkdir through a
            # user-controlled junction even when its target remains inside root.
            for directory in reversed(final.parent.parents):
                if directory!=self.root and not directory.is_relative_to(self.root):
                    continue
                self._guard(directory).mkdir(exist_ok=True)
            self._guard(final.parent).mkdir(exist_ok=True)
            if final.exists():
                raise ArtifactFileError('Artifact UUID đã tồn tại; không ghi đè.')
            fd,name = tempfile.mkstemp(prefix=f'.{aid}-',suffix='.tmp',dir=final.parent)
            temporary = Path(name)
            with os.fdopen(fd,'wb') as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            self._guard(temporary)
            self._guard(final)
            _publish(temporary,final)
            return StoredArtifact(aid,session_id,page_id,kind,revision,relative,mime,len(payload),
                sha256(payload).hexdigest(),width,height)
        except OSError as error:
            raise ArtifactFileError('Không ghi hoàn tất artifact.') from error
        finally:
            if temporary is not None and temporary.exists():
                self._guard(temporary).unlink()  # only the exact temporary file created above

    def verify(self, stored: StoredArtifact) -> Path:
        path = self.path_for(stored)
        try:
            digest = sha256()
            with path.open('rb') as stream:
                metadata = os.fstat(stream.fileno())
                if not stat.S_ISREG(metadata.st_mode) or metadata.st_size!=stored.byte_size:
                    raise ArtifactFileError('Artifact thiếu hoặc kích thước đã thay đổi.')
                for block in iter(lambda:stream.read(1024*1024),b''):
                    digest.update(block)
            if digest.hexdigest()!=stored.sha256:
                raise ArtifactFileError('Hash artifact đã thay đổi.')
        except OSError as error:
            raise ArtifactFileError('Artifact chưa hoàn tất hoặc không đọc được.') from error
        return path

    def _discard(self, stored: StoredArtifact) -> None:
        """Repository must first prove no DB row references this exact artifact."""
        self.verify(stored).unlink()
