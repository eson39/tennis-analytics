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
  progress: number | null
  error_message: string | null
  has_tracking: boolean
  has_court: boolean
}

export interface MatchCreateResponse {
  match_id: string
  status: MatchStatus
  original_filename: string
  created_at: string
}

export interface MatchStatusResponse {
  match_id: string
  status: MatchStatus
  progress: number | null
  error_message: string | null
  has_tracking: boolean
  has_court: boolean
}

export interface CourtData {
  method: string
  num_keypoints: number
  keypoints: number[][]
  frame_index: number
  frame_width: number
  frame_height: number
  fps: number
  frame_count: number
}

export interface TrackedPlayer {
  track_id: number
  source_track_id?: number
  bbox: [number, number, number, number]
  center: [number, number]
  foot: [number, number]
}

export interface TrackingFrame {
  frame_index: number
  timestamp_ms: number
  players: TrackedPlayer[]
}

export interface TrackingData {
  fps: number
  frame_width: number
  frame_height: number
  frame_count: number
  frame_stride: number
  chosen_source_track_ids: number[]
  frames: TrackingFrame[]
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

export async function getMatchStatus(matchId: string): Promise<MatchStatusResponse> {
  const response = await fetch(`${API_BASE}/matches/${matchId}/status`)
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

export async function reprocessMatch(matchId: string): Promise<MatchStatusResponse> {
  const response = await fetch(`${API_BASE}/matches/${matchId}/process`, {
    method: 'POST',
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

export async function getCourt(matchId: string): Promise<CourtData> {
  const response = await fetch(`${API_BASE}/matches/${matchId}/court`)
  if (!response.ok) {
    throw new Error(await readError(response))
  }
  const data = (await response.json()) as { court: CourtData }
  return data.court
}

export async function getTracking(matchId: string): Promise<TrackingData> {
  const response = await fetch(`${API_BASE}/matches/${matchId}/tracking`)
  if (!response.ok) {
    throw new Error(await readError(response))
  }
  const data = (await response.json()) as { tracking: TrackingData }
  return data.tracking
}

export function matchVideoUrl(match: Match): string {
  return `${API_BASE}${match.video_url}`
}

export function isProcessingStatus(status: MatchStatus): boolean {
  return status === 'queued' || status === 'processing' || status === 'analyzing'
}
