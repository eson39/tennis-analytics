export function findFrameAtTime(
  tracking: { frames: { timestamp_ms: number; players: unknown[] }[] } | null,
  timeSeconds: number,
) {
  if (!tracking || tracking.frames.length === 0) {
    return null
  }

  const targetMs = timeSeconds * 1000
  let lo = 0
  let hi = tracking.frames.length - 1
  let best = tracking.frames[0]

  while (lo <= hi) {
    const mid = (lo + hi) >> 1
    const frame = tracking.frames[mid]
    if (frame.timestamp_ms <= targetMs) {
      best = frame
      lo = mid + 1
    } else {
      hi = mid - 1
    }
  }

  return best
}
