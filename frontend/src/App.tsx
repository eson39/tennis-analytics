import { useEffect, useState } from 'react'
import { MatchList } from './components/MatchList'
import { MatchPlayer } from './components/MatchPlayer'
import { VideoUpload } from './components/VideoUpload'
import { deleteMatch, getMatch, listMatches, type Match } from './services/api'

export default function App() {
  const [matches, setMatches] = useState<Match[]>([])
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [removingMatchId, setRemovingMatchId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function refreshMatches(preferredMatchId?: string) {
    setError(null)
    const nextMatches = await listMatches()
    setMatches(nextMatches)

    const preferred =
      (preferredMatchId
        ? nextMatches.find((match) => match.match_id === preferredMatchId)
        : undefined) ??
      nextMatches.find((match) => match.match_id === selectedMatch?.match_id) ??
      null

    setSelectedMatch(preferred)
  }

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        await refreshMatches()
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load matches')
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    void load()

    return () => {
      cancelled = true
    }
    // Initial load only.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function handleSelect(matchId: string) {
    setError(null)
    try {
      const match = await getMatch(matchId)
      setSelectedMatch(match)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load match')
    }
  }

  async function handleUploaded(matchId: string) {
    setIsLoading(true)
    try {
      await refreshMatches(matchId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh matches')
    } finally {
      setIsLoading(false)
    }
  }

  async function handleRemove(matchId: string) {
    const match = matches.find((item) => item.match_id === matchId)
    const label = match?.original_filename ?? 'this match'
    const confirmed = window.confirm(`Remove ${label}? This cannot be undone.`)
    if (!confirmed) {
      return
    }

    setRemovingMatchId(matchId)
    setError(null)

    try {
      await deleteMatch(matchId)
      const nextMatches = matches.filter((item) => item.match_id !== matchId)
      setMatches(nextMatches)
      if (selectedMatch?.match_id === matchId) {
        setSelectedMatch(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove match')
    } finally {
      setRemovingMatchId(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-100 via-slate-50 to-emerald-50/40">
      <header className="border-b border-slate-200/80 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-baseline justify-between gap-4 px-4 py-5 sm:px-6">
          <div>
            <p className="text-2xl font-semibold tracking-tight text-slate-900">CourtVision</p>
            <p className="mt-1 text-sm text-slate-600">
              Upload a match video and play it back.
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl gap-6 px-4 py-8 sm:px-6 lg:grid-cols-[320px_minmax(0,1fr)]">
        <aside className="flex flex-col gap-6">
          <VideoUpload onUploaded={handleUploaded} disabled={isLoading} />
          {isLoading ? (
            <div className="rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-600 shadow-sm">
              Loading matches…
            </div>
          ) : (
            <MatchList
              matches={matches}
              selectedMatchId={selectedMatch?.match_id ?? null}
              onSelect={handleSelect}
              onRemove={handleRemove}
              removingMatchId={removingMatchId}
            />
          )}
        </aside>

        <div className="flex flex-col gap-4">
          {error ? (
            <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
              {error}
            </p>
          ) : null}

          {selectedMatch ? (
            <MatchPlayer
              match={selectedMatch}
              onClose={() => setSelectedMatch(null)}
              onRemove={() => void handleRemove(selectedMatch.match_id)}
              isRemoving={removingMatchId === selectedMatch.match_id}
            />
          ) : (
            <div className="rounded-xl border border-dashed border-slate-300 bg-white/70 p-10 text-center text-sm text-slate-600">
              {matches.length > 0
                ? 'Select a match from the list to watch it here.'
                : 'Upload a video to start watching it here.'}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
