"""Page/config/artifact contracts. Routes/services will enforce membership/CAS."""
from typing import Literal

from pydantic import Field, JsonValue, StrictBool, StrictInt, UUID4, ValidationInfo, field_validator, model_validator

from ..processing.config import Corners, PageConfig, parse_config
from ..processing.geometry import validate_quad
from .common import APIModel, ArtifactKind, Milliseconds, Revision, Timestamp


class ArtifactRead(APIModel):
    id: UUID4
    kind: ArtifactKind
    revision: Revision | None = None
    mime: Literal['image/jpeg','image/png','application/pdf']
    byte_size: StrictInt = Field(gt=0)
    sha256: str = Field(strict=True, pattern=r'^[0-9a-f]{64}$')
    width: StrictInt | None = Field(default=None, ge=1)
    height: StrictInt | None = Field(default=None, ge=1)
    created_at: Timestamp

    @model_validator(mode='after')
    def artifact_shape(self):
        if (self.width is None)!=(self.height is None):
            raise ValueError('Dimensions artifact phải có đủ width/height hoặc cả hai null.')
        derived = self.kind in ('render','preview','debug')
        if derived!=(self.revision is not None):
            raise ValueError('Chỉ artifact render/preview/debug gắn page revision.')
        return self


class ConfigUpdateRequest(APIModel):
    expected_revision: Revision
    config: dict[str, JsonValue]

    def validate_config(self, *, source_size: tuple[int,int], warp_size: tuple[int,int] | None = None) -> PageConfig:
        """Validate after looking up the page; never merge the persisted config.

        Body shape can be parsed before DB lookup. Geometry must wait for real
        EXIF-normalized source dimensions; don't invent dimensions in a route.
        """
        return parse_config(self.config, source_size=source_size, warp_size=warp_size)


class ConfigRead(APIModel):
    page_id: UUID4
    revision: Revision
    effective_config: PageConfig
    inactive_fields: tuple[str,...]


class PageRead(APIModel):
    id: UUID4
    session_id: UUID4
    position: StrictInt = Field(ge=0)
    width: StrictInt = Field(ge=2)
    height: StrictInt = Field(ge=2)
    original_artifact_id: UUID4
    normalized_artifact_id: UUID4
    thumbnail_artifact_id: UUID4
    revision: Revision
    render_revision: Revision | None = None
    latest_render: 'RenderRead | None' = None
    latest_detection: 'DetectionRunRead | None' = None
    effective_config: PageConfig
    created_at: Timestamp
    updated_at: Timestamp

    @field_validator('effective_config', mode='wrap')
    @classmethod
    def source_bound_config(cls, value, handler, info: ValidationInfo) -> PageConfig:
        # Replace the context-free nested parse with the canonical source-bound
        # parser, while retaining PageConfig's normal model serializer/schema.
        return parse_config(value, source_size=(info.data.get('width',0),info.data.get('height',0)))

    @model_validator(mode='after')
    def source_limit(self):
        if self.width*self.height>16_000_000:
            raise ValueError('Nguồn vượt16triệu pixel.')
        if self.render_revision is not None and self.render_revision>self.revision:
            raise ValueError('Render revision không được lớn hơn config revision.')
        if self.latest_render and (self.latest_render.page_id!=self.id or self.latest_render.revision>self.revision):
            raise ValueError('Render lưu không khớp trang/revision.')
        if self.latest_detection and (self.latest_detection.page_id!=self.id
                or self.latest_detection.source_artifact_id!=self.normalized_artifact_id
                or (self.latest_detection.source_width,self.latest_detection.source_height)!=(self.width,self.height)
                or self.latest_detection.source_revision>self.revision):
            raise ValueError('Detection lưu không khớp nguồn trang.')
        return self


class RenderRequest(APIModel):
    expected_revision: Revision
    debug: StrictBool = False


class RenderRead(APIModel):
    page_id: UUID4
    revision: Revision
    render_artifact_id: UUID4
    preview_artifact_id: UUID4
    render_run_id: UUID4 | None = None
    width: StrictInt = Field(ge=2, le=2400)
    height: StrictInt = Field(ge=2, le=2400)
    warnings: tuple[str,...] = ()
    timings_ms: dict[str, Milliseconds]  # scope labels are documented, no pretend stage times


class DetectRequest(APIModel):
    debug: StrictBool = False  # MVP fixes detector revised/Gaussian5; no tuning in API


class DetectRead(APIModel):
    page_id: UUID4
    source_width: StrictInt = Field(ge=2)
    source_height: StrictInt = Field(ge=2)
    status: Literal['proposed','proposed_with_warning','manual_required']
    corners: Corners | None
    heuristic_score: float | None = Field(ge=0, le=1)
    algorithm_version: str = Field(strict=True, min_length=1)
    confirmed: StrictBool = False
    warnings: tuple[str,...] = ()
    timings_ms: dict[str, Milliseconds]

    @model_validator(mode='after')
    def proposal_only(self):
        if self.confirmed or self.source_width*self.source_height>16_000_000:
            raise ValueError('Detection luôn unconfirmed và nguồn trong quota.')
        if (self.status=='manual_required')!=(self.corners is None):
            raise ValueError('Chỉ proposal được trả góc; manual_required phải null.')
        if self.corners is not None:
            validate_quad(self.corners,self.source_width,self.source_height)
            if self.heuristic_score is None:
                raise ValueError('Proposal phải có heuristic_score.')
        return self


class DetectionRunRead(DetectRead):
    run_id: UUID4
    source_artifact_id: UUID4
    source_revision: Revision
    source_sha256: str = Field(strict=True,pattern=r'^[0-9a-f]{64}$')
    selected_trial_id: str | None
    stage_artifacts: dict[str,UUID4]


class DebugQuery(APIModel):
    revision: Revision | None = Field(default=None,le=2**63-1)
    render_run_id: UUID4 | None = None
    detection_run_id: UUID4 | None = None

    @field_validator('revision',mode='before')
    @classmethod
    def query_revision(cls,value):
        if isinstance(value,str):
            if not value.isascii() or not value.isdecimal():raise ValueError('Revision phải là số nguyên không âm.')
            return int(value)
        return value

    @model_validator(mode='after')
    def one_selector(self):
        if sum(v is not None for v in (self.revision,self.render_run_id,self.detection_run_id))>1:
            raise ValueError('Chỉ chọn revision, render_run_id hoặc detection_run_id.')
        return self


class DebugRead(APIModel):
    page_id: UUID4
    kind: Literal['render','detection']
    current_revision: Revision
    revision: Revision | None
    run_id: UUID4 | None
    status: Literal['available','not_requested','not_recorded','incomplete']
    debug_persisted: StrictBool
    created_at: Timestamp | None
    metadata: dict[str,JsonValue] | None
    artifacts: dict[str,ArtifactRead]
    missing_stages: dict[str,Literal['not_found','invalid_metadata','file_unavailable']]


class PageSnapshot(APIModel):
    page_id: UUID4
    revision: Revision


PageRead.model_rebuild()
