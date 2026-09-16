import { useEffect, useRef } from 'react'
import type { CourtData } from '../services/api'

interface VideoOverlayProps {
  videoRef: React.RefObject<HTMLVideoElement | null>
  court: CourtData | null
  showCourtKeypoints: boolean
}

export function VideoOverlay({
  videoRef,
  court,
  showCourtKeypoints,
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

    if (!showCourtKeypoints || !court?.keypoints?.length) {
      return
    }

    const sourceWidth = court.frame_width || video.videoWidth || width
    const sourceHeight = court.frame_height || video.videoHeight || height
    const scaleX = width / sourceWidth
    const scaleY = height / sourceHeight

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
  }, [videoRef, court, showCourtKeypoints])

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 h-full w-full"
      aria-hidden
    />
  )
}
