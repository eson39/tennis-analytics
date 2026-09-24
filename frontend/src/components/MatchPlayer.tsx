import { useEffect, useRef, useState } from 'react'
import type { CourtData, Match, TrackingData } from '../services/api'
import {
  getCourt,
  getTracking,
  isProcessingStatus,
  matchVideoUrl,
  reprocessMatch,
} from '../services/api'
import { VideoOverlay } from './VideoOverlay'

interface MatchPlayerProps {
  match: Match
  onClose: () => void
  onRemove: () => void
  onMatchUpdate: (match: Match) => void
  isRemoving?: boolean
}

function formatBytes(bytes: number): string {
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function MatchPlayer({
  match,
  onClose,
  onRemove,
  onMatchUpdate,
  isRemoving = false,
}: MatchPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [court, setCourt] = useState<CourtData | null>(null)
  const [tracking, setTracking] = useState<TrackingData | null>(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [isReprocessing, setIsReprocessing] = useState(false)
  const [showCourtKeypoints, setShowCourtKeypoints] = useState(true)
  const [showBoxes, setShowBoxes] = useState(true)
  const [showMarkers, setShowMarkers] = useState(true)

  useEffect(() => {
    const video = videoRef.current
    if (!video) {
      return
    }
    const onTimeUpdate = () => setCurrentTime(video.currentTime)
    const onSeeked = () => setCurrentTime(video.currentTime)
    video.addEventListener('timeupdate', onTimeUpdate)
    video.addEventListener('seeked', onSeeked)
    return () => {
      video.removeEventListener('timeupdate', onTimeUpdate)
      video.removeEventListener('seeked', onSeeked)
    }
  }, [match.match_id])

  useEffect(() => {
    let cancelled = false

    async function loadArtifacts() {
      setLoadError(null)
      setCourt(null)
      setTracking(null)

      try {
        if (match.has_court) {
          const nextCourt = await getCourt(match.match_id)
          if (!cancelled) {
            setCourt(nextCourt)
          }
        }
        if (match.has_tracking) {
          const nextTracking = await getTracking(match.match_id)
          if (!cancelled) {
            setTracking(nextTracking)
          }
        }
      } catch (err) {
        if (!cancelled) {
          setLoadError(err instanceof Error ? err.message : 'Failed to load analytics')
        }
      }
    }

    void loadArtifacts()
    return () => {
      cancelled = true
    }
  }, [match.match_id, match.has_court, match.has_tracking, match.status])

  async function handleReprocess() {
    setIsReprocessing(true)
    setLoadError(null)
    try {
      const status = await reprocessMatch(match.match_id)
      onMatchUpdate({
        ...match,
        status: status.status,
        progress: status.progress,
        error_message: status.error_message,
        has_tracking: status.has_tracking,
        has_court: status.has_court,
      })
      setCourt(null)
      setTracking(null)
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to reprocess')
    } finally {
      setIsReprocessing(false)
    }
  }

  const processing = isProcessingStatus(match.status)
  const progressPct = Math.round((match.progress ?? 0) * 100)

  return (
    <section className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Match playback</h2>
          <p className="mt-1 text-sm text-slate-600">{match.original_filename}</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="flex flex-wrap justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isRemoving}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              View another video
            </button>
            <button
              type="button"
              onClick={() => void handleReprocess()}
              disabled={isRemoving || isReprocessing || processing}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isReprocessing ? 'Queuing…' : 'Reprocess'}
            </button>
            <button
              type="button"
              onClick={onRemove}
              disabled={isRemoving}
              className="rounded-lg border border-red-200 bg-white px-3 py-1.5 text-sm font-medium text-red-700 transition hover:border-red-300 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isRemoving ? 'Removing…' : 'Remove match'}
            </button>
          </div>
          <div className="text-right text-xs text-slate-500">
            <p>
              Status: <span className="font-medium text-slate-700">{match.status}</span>
              {processing ? ` · ${progressPct}%` : null}
            </p>
            <p>{formatBytes(match.file_size_bytes)}</p>
          </div>
        </div>
      </div>

      {processing ? (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
          Processing… {match.error_message ?? 'court keypoints + player tracking'}
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-emerald-100">
            <div
              className="h-full rounded-full bg-emerald-600 transition-all"
              style={{ width: `${Math.max(progressPct, 4)}%` }}
            />
          </div>
        </div>
      ) : null}

      {match.status === 'failed' ? (
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
          Processing failed{match.error_message ? `: ${match.error_message}` : '.'}
        </p>
      ) : null}

      {match.status === 'completed' && match.error_message ? (
        <p className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
          {match.error_message}
        </p>
      ) : null}

      {loadError ? (
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
          {loadError}
        </p>
      ) : null}

      <div className="relative overflow-hidden rounded-lg bg-black">
        <video
          ref={videoRef}
          key={match.match_id}
          controls
          playsInline
          className="aspect-video w-full"
          src={matchVideoUrl(match)}
        >
          Your browser does not support video playback.
        </video>
        <VideoOverlay
          videoRef={videoRef}
          court={court}
          tracking={tracking}
          showCourtKeypoints={showCourtKeypoints}
          showBoxes={showBoxes}
          showMarkers={showMarkers}
          currentTime={currentTime}
        />
      </div>

      <div className="flex flex-wrap gap-3 text-sm text-slate-700">
        <label className="inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={showCourtKeypoints}
            onChange={(event) => setShowCourtKeypoints(event.target.checked)}
          />
          Court keypoints
        </label>
        <label className="inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={showBoxes}
            onChange={(event) => setShowBoxes(event.target.checked)}
          />
          Player boxes
        </label>
        <label className="inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={showMarkers}
            onChange={(event) => setShowMarkers(event.target.checked)}
          />
          Foot markers
        </label>
      </div>

      <p className="font-mono text-xs text-slate-500">match_id: {match.match_id}</p>
    </section>
  )
}
