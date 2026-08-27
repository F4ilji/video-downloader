const API_BASE = '/api'
const API_KEY = import.meta.env.VITE_API_KEY || ''

function authHeaders(extra = {}) {
  const headers = { ...extra }
  if (API_KEY) {
    headers['Authorization'] = `Bearer ${API_KEY}`
  }
  return headers
}

export async function getVideoInfo(url) {
  const res = await fetch(`${API_BASE}/video-info?url=${encodeURIComponent(url)}`, {
    headers: authHeaders(),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Failed to get video info')
  }
  return res.json()
}

export async function downloadVideo(url, options = {}) {
  const res = await fetch(`${API_BASE}/download`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ url, ...options }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Download failed')
  }
  return res.json()
}

export async function getTaskStatus(taskId) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error('Task not found')
  return res.json()
}

export function streamProgress(taskId, onProgress, onError) {
  const url = API_KEY
    ? `${API_BASE}/tasks/${taskId}/progress?api_key=${encodeURIComponent(API_KEY)}`
    : `${API_BASE}/tasks/${taskId}/progress`
  const evtSource = new EventSource(url)
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
  const res = await fetch(`${API_BASE}/downloads`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to load downloads')
  return res.json()
}

export async function getActiveTasks() {
  const res = await fetch(`${API_BASE}/tasks/active`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to load active tasks')
  return res.json()
}

export async function deleteTask(taskId) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to delete task')
  return res.json()
}
