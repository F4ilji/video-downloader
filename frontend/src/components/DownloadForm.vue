<template>
  <div class="download-form">
    <form @submit.prevent>
      <input
        v-model="url"
        type="url"
        placeholder="Вставьте URL видео..."
        :disabled="loading"
        required
      />
    </form>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="loading && !videoInfo" class="preview skeleton">
      <div class="skeleton-thumb"></div>
      <div class="skeleton-body">
        <div class="skeleton-line wide"></div>
        <div class="skeleton-line narrow"></div>
      </div>
      <div class="skeleton-row">
        <div class="skeleton-check"></div>
        <div class="skeleton-line short"></div>
      </div>
      <div class="skeleton-row">
        <div class="skeleton-line tiny"></div>
        <div class="skeleton-select"></div>
      </div>
      <div class="skeleton-btn"></div>
    </div>

    <div v-if="videoInfo" class="preview">
      <img v-if="videoInfo.thumbnail" :src="videoInfo.thumbnail" class="preview-thumb" />
      <div class="preview-body">
        <span class="preview-title">{{ videoInfo.title }}</span>
        <span v-if="videoInfo.duration" class="preview-duration">{{ formatDuration(videoInfo.duration) }}</span>
      </div>

      <label class="checkbox">
        <input type="checkbox" v-model="audioOnly" />
        <span>Только аудио</span>
      </label>

      <div v-if="!audioOnly" class="quality-row">
        <label class="select-label">Качество</label>
        <div class="select-wrapper">
          <select v-model="quality">
            <option value="best">Лучшее</option>
            <option value="high">1080p</option>
            <option value="medium">720p</option>
            <option value="low">480p</option>
          </select>
        </div>
      </div>

      <button
        class="btn-download"
        :class="{ loading }"
        @click="startDownload"
        :disabled="loading"
      >
        {{ loading ? 'Скачивание...' : 'Скачать' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getVideoInfo, downloadVideo } from '../api.js'

const emit = defineEmits(['download-started'])

const url = ref('')
const loading = ref(false)
const error = ref('')
const videoInfo = ref(null)
const audioOnly = ref(false)
const quality = ref('best')
let checkTimeout = null

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

async function handleCheck() {
  if (!url.value) return
  error.value = ''
  videoInfo.value = null
  loading.value = true

  try {
    videoInfo.value = await getVideoInfo(url.value)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

watch(url, (val) => {
  if (checkTimeout) clearTimeout(checkTimeout)
  if (!val) {
    videoInfo.value = null
    return
  }
  checkTimeout = setTimeout(handleCheck, 600)
})

async function startDownload() {
  if (!url.value) return
  loading.value = true
  error.value = ''

  try {
    const task = await downloadVideo(url.value, {
      mode: audioOnly.value ? 'audio' : 'video',
      quality: quality.value,
    })
    emit('download-started', task)
    url.value = ''
    videoInfo.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.download-form {
  margin-bottom: var(--space-xl);
}

form {
  display: flex;
  gap: var(--space-sm);
}

input[type="url"] {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-input);
  color: var(--text-main);
  font: var(--p-sm);
  font-family: inherit;
  transition: border-color 150ms ease-out, box-shadow 150ms ease-out;
}

input[type="url"]:hover {
  border-color: var(--border-hover);
}

input[type="url"]:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px var(--blue-focus);
}

input[type="url"]::placeholder {
  color: var(--text-muted);
}

input[type="url"].warning {
  border-color: var(--yellow-warn);
}

input[type="url"].warning:focus {
  box-shadow: 0 0 0 3px var(--yellow-focus);
}

.error {
  margin-top: var(--space-sm);
  color: var(--red-alert);
  font: var(--p-xs);
}

.preview {
  margin-top: var(--space-md);
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  box-shadow: var(--shadow-card);
  transition: border-color 150ms ease-out;
}

.preview:hover {
  border-color: var(--blue-soft-border);
}

.preview-thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: var(--radius-sm);
}

.preview-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.preview-title {
  font-weight: 500;
  font: var(--p-sm);
  color: var(--text-main);
  line-height: 1.4;
}

.preview-duration {
  font: var(--p-xs);
  color: var(--text-sub);
}

.checkbox {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font: var(--p-sm);
  color: var(--text-main);
  cursor: pointer;
}

.checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--blue-info);
  cursor: pointer;
}

.quality-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.select-label {
  font: var(--p-xs);
  font-weight: 500;
  color: var(--text-sub);
  white-space: nowrap;
}

.select-wrapper {
  flex: 1;
}

.select-wrapper select {
  width: 100%;
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-input);
  color: var(--text-main);
  font: var(--p-sm);
  font-family: inherit;
  cursor: pointer;
  transition: border-color 150ms ease-out, box-shadow 150ms ease-out;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L5 5L9 1' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right var(--space-sm) center;
  padding-right: var(--space-lg);
}

.select-wrapper select:hover {
  border-color: var(--border-hover);
}

.select-wrapper select:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px var(--blue-focus);
}

.btn-download {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  border: none;
  border-radius: var(--radius-md);
  background: var(--blue-info);
  color: hsl(0, 0%, 100%);
  font: var(--p-sm);
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: background 150ms ease-out, transform 100ms ease-out, opacity 150ms ease-out;
}

.btn-download:hover:not(:disabled) {
  filter: brightness(0.9);
}

.btn-download:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-download:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-download.loading {
  position: relative;
  color: transparent;
  pointer-events: none;
}

.btn-download.loading::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid hsla(0, 0%, 100%, 0.3);
  border-top-color: hsl(0, 0%, 100%);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0 }
  100% { background-position: 200% 0 }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.skeleton > * {
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--border) 25%, var(--bg-hover) 50%, var(--border) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

.skeleton-thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
}

.skeleton-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.skeleton-line {
  height: 14px;
  border-radius: var(--space-xs);
}

.skeleton-line.wide { width: 80% }
.skeleton-line.narrow { width: 40% }
.skeleton-line.short { width: 60px }
.skeleton-line.tiny { width: 50px }

.skeleton-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.skeleton-check {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.skeleton-select {
  flex: 1;
  height: 36px;
  border-radius: var(--radius-sm);
}

.skeleton-btn {
  width: 100%;
  height: 44px;
  border-radius: var(--radius-md);
}
</style>
