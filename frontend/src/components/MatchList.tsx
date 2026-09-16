import type { Match } from '../services/api'

interface MatchListProps {
  matches: Match[]
  selectedMatchId: string | null
  onSelect: (matchId: string) => void
  onRemove: (matchId: string) => void
  removingMatchId?: string | null
}

export function MatchList({
  matches,
  selectedMatchId,
  onSelect,
  onRemove,
  removingMatchId = null,
}: MatchListProps) {
  if (matches.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-600 shadow-sm">
        No matches uploaded yet.
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Uploaded matches</h2>
      <ul className="mt-4 flex flex-col gap-2">
        {matches.map((match) => {
          const selected = match.match_id === selectedMatchId
          const removing = match.match_id === removingMatchId
          return (
            <li key={match.match_id}>
              <div
                className={`flex items-stretch gap-2 rounded-lg border px-3 py-3 transition ${
                  selected
                    ? 'border-emerald-700 bg-emerald-50'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <button
                  type="button"
                  onClick={() => onSelect(match.match_id)}
                  className="min-w-0 flex-1 text-left"
                  disabled={removing}
                >
                  <p className="truncate text-sm font-medium text-slate-900">
                    {match.original_filename}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {new Date(match.created_at).toLocaleString()} · {match.status}
                  </p>
                </button>
                <button
                  type="button"
                  onClick={() => onRemove(match.match_id)}
                  disabled={removing}
                  className="shrink-0 self-center rounded-md px-2 py-1 text-xs font-medium text-red-700 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                  aria-label={`Remove ${match.original_filename}`}
                >
                  {removing ? 'Removing…' : 'Remove'}
                </button>
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
