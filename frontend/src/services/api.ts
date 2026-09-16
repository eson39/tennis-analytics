export type MatchStatus =
  | 'uploaded'
  | 'queued'
  | 'processing'
  | 'analyzing'
  | 'completed'
  | 'failed'

export interface Match {
  match_id: string
  status: MatchStatus
  original_filename: string
  content_type: string | null
  file_size_bytes: number
  created_at: string
  video_url: string
}

export interface MatchCreateResponse {
  match_id: string
  status: MatchStatus
  original_filename: string
  created_at: string
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

async function readError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string }
    return data.detail ?? `Request failed (${response.status})`
  } catch {
    return `Request failed (${response.status})`
  }
}

export async function listMatches(): Promise<Match[]> {
  const response = await fetch(`${API_BASE}/matches`)
  if (!response.ok) {
    throw new Error(await readError(response))
  }
  return response.json()
}

export async function getMatch(matchId: string): Promise<Match> {
  const response = await fetch(`${API_BASE}/matches/${matchId}`)
  if (!response.ok) {
    throw new Error(await readError(response))
  }
  return response.json()
}

export async function uploadMatch(file: File): Promise<MatchCreateResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/matches`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  return response.json()
}

export async function deleteMatch(matchId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/matches/${matchId}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error(await readError(response))
  }
}

export function matchVideoUrl(match: Match): string {
  return `${API_BASE}${match.video_url}`
}
