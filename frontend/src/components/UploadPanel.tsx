import { useMemo, useState } from 'react'
import { createUploadBatch } from './uploadBatch'
import type { Outcome } from './uploadBatch'

interface Props {
  disabled: boolean
  busy: boolean
  remainingSlots: number
  onBusy: (busy: boolean) => void
  onUpload: (file: File,onDetecting:()=>void) => Promise<string|void>
  onFinished: () => Promise<void>
}

export function UploadPanel({ disabled, busy, remainingSlots, onBusy, onUpload, onFinished }: Props) {
  const [results, setResults] = useState<Outcome[]>([])
  // Keep the batch lock across renders, but refresh its implementation on hot updates.
  const runBatch = useMemo(createUploadBatch, [createUploadBatch])
  async function importFiles(files: File[]) {
    if (!files.length || busy || disabled) return
    await runBatch({files,remainingSlots,onBusy,onUpload,onFinished,onResults:setResults})
  }
  return <section className="upload-panel" aria-labelledby="upload-title">
    <h3 id="upload-title">Thêm ảnh vào tài liệu</h3>
    <p className="muted small">JPEG hoặc PNG · tối đa 15 MiB/ảnh, 16 triệu pixel · 20 trang/tài liệu.</p>
    <p className="muted small">Mỗi ảnh nhập sẽ tự nhận diện vùng. Duyệt từng trang để kiểm tra, chỉnh góc và xác nhận.</p>
    <p className="muted small">{remainingSlots>0?`Còn chỗ cho ${remainingSlots} trang. Thêm ảnh giữ nguyên trang đang xem và các chỉnh sửa của bạn.`:'Tài liệu đã đủ 20 trang.'}</p>
    <label className="file-label" htmlFor="document-images">Chọn ảnh tài liệu</label>
    <input id="document-images" type="file" accept="image/jpeg,image/png" multiple disabled={disabled || busy}
      onChange={event => {
        const files = Array.from(event.target.files ?? [])
        event.target.value = ''
        void importFiles(files)
      }} />
    {busy && <p role="status">Đang nhập và nhận diện lần lượt từng ảnh. Vui lòng giữ trang này mở.</p>}
    {results.length > 0 && <ul className="upload-results" aria-label="Kết quả nhập ảnh" aria-live="polite">
      {results.map((item, index) => <li key={index} data-state={item.state}>
        <span>{item.name}</span><strong>{item.message}</strong>
      </li>)}
    </ul>}
  </section>
}
