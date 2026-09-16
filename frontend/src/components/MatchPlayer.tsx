import type { Match } from '../services/api'
import { matchVideoUrl } from '../services/api'

interface MatchPlayerProps {
  match: Match
  onClose: () => void
  onRemove: () => void
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
  isRemoving = false,
}: MatchPlayerProps) {
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
            </p>
            <p>{formatBytes(match.file_size_bytes)}</p>
          </div>
        </div>
      </div>

      <video
        key={match.match_id}
        controls
        playsInline
        className="aspect-video w-full rounded-lg bg-black"
        src={matchVideoUrl(match)}
      >
        Your browser does not support video playback.
      </video>

      <p className="font-mono text-xs text-slate-500">match_id: {match.match_id}</p>
    </section>
  )
}
