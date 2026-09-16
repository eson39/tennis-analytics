import { useRef, useState } from 'react'
import { uploadMatch } from '../services/api'

interface VideoUploadProps {
  onUploaded: (matchId: string) => void
  disabled?: boolean
}

export function VideoUpload({ onUploaded, disabled = false }: VideoUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selectedFile || isUploading) {
      return
    }

    setIsUploading(true)
    setError(null)

    try {
      const result = await uploadMatch(selectedFile)
      setSelectedFile(null)
      if (inputRef.current) {
        inputRef.current.value = ''
      }
      onUploaded(result.match_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Upload match video</h2>
        <p className="mt-1 text-sm text-slate-600">
          Record from behind the baseline, then upload an MP4, MOV, or WebM file.
        </p>
      </div>

      <label className="flex cursor-pointer flex-col items-start gap-2 rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-6 transition hover:border-slate-400 hover:bg-slate-100">
        <span className="text-sm font-medium text-slate-800">
          {selectedFile ? selectedFile.name : 'Choose a video file'}
        </span>
        <span className="text-xs text-slate-500">
          {selectedFile
            ? `${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB`
            : 'Click to browse'}
        </span>
        <input
          ref={inputRef}
          type="file"
          accept="video/mp4,video/quicktime,video/webm,video/x-matroska,video/avi,.mp4,.mov,.webm,.mkv,.avi"
          className="sr-only"
          disabled={disabled || isUploading}
          onChange={(event) => {
            const file = event.target.files?.[0] ?? null
            setSelectedFile(file)
            setError(null)
          }}
        />
      </label>

      {error ? (
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
          {error}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={!selectedFile || disabled || isUploading}
        className="inline-flex items-center justify-center rounded-lg bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {isUploading ? 'Uploading…' : 'Upload video'}
      </button>
    </form>
  )
}
