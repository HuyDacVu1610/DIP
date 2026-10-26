/** CSS/source transforms and manual draft preflight; backend validation stays authoritative. */
import type { Point, Quad } from '../types/scanner'

export interface Size { readonly width: number; readonly height: number }
export interface CanvasRect extends Size { readonly left: number; readonly top: number }
export interface ContainTransform {
  readonly sourceWidth: number
  readonly sourceHeight: number
  readonly cssWidth: number
  readonly cssHeight: number
  readonly scale: number
  readonly offsetX: number
  readonly offsetY: number
}

function positive(value: number): void {
  if (!Number.isFinite(value) || value <= 0) throw new RangeError('Size/scale must be finite and positive.')
}

function sourceSize(source: Size): void {
  if (![source.width, source.height].every(value => Number.isSafeInteger(value) && value >= 2)) {
    throw new RangeError('Source dimensions must be safe integers >=2 after EXIF.')
  }
}

function finitePoint(point: Point): Point {
  if (!Array.isArray(point) || point.length !== 2 || !point.every(Number.isFinite)) {
    throw new RangeError('Point must contain two finite numbers.')
  }
  return point
}

export function createContainTransform(source: Size, css: Size): ContainTransform {
  sourceSize(source)
  positive(css.width)
  positive(css.height)
  const scale = Math.min(css.width / source.width, css.height / source.height)
  positive(scale)
  return Object.freeze({ sourceWidth: source.width, sourceHeight: source.height,
    cssWidth: css.width, cssHeight: css.height, scale,
    offsetX: (css.width - scale * source.width) / 2,
    offsetY: (css.height - scale * source.height) / 2 })
}

export function sourceToCanvas(point: Point, t: ContainTransform): Point {
  const [x, y] = finitePoint(point)
  return finitePoint([t.offsetX + t.scale * x, t.offsetY + t.scale * y])
}

export function canvasToSource(point: Point, t: ContainTransform): Point {
  const [cx, cy] = finitePoint(point)
  return finitePoint([(cx - t.offsetX) / t.scale, (cy - t.offsetY) / t.scale])
}

export function normalizedToSource(point: Point, source: Size): Point {
  sourceSize(source)
  const [u, v] = finitePoint(point)
  return finitePoint([u * (source.width - 1), v * (source.height - 1)])
}

export function sourceToNormalized(point: Point, source: Size): Point {
  sourceSize(source)
  const [x, y] = finitePoint(point)
  return finitePoint([x / (source.width - 1), y / (source.height - 1)])
}

export function normalizedToCanvas(point: Point, t: ContainTransform): Point {
  return sourceToCanvas(normalizedToSource(point, { width: t.sourceWidth, height: t.sourceHeight }), t)
}

export function canvasToNormalized(point: Point, t: ContainTransform): Point {
  return sourceToNormalized(canvasToSource(point, t), { width: t.sourceWidth, height: t.sourceHeight })
}

/** rect describes the unbordered/unpadded canvas content box; DPR never enters pointer math. */
export function clientToCanvas(point: Point, rect: CanvasRect, t: ContainTransform): Point {
  const [clientX, clientY] = finitePoint(point)
  finitePoint([rect.left, rect.top])
  positive(rect.width)
  positive(rect.height)
  return finitePoint([(clientX - rect.left) * t.cssWidth / rect.width,
    (clientY - rect.top) * t.cssHeight / rect.height])
}

/** Use these actual rounded backing/CSS ratios with ctx.setTransform after each resize. */
export function getCanvasBackingSize(css: Size, dpr: number) {
  positive(css.width)
  positive(css.height)
  positive(dpr)
  const width = Math.max(1, Math.round(css.width * dpr))
  const height = Math.max(1, Math.round(css.height * dpr))
  if (!Number.isSafeInteger(width) || !Number.isSafeInteger(height)) {
    throw new RangeError('Backing dimensions exceed safe integer range.')
  }
  return Object.freeze({ width, height, scaleX: width / css.width, scaleY: height / css.height })
}

export type CornerId = 0 | 1 | 2 | 3

/** Nearest handle within a CSS-pixel radius; equal distances keep the lower ID. */
export function hitTestCorner(point: Point, corners: Quad, t: ContainTransform, radius = 22): CornerId | null {
  finitePoint(point)
  positive(radius)
  let selected: CornerId | null = null
  let nearest = radius
  corners.forEach((corner, id) => {
    const [x, y] = normalizedToCanvas(corner, t)
    const distance = Math.hypot(point[0] - x, point[1] - y)
    if (distance <= radius && (selected === null || distance < nearest)) {
      selected = id as CornerId
      nearest = distance
    }
  })
  return selected
}

export function moveCorner(corners: Quad, id: CornerId, point: Point, t: ContainTransform): Quad {
  if (!Number.isInteger(id) || id < 0 || id > 3) throw new RangeError('Invalid corner ID.')
  const [u, v] = canvasToNormalized(point, t)
  const next = structuredClone(corners)
  next[id] = [Math.max(0, Math.min(1, u)), Math.max(0, Math.min(1, v))]
  return next
}

const quadMessages = {
  INVALID_CORNER_COUNT: 'Vùng cắt cần đúng bốn góc.',
  INVALID_POINT: 'Tọa độ góc phải là số hữu hạn.',
  POINT_OUT_OF_BOUNDS: 'Góc nằm ngoài ảnh nguồn.',
  DUPLICATE_POINTS: 'Hai góc trùng hoặc quá gần nhau.',
  SHORT_EDGE: 'Một cạnh của vùng cắt quá ngắn.',
  DEGENERATE_QUAD: 'Vùng cắt quá nhỏ hoặc có ba góc gần thẳng hàng.',
  SELF_INTERSECTION: 'Các cạnh đối giao hoặc chạm nhau. Hãy giữ đúng thứ tự góc.',
  NON_CONVEX_QUAD: 'Vùng cắt bị lõm. Hãy kéo góc ra ngoài để tạo tứ giác lồi.',
  INVALID_WINDING: 'Thứ tự góc phải theo chiều kim đồng hồ.',
} as const
export interface QuadIssue { code: keyof typeof quadMessages; message: string }

const cross = (a: Point, b: Point, c: Point) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
const distance = (a: Point, b: Point) => Math.hypot(a[0] - b[0], a[1] - b[1])
const epsilon = 1e-6

function intersects(a: Point, b: Point, c: Point, d: Point): boolean {
  const orientation = (p: Point, q: Point, r: Point) => {
    const value = cross(p, q, r)
    return Math.abs(value) <= epsilon * distance(p, q) ? 0 : Math.sign(value)
  }
  const onSegment = (p: Point, q: Point, r: Point) => [0, 1].every(k =>
    r[k] >= Math.min(p[k], q[k]) - epsilon && r[k] <= Math.max(p[k], q[k]) + epsilon)
  const o1 = orientation(a, b, c), o2 = orientation(a, b, d)
  const o3 = orientation(c, d, a), o4 = orientation(c, d, b)
  return o1 * o2 < 0 && o3 * o4 < 0 ||
    o1 === 0 && onSegment(a, b, c) || o2 === 0 && onSegment(a, b, d) ||
    o3 === 0 && onSegment(c, d, a) || o4 === 0 && onSegment(c, d, b)
}

/** Same gates/units/order as processing.geometry.validate_quad; never sort manual handles. */
export function validateDraftQuad(corners: Quad, source: Size): QuadIssue | null {
  sourceSize(source)
  const issue = (code: QuadIssue['code']): QuadIssue => ({ code, message: quadMessages[code] })
  if (!Array.isArray(corners) || corners.length !== 4) return issue('INVALID_CORNER_COUNT')
  for (const point of corners) {
    if (!Array.isArray(point) || point.length !== 2 || !point.every(Number.isFinite)) return issue('INVALID_POINT')
    if (point.some(value => value < 0 || value > 1)) return issue('POINT_OUT_OF_BOUNDS')
  }
  const pixels = corners.map(point => normalizedToSource(point, source))
  const diagonal = Math.hypot(source.width - 1, source.height - 1)
  for (let i = 0; i < 4; i++) {
    for (let j = i + 1; j < 4; j++) {
      if (distance(pixels[i], pixels[j]) <= epsilon * diagonal) return issue('DUPLICATE_POINTS')
    }
  }
  for (let i = 0; i < 4; i++) {
    if (distance(pixels[i], pixels[(i + 1) % 4]) <= 1e-3 * diagonal) return issue('SHORT_EDGE')
  }
  const scaled = pixels.map(([x, y]): Point => [x / diagonal, y / diagonal])
  const turns = scaled.map((a, i) => cross(a, scaled[(i + 1) % 4], scaled[(i + 2) % 4]))
  if (turns.some((turn, i) => Math.abs(turn) <= epsilon * Math.max(
    distance(scaled[i], scaled[(i + 1) % 4]), distance(scaled[(i + 1) % 4], scaled[(i + 2) % 4])))) {
    return issue('DEGENERATE_QUAD')
  }
  if (intersects(scaled[0], scaled[1], scaled[2], scaled[3]) || intersects(scaled[1], scaled[2], scaled[3], scaled[0])) {
    return issue('SELF_INTERSECTION')
  }
  const area = (cross(scaled[0], scaled[1], scaled[2]) + cross(scaled[0], scaled[2], scaled[3])) / 2
  if (Math.abs(area) <= epsilon) return issue('DEGENERATE_QUAD')
  if (!turns.every(turn => turn > 0) && !turns.every(turn => turn < 0)) return issue('NON_CONVEX_QUAD')
  return area < 0 ? issue('INVALID_WINDING') : null
}
