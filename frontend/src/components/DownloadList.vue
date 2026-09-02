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
      <button
        v-if="item.filename"
        class="btn-share"
        :class="{ disabled: fileExists[item.filename] === false }"
        :disabled="fileExists[item.filename] === false"
        @click="handleShare(item)"
        title="Поделиться"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="4" r="2"/><circle cx="4" cy="8" r="2"/><circle cx="12" cy="12" r="2"/>
          <path d="M6 7l4-2M6 9l4 2"/>
        </svg>
      </button>
      <button class="btn-delete" @click="handleDelete(item)" title="Удалить">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
          <path d="M3 3l8 8M11 3l-8 8"/>
        </svg>
      </button>
    </div>
    <div v-if="error" class="error-banner">
      <span class="error-banner-icon">⚠️</span>
      <span class="error-banner-text">{{ error }}</span>
      <button class="error-banner-close" @click="error = ''" aria-label="Закрыть">✕</button>
    </div>
    <div v-if="copied" class="toast">
      Ссылка скопирована
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { downloadVideo, deleteTask } from '../api.js'

const emit = defineEmits(['download-started', 'download-deleted'])

const props = defineProps({
  downloads: { type: Array, default: () => [] },
})

const error = ref('')
const copied = ref(false)
const fileExists = ref({})

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

function fileName(path) {
  return path.split('/').pop()
}

function downloadUrl(item) {
  const apiKey = import.meta.env.VITE_API_KEY || ''
  const name = fileName(item.filename)
  const base = `/api/download/${encodeURIComponent(name)}`
  return apiKey ? `${base}?api_key=${encodeURIComponent(apiKey)}` : base
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
    if (res.status === 404) {
      fileExists.value[item.filename] = false
      const action = confirm('Видео было удалено с сервера.\n\nСкачать заново или удалить запись из истории?')
      if (action) {
        try {
          const task = await downloadVideo(item.url, {
            mode: item.mode || 'video',
            quality: item.quality || 'best',
          })
          emit('download-started', task)
        } catch (e) {
          error.value = e.message || 'Не удалось начать повторное скачивание'
        }
      } else {
        await handleDelete(item)
      }
      return
    }
    error.value = `Ошибка сервера: ${res.status}`
    return
  } catch (e) {
    error.value = 'Не удалось проверить файл на сервере'
  }
}

async function handleDelete(item) {
  if (!item.task_id) return
  try {
    await deleteTask(item.task_id)
    emit('download-deleted', item.task_id)
  } catch (e) {
    error.value = e.message || 'Не удалось удалить задачу'
  }
}

async function handleShare(item) {
  if (!item.filename) return
  
  try {
    const res = await fetch(downloadUrl(item), { method: 'HEAD' })
    if (!res.ok) {
      fileExists.value[item.filename] = false
      error.value = 'Файл не найден на сервере'
      return
    }
  } catch {
    error.value = 'Не удалось проверить файл на сервере'
    return
  }
  
  try {
    await navigator.clipboard.writeText(downloadUrl(item))
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
  } catch {
    error.value = 'Не удалось скопировать ссылку'
  }
}

let checkTimeout = null

function scheduleCheckAllFiles() {
  if (checkTimeout) clearTimeout(checkTimeout)
  checkTimeout = setTimeout(checkAllFiles, 500)
}

async function checkFileExists(item) {
  if (!item.filename) return
  try {
    const res = await fetch(downloadUrl(item), { method: 'HEAD' })
    fileExists.value[item.filename] = res.ok
  } catch {
    fileExists.value[item.filename] = false
  }
}

async function checkAllFiles() {
  const promises = props.downloads.map(item => checkFileExists(item))
  await Promise.all(promises)
}

onMounted(checkAllFiles)

watch(() => props.downloads, scheduleCheckAllFiles, { deep: true })
</script>

<style scoped>
.download-list {
  margin-top: var(--space-xl);
}

h2 {
  font: var(--p-xs);
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-md);
}

.item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-sm);
  box-shadow: var(--shadow-card);
  transition: border-color 150ms ease-out;
}

.item:hover {
  border-color: var(--blue-soft-border);
}

.thumb {
  width: 112px;
  height: 64px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.info {
  flex: 1;
  min-width: 0;
}

.title {
  display: block;
  font-weight: 500;
  font: var(--p-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-main);
}

.meta {
  display: block;
  font: var(--p-xs);
  color: var(--text-sub);
  margin-top: var(--space-xs);
}

.btn-download {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--blue-soft-bg);
  color: var(--blue-info);
  text-decoration: none;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
  transition: background 150ms ease-out, color 150ms ease-out;
}

.btn-download:hover {
  background: var(--blue-info);
  color: hsl(0, 0%, 100%);
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
  border-radius: var(--radius-sm);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 150ms ease-out, color 150ms ease-out;
}

.btn-delete:hover {
  background: var(--red-soft-bg);
  color: var(--red-alert);
}

.btn-share {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--text-muted);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 150ms ease-out, color 150ms ease-out;
}

.btn-share:hover {
  background: var(--blue-soft-bg);
  color: var(--blue-info);
}

.btn-share.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-share.disabled:hover {
  background: transparent;
  color: var(--text-muted);
}

.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-card);
  color: var(--text-main);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-sm);
  font: var(--p-xs);
  z-index: 1000;
  animation: fadeInOut 2s ease-in-out;
}

@keyframes fadeInOut {
  0% { opacity: 0; transform: translateX(-50%) translateY(8px); }
  15% { opacity: 1; transform: translateX(-50%) translateY(0); }
  85% { opacity: 1; }
  100% { opacity: 0; }
}
</style>
