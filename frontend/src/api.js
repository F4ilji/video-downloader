const API_BASE = '/api'

export async function downloadVideo(url) {
  const res = await fetch(`${API_BASE}/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Download failed')
  }
  return res.json()
}

export async function getTaskStatus(taskId) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`)
  if (!res.ok) throw new Error('Task not found')
  return res.json()
}

export function streamProgress(taskId, onProgress, onError) {
  const evtSource = new EventSource(`${API_BASE}/tasks/${taskId}/progress`)
  evtSource.onmessage = (e) => {
    const data = JSON.parse(e.data)
    onProgress(data)
    if (data.status === 'completed' || data.status === 'failed') {
      evtSource.close()
    }
  }
  evtSource.onerror = (e) => {
    evtSource.close()
    onError(e)
  }
  return evtSource
}

export async function listDownloads() {
  const res = await fetch(`${API_BASE}/downloads`)
  if (!res.ok) throw new Error('Failed to load downloads')
  return res.json()
}
