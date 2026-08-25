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
  margin-bottom: 2.5rem;
}

form {
  display: flex;
  gap: 0.75rem;
}

input[type="url"] {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-subtle);
  border-radius: 0.75rem;
  background: var(--bg-base);
  color: var(--text-primary);
  font-size: 0.9375rem;
  font-family: inherit;
  transition: all 150ms ease-out;
}

input[type="url"]:hover {
  border-color: var(--border-hover);
}

input[type="url"]:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-focus);
}

input[type="url"]::placeholder {
  color: var(--text-muted);
}

.error {
  margin-top: 0.75rem;
  color: #DC2626;
  font-size: 0.8125rem;
}

.preview {
  margin-top: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 0.75rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 150ms ease-out;
}

.preview:hover {
  border-color: var(--accent-soft-border);
}

.preview-thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 0.5rem;
}

.preview-body {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.preview-title {
  font-weight: 500;
  font-size: 0.9375rem;
  color: var(--text-primary);
  line-height: 1.4;
}

.preview-duration {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-primary);
  cursor: pointer;
}

.checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
  cursor: pointer;
}

.quality-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.select-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
}

.select-wrapper {
  flex: 1;
}

.select-wrapper select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-subtle);
  border-radius: 0.5rem;
  background: var(--bg-base);
  color: var(--text-primary);
  font-size: 0.875rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 150ms ease-out;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L5 5L9 1' stroke='%236B7280' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  padding-right: 2rem;
}

.select-wrapper select:hover {
  border-color: var(--border-hover);
}

.select-wrapper select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-focus);
}

.btn-download {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 0.75rem;
  background: var(--text-primary);
  color: var(--bg-base);
  font-size: 0.9375rem;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 150ms ease-out;
}

.btn-download:hover:not(:disabled) {
  background: #27272A;
}

.btn-download:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

@keyframes shimmer {
  0% { background-position: -200% 0 }
  100% { background-position: 200% 0 }
}

.skeleton > * {
  border-radius: 0.5rem;
  background: linear-gradient(90deg, var(--border-subtle) 25%, #f0f0f0 50%, var(--border-subtle) 75%);
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
  gap: 0.5rem;
}

.skeleton-line {
  height: 14px;
  border-radius: 4px;
}

.skeleton-line.wide { width: 80% }
.skeleton-line.narrow { width: 40% }
.skeleton-line.short { width: 60px }
.skeleton-line.tiny { width: 50px }

.skeleton-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.skeleton-check {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.skeleton-select {
  flex: 1;
  height: 36px;
  border-radius: 0.5rem;
}

.skeleton-btn {
  width: 100%;
  height: 44px;
  border-radius: 0.75rem;
}
</style>
