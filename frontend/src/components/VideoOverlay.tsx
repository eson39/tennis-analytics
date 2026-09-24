import { useEffect, useRef } from 'react'
import type { CourtData, TrackedPlayer, TrackingData } from '../services/api'
import { findFrameAtTime } from '../lib/trackingSync'

const PLAYER_COLORS = ['#059669', '#d97706']

interface VideoOverlayProps {
  videoRef: React.RefObject<HTMLVideoElement | null>
  court: CourtData | null
  tracking: TrackingData | null
  showCourtKeypoints: boolean
  showBoxes: boolean
  showMarkers: boolean
  currentTime: number
}

export function VideoOverlay({
  videoRef,
  court,
  tracking,
  showCourtKeypoints,
  showBoxes,
  showMarkers,
  currentTime,
}: VideoOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (!canvas || !video) {
      return
    }

    const width = video.clientWidth
    const height = video.clientHeight
    if (width === 0 || height === 0) {
      return
    }

    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width
      canvas.height = height
    }

    const ctx = canvas.getContext('2d')
    if (!ctx) {
      return
    }

    ctx.clearRect(0, 0, width, height)

    const sourceWidth =
      tracking?.frame_width || court?.frame_width || video.videoWidth || width
    const sourceHeight =
      tracking?.frame_height || court?.frame_height || video.videoHeight || height
    const scaleX = width / sourceWidth
    const scaleY = height / sourceHeight

    if (showCourtKeypoints && court?.keypoints?.length) {
      court.keypoints.forEach((point, index) => {
        const x = point[0] * scaleX
        const y = point[1] * scaleY
        ctx.fillStyle = '#ef4444'
        ctx.beginPath()
        ctx.arc(x, y, 5, 0, Math.PI * 2)
        ctx.fill()
        ctx.fillStyle = '#fff'
        ctx.font = '11px IBM Plex Sans, sans-serif'
        ctx.fillText(String(index), x + 6, y - 6)
      })
    }

    const frame = findFrameAtTime(tracking, currentTime)
    const players = (frame?.players ?? []) as TrackedPlayer[]
    players.forEach((player, index) => {
      const color = PLAYER_COLORS[index % PLAYER_COLORS.length]
      const [x1, y1, x2, y2] = player.bbox
      const left = x1 * scaleX
      const top = y1 * scaleY
      const right = x2 * scaleX
      const bottom = y2 * scaleY

      if (showBoxes) {
        ctx.strokeStyle = color
        ctx.lineWidth = 2
        ctx.strokeRect(left, top, right - left, bottom - top)
        ctx.fillStyle = color
        ctx.font = '12px IBM Plex Sans, sans-serif'
        ctx.fillText(`P${player.track_id}`, left + 4, Math.max(12, top - 4))
      }

      if (showMarkers) {
        const [fx, fy] = player.foot
        ctx.fillStyle = color
        ctx.beginPath()
        ctx.arc(fx * scaleX, fy * scaleY, 5, 0, Math.PI * 2)
        ctx.fill()
      }
    })
  }, [
    videoRef,
    court,
    tracking,
    showCourtKeypoints,
    showBoxes,
    showMarkers,
    currentTime,
  ])

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 h-full w-full"
      aria-hidden
    />
  )
}
