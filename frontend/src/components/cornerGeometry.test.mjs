// Node's native runner executes the actual TypeScript module; no test dependency.
import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  createContainTransform, sourceToCanvas, canvasToSource,
  normalizedToSource, sourceToNormalized, normalizedToCanvas, canvasToNormalized,
  clientToCanvas, getCanvasBackingSize,
  hitTestCorner, moveCorner, validateDraftQuad,
} from './cornerGeometry.ts'

function near(actual, expected, tolerance = 1e-8) {
  assert.equal(actual.length, expected.length)
  actual.forEach((value, index) => assert.ok(Math.abs(value - expected[index]) <= tolerance,
    `${value} differs from ${expected[index]}`))
}

test('contain uses bitmap W/H, while normalized endpoints use pixel W−1/H−1', () => {
  const t = createContainTransform({ width: 480, height: 640 }, { width: 640, height: 480 })
  assert.equal(t.scale, .75)
  assert.equal(t.offsetX, 140)
  assert.equal(t.offsetY, 0)
  near(normalizedToCanvas([0, 0], t), [140, 0])
  near(normalizedToCanvas([1, 1], t), [499.25, 479.25])
  near(normalizedToSource([.5, .5], { width: 101, height: 51 }), [50, 25])
  near(sourceToNormalized([50, 25], { width: 101, height: 51 }), [.5, .5])
})

for (const source of [{ width: 480, height: 640 }, { width: 1536, height: 1024 },
  { width: 2, height: 2 }, { width: 8_000_000, height: 2 }]) {
  for (const css of [{ width: 320, height: 480 }, { width: 640, height: 360 },
    { width: 333.3, height: 201.25 }]) {
    test(`round-trip source ${source.width}×${source.height}, CSS ${css.width}×${css.height}`, () => {
      const t = createContainTransform(source, css)
      const rect = { left: 83.25, top: 17.5, width: css.width * 1.25, height: css.height * .8 }
      for (const point of [[0, 0], [1, 0], [1, 1], [0, 1], [.1234567, .7654321]]) {
        const canvas = normalizedToCanvas(point, t)
        const pixel = normalizedToSource(point, source)
        near(sourceToCanvas(pixel, t), canvas)
        near(canvasToSource(canvas, t), pixel, 1e-7)
        const client = [rect.left + canvas[0] * rect.width / css.width,
          rect.top + canvas[1] * rect.height / css.height]
        const mapped = clientToCanvas(client, rect, t)
        near(mapped, canvas)
        // Acceptance error is in CSS pixels, including letterbox and CSS transform.
        near(normalizedToCanvas(canvasToNormalized(mapped, t), t), canvas, 1e-6)
      }
    })
  }
}

test('resizing recomputes contain from source, with no accumulated transform', () => {
  const source = { width: 1200, height: 800 }
  const wide = createContainTransform(source, { width: 600, height: 300 })
  const narrow = createContainTransform(source, { width: 300, height: 600 })
  near(normalizedToCanvas([0, 0], wide), [75, 0])
  near(normalizedToCanvas([0, 0], narrow), [0, 200])
  near(normalizedToCanvas([1, 1], narrow), [299.75, 399.75])
  near(normalizedToCanvas([0, 0], wide), [75, 0])
})

for (const dpr of [1, 1.25, 2]) {
  test(`DPR ${dpr}: rounded backing store scales, pointer remains CSS pixels`, () => {
    const css = { width: 333.3, height: 201.25 }
    const t = createContainTransform({ width: 480, height: 640 }, css)
    const backing = getCanvasBackingSize(css, dpr)
    assert.equal(backing.width, Math.round(css.width * dpr))
    assert.equal(backing.height, Math.round(css.height * dpr))
    near([backing.scaleX * css.width, backing.scaleY * css.height], [backing.width, backing.height])
    near(clientToCanvas([20, 30], { left: 0, top: 0, ...css }, t), [20, 30])
  })
}

test('mapping stays continuous outside the image; no hidden clamp or handle sorting', () => {
  const t = createContainTransform({ width: 480, height: 640 }, { width: 640, height: 480 })
  const outside = canvasToNormalized([0, -5], t)
  assert.ok(outside[0] < 0 && outside[1] < 0)
  near(normalizedToCanvas(outside, t), [0, -5])
  const source = [.1, .9]
  const before = [...source]
  normalizedToCanvas(source, t)
  assert.deepEqual(source, before)
})

for (const source of [{ width: 1, height: 4 }, { width: 4.5, height: 6 },
  { width: Infinity, height: 4 }, { width: Number.MAX_SAFE_INTEGER + 1, height: 2 }]) {
  test(`reject invalid source dimensions ${JSON.stringify(source)}`, () => {
    assert.throws(() => createContainTransform(source, { width: 320, height: 240 }), RangeError)
  })
}

for (const css of [{ width: 0, height: 100 }, { width: -1, height: 100 },
  { width: NaN, height: 100 }, { width: Infinity, height: 100 }]) {
  test(`reject unusable CSS size ${JSON.stringify(css)}`, () => {
    assert.throws(() => createContainTransform({ width: 100, height: 100 }, css), RangeError)
    assert.throws(() => getCanvasBackingSize(css, 2), RangeError)
  })
}

test('reject nonfinite points, zero rect, invalid DPR and backing overflow', () => {
  const t = createContainTransform({ width: 100, height: 100 }, { width: 320, height: 240 })
  for (const point of [[NaN, 0], [0, Infinity], ['1', 2], [1], null]) {
    assert.throws(() => normalizedToCanvas(point, t), RangeError)
    assert.throws(() => canvasToSource(point, t), RangeError)
  }
  assert.throws(() => clientToCanvas([0, 0], { left: 0, top: 0, width: 0, height: 1 }, t), RangeError)
  for (const dpr of [0, -1, NaN, Infinity]) {
    assert.throws(() => getCanvasBackingSize({ width: 320, height: 240 }, dpr), RangeError)
  }
  assert.throws(() => getCanvasBackingSize({ width: 1e308, height: 1 }, 2), RangeError)
})

const fullQuad = [[0, 0], [1, 0], [1, 1], [0, 1]]
const square = { width: 1001, height: 1001 }
test('hit test uses CSS distance, keeps IDs/tie order and ignores empty letterbox', () => {
  const t = createContainTransform(square, { width: 500, height: 300 })
  const p = normalizedToCanvas([0, 0], t)
  assert.equal(hitTestCorner([p[0] + 21, p[1]], fullQuad, t), 0)
  assert.equal(hitTestCorner([p[0] + 23, p[1]], fullQuad, t), null)
  assert.equal(hitTestCorner([0, 100], fullQuad, t), null)
  assert.equal(hitTestCorner(p, [[0,0],[0,0],[1,1],[0,1]], t), 0)
})

test('moving a handle clamps normalized source bounds, preserves every other ID and input', () => {
  const t = createContainTransform(square, { width: 500, height: 300 })
  const before = structuredClone(fullQuad)
  const changed = moveCorner(fullQuad, 0, [-100, 1000], t)
  assert.deepEqual(changed, [[0, 1], fullQuad[1], fullQuad[2], fullQuad[3]])
  assert.deepEqual(fullQuad, before)
  const subpixel = normalizedToCanvas([.123456, .654321], t)
  near(moveCorner(fullQuad, 2, subpixel, t)[2], [.123456, .654321])
  assert.throws(() => moveCorner(fullQuad, 4, subpixel, t), RangeError)
})

for (const source of [square,{ width: 480, height: 640 },{ width: 2000, height: 100 },{ width: 2, height: 2 }]) {
  for (const quad of [fullQuad, [[.5,0],[1,.5],[.5,1],[0,.5]], [[.1,.2],[.8,.1],[.9,.8],[.2,.9]]]) {
    test(`valid manual quad on ${source.width}x${source.height}: ${JSON.stringify(quad[0])}`, () => {
      assert.equal(validateDraftQuad(quad, source), null)
    })
  }
}

for (const [quad,code] of [
  [[[0,0],[0,0],[1,1],[0,1]],'DUPLICATE_POINTS'],
  [[[0,0],[.0005,0],[1,1],[0,1]],'SHORT_EDGE'],
  [[[0,0],[.5,0],[1,0],[0,1]],'DEGENERATE_QUAD'],
  [[[0,0],[1,1],[1,0],[0,1]],'SELF_INTERSECTION'],
  [[[0,0],[1,0],[.2,.2],[0,1]],'NON_CONVEX_QUAD'],
  [[[0,0],[0,1],[1,1],[1,0]],'INVALID_WINDING'],
  [[[-.1,0],[1,0],[1,1],[0,1]],'POINT_OUT_OF_BOUNDS'],
  [[[NaN,0],[1,0],[1,1],[0,1]],'INVALID_POINT'],
  [[[0,0],[1,0],[1,1]],'INVALID_CORNER_COUNT'],
]) {
  test(`invalid quad reports ${code} and is never silently reordered`, () => {
    const before = structuredClone(quad)
    const issue = validateDraftQuad(quad, square)
    assert.equal(issue?.code, code)
    assert.ok(issue.message.length > 0)
    assert.deepEqual(quad, before)
  })
}

test('relative gates use pixel diagonal, not unequal normalized axis units or detector 10% area', () => {
  const small = [[.1,.1],[.11,.1],[.11,.11],[.1,.11]]
  assert.equal(validateDraftQuad(small, square), null)
  assert.equal(validateDraftQuad(fullQuad, {width:2,height:8_000_000})?.code, 'DUPLICATE_POINTS')
})
