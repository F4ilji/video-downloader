<template>
  <div class="download-list" v-if="downloads.length">
    <h2>Скачанные видео</h2>
    <div v-for="item in downloads" :key="item.filename || item.task_id" class="item">
      <img v-if="item.thumbnail" :src="item.thumbnail" class="thumb" />
      <div class="info">
        <span class="title">{{ item.title || item.filename }}</span>
        <span class="meta">
          <span v-if="item.duration">{{ formatDuration(item.duration) }}</span>
          <span v-if="item.filename"> &middot; {{ fileName(item.filename) }}</span>
        </span>
      </div>
      <a
        v-if="item.filename"
        :href="downloadUrl(item)"
        class="btn-download"
        download
        @click.prevent="handleClick(item)"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M8 2v9m0 0L5 8m3 3 3-3M3 13h10"/>
        </svg>
      </a>
      <button class="btn-delete" @click="handleDelete(item)" title="Удалить">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
          <path d="M3 3l8 8M11 3l-8 8"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { downloadVideo, deleteTask } from '../api.js'

const emit = defineEmits(['download-started', 'download-deleted'])

defineProps({
  downloads: { type: Array, default: () => [] },
})

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

function fileName(path) {
  return path.split('/').pop()
}

function downloadUrl(item) {
  if (item.filename) return `/api/download/${encodeURIComponent(fileName(item.filename))}`
  if (item.url) return item.url
  return '#'
}

async function handleClick(item) {
  if (!item.url) return
  const url = downloadUrl(item)
  try {
    const res = await fetch(url, { method: 'HEAD' })
    if (res.ok) {
      const a = document.createElement('a')
      a.href = url
      a.download = ''
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      return
    }
  } catch {
    // file missing, re-download
  }
  try {
    const task = await downloadVideo(item.url, {
      mode: item.mode || 'video',
      quality: item.quality || 'best',
    })
    emit('download-started', task)
  } catch (e) {
    console.error('Re-download failed:', e)
  }
}

async function handleDelete(item) {
  if (!item.task_id) return
  try {
    await deleteTask(item.task_id)
    emit('download-deleted', item.task_id)
  } catch (e) {
    console.error('Delete failed:', e)
  }
}
</script>

<style scoped>
.download-list {
  margin-top: 3rem;
}

h2 {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
}

.item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 0.75rem;
  margin-bottom: 0.5rem;
  transition: all 150ms ease-out;
}

.item:hover {
  border-color: var(--accent-soft-border);
}

.thumb {
  width: 112px;
  height: 64px;
  object-fit: cover;
  border-radius: 0.5rem;
  flex-shrink: 0;
}

.info {
  flex: 1;
  min-width: 0;
}

.title {
  display: block;
  font-weight: 500;
  font-size: 0.9375rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary);
}

.meta {
  display: block;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.btn-download {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-soft-bg);
  color: var(--accent-hover);
  text-decoration: none;
  border-radius: 0.5rem;
  flex-shrink: 0;
  transition: all 150ms ease-out;
}

.btn-download:hover {
  background: var(--accent);
  color: var(--bg-base);
}

.btn-delete {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--text-muted);
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 150ms ease-out;
}

.btn-delete:hover {
  background: #FEF2F2;
  color: #DC2626;
}
</style>
