import { useId } from 'react'
import type { PageConfig } from '../types/scanner'

type Settings = Pick<PageConfig, 'mode' | 'denoise' | 'contrast' | 'threshold' | 'rotation'>

/** Edits full-config draft only; the existing explicit render action owns HTTP. */
export function FilterPanel({ config, disabled, onChange }: {
  config: PageConfig
  disabled: boolean
  onChange: (settings: Partial<Settings>) => void
}) {
  const id = useId()
  const color = config.mode === 'color'
  const bw = config.mode === 'bw'
  const adaptive = bw && config.threshold.method === 'adaptive_gaussian'
  return <fieldset className="filter-panel" disabled={disabled} aria-describedby={`${id}-help`}>
    <legend>Xử lý bản quét</legend>
    <p id={`${id}-help`} className="muted small">Đổi tham số chỉ sửa nháp. Bấm “Tạo bản quét” để xử lý lại từ ảnh nguồn;
      tham số không hoạt động vẫn được giữ khi đổi chế độ.</p>
    <div className="filter-grid">
      <label>Xoay bản quét
        <select aria-label="Xoay bản quét" value={config.rotation} onChange={e=>onChange({rotation:Number(e.target.value) as PageConfig['rotation']})}>
          <option value="0">0° · giữ nguyên</option><option value="90">90° theo chiều kim đồng hồ</option>
          <option value="180">180°</option><option value="270">270° theo chiều kim đồng hồ</option>
        </select>
      </label>
      <label>Chế độ ảnh
        <select aria-label="Chế độ ảnh" value={config.mode} onChange={e => onChange({ mode: e.target.value as PageConfig['mode'] })}>
          <option value="color">Màu (Color)</option><option value="gray">Thang xám (Gray)</option><option value="bw">Đen trắng (BW)</option>
        </select>
      </label>
      <label>Lọc nhiễu
        <select aria-label="Lọc nhiễu" value={config.denoise.method} onChange={e => onChange({ denoise: { ...config.denoise,
          method: e.target.value as PageConfig['denoise']['method'] } })}>
          <option value="none">Không lọc</option><option value="median">Median</option><option value="gaussian">Gaussian</option>
        </select>
      </label>
      <label>Kernel lọc nhiễu {config.denoise.method === 'none' && <span className="muted">· không hoạt động</span>}
        <select aria-label="Kernel lọc nhiễu" value={config.denoise.kernel} disabled={config.denoise.method === 'none'}
          onChange={e => onChange({ denoise: { ...config.denoise, kernel: Number(e.target.value) } })}>
          <option value={3}>3 × 3</option><option value={5}>5 × 5</option>
        </select>
      </label>
      <label>Tương phản {color && <span className="muted">· không hoạt động ở Color</span>}
        <select aria-label="Tương phản" value={config.contrast.method} disabled={color}
          onChange={e => onChange({ contrast: { ...config.contrast, method: e.target.value as PageConfig['contrast']['method'] } })}>
          <option value="none">Không tăng tương phản</option><option value="clahe">CLAHE</option>
        </select>
      </label>
      <label>Giới hạn CLAHE: {config.contrast.clip_limit}
        <input type="range" min={1} max={4} step={.1} value={config.contrast.clip_limit}
          disabled={color || config.contrast.method !== 'clahe'} aria-label="Giới hạn CLAHE"
          onChange={e => onChange({ contrast: { ...config.contrast, clip_limit: Number(e.target.value) } })} />
        <span className="muted small">1–4 · lưới cố định 8 × 8 ô; chỉ hoạt động khi bật CLAHE ở Gray/BW.</span>
      </label>
      <label>Phương pháp nhị phân {!bw && <span className="muted">· chỉ hoạt động ở BW</span>}
        <select aria-label="Phương pháp nhị phân" value={config.threshold.method} disabled={!bw}
          onChange={e => onChange({ threshold: { ...config.threshold,
            method: e.target.value as PageConfig['threshold']['method'] } })}>
          <option value="otsu">Otsu · ngưỡng toàn ảnh</option>
          <option value="adaptive_gaussian">Adaptive Gaussian · ngưỡng cục bộ</option>
        </select>
      </label>
      <label>Block Adaptive {!adaptive && <span className="muted">· không hoạt động</span>}
        <select aria-label="Block Adaptive" value={config.threshold.block_size} disabled={!adaptive}
          onChange={e => onChange({ threshold: { ...config.threshold, block_size: Number(e.target.value) } })}>
          {Array.from({ length: 75 }, (_, i) => 3 + i * 2).map(n => <option key={n} value={n}>{n} × {n}</option>)}
        </select>
        <span className="muted small">Số lẻ 3–151 pixel, không lớn hơn cạnh ngắn vùng đã warp. Nếu bị từ chối, chọn block nhỏ hơn hoặc Otsu; không tự giảm block.</span>
      </label>
      <label>Hằng số C Adaptive: {config.threshold.c} {!adaptive && <span className="muted">· không hoạt động</span>}
        <input type="range" min={-20} max={30} step={1} value={config.threshold.c}
          disabled={!adaptive} aria-label="Hằng số C Adaptive"
          onChange={e => onChange({ threshold: { ...config.threshold, c: Number(e.target.value) } })} />
        <span className="muted small">Số nguyên −20 đến 30 · ngưỡng cục bộ = trung bình có trọng số Gaussian − C.</span>
      </label>
    </div>
    <p className="muted small">Otsu dùng một ngưỡng cho toàn ảnh, không dùng block/C. Adaptive phù hợp hơn khi sáng không đều nhưng vẫn có thể giữ nhiễu, ô ly hoặc làm đứt nét.</p>
    <p className="muted small">Median có thể xóa nét mảnh; Gaussian làm mềm nét. Đổi chế độ giữ các lựa chọn hiện tại, không tự đặt lại preset.</p>
  </fieldset>
}
