<template>
  <div class="progress-bar" :class="status">
    <div class="progress-ring" :style="ringStyle" />
    <div class="progress-fill" />
    <div class="progress-content">
      <div class="details">
        <span class="title">{{ title }}</span>
        <div class="meta">
          <span class="status-badge" :class="status">{{ statusText }}</span>
          <span v-if="isActive" class="percent">{{ displayPercent.toFixed(1) }}%</span>
          <span v-if="speed" class="speed">{{ speed }}</span>
          <span v-if="eta" class="eta">Осталось ~{{ eta }}</span>
        </div>
      </div>

      <a
        v-if="status === 'completed' && filename"
        :href="downloadUrl"
        class="download-link"
        download
      >
        Скачать файл
      </a>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { streamProgress, getTaskStatus } from '../api.js'

const props = defineProps({
  task: { type: Object, required: true },
})

const emit = defineEmits(['completed'])

const LERP_FACTOR = 0.08

const targetPercent = ref(0)
const displayPercent = ref(0)
const speed = ref('')
const eta = ref('')
const status = ref('pending')
const filename = ref('')
const error = ref('')
const title = ref(props.task.url)
const evtSource = ref(null)
let rafId = null

const isActive = computed(() =>
  ['downloading', 'processing'].includes(status.value)
)

const statusText = computed(() => {
  const map = {
    pending: 'Ожидание',
    downloading: 'Загрузка',
    processing: 'Обработка',
    completed: 'Готово',
    failed: 'Ошибка',
  }
  return map[status.value] || status.value
})

const ringColor = computed(() => {
  if (status.value === 'completed') return 'var(--green-ok)'
  if (status.value === 'failed') return 'var(--red-alert)'
  return 'var(--blue-info)'
})

const ringStyle = computed(() => {
  if (isActive.value) {
    return { '--progress': `${Math.round(displayPercent.value * 3.6)}deg` }
  }
  if (status.value === 'completed' || status.value === 'failed') {
    return { '--progress': '360deg' }
  }
  return {}
})

const downloadUrl = computed(() => {
  if (!filename.value) return ''
  const apiKey = import.meta.env.VITE_API_KEY || ''
  const name = filename.value.split('/').pop()
  const base = `/api/download/${encodeURIComponent(name)}`
  return apiKey ? `${base}?api_key=${encodeURIComponent(apiKey)}` : base
})

function animate() {
  const diff = targetPercent.value - displayPercent.value
  if (Math.abs(diff) > 0.1) {
    displayPercent.value += diff * LERP_FACTOR
    rafId = requestAnimationFrame(animate)
  } else {
    displayPercent.value = targetPercent.value
  }
}

function startAnimation() {
  if (rafId) cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(animate)
}

function handleSseData(data) {
  const newStatus = data.status
  const newPercent = parseFloat(data.percent) || 0

  status.value = newStatus
  speed.value = data.speed
  eta.value = data.eta
  filename.value = data.filename
  error.value = data.error

  if (newStatus === 'downloading' || newStatus === 'processing') {
    if (newPercent >= targetPercent.value) {
      targetPercent.value = newPercent
    }
    startAnimation()
  }

  if (newStatus === 'completed' || newStatus === 'failed') {
    targetPercent.value = newStatus === 'completed' ? 100 : targetPercent.value
    displayPercent.value = targetPercent.value
    if (rafId) cancelAnimationFrame(rafId)
    emit('completed', props.task)
  }

  if (newStatus === 'completed' && data.filename) {
    const apiKey = import.meta.env.VITE_API_KEY || ''
    const name = data.filename.split('/').pop()
    const base = `/api/download/${encodeURIComponent(name)}`
    const url = apiKey ? `${base}?api_key=${encodeURIComponent(apiKey)}` : base
    const a = document.createElement('a')
    a.href = url
    a.download = ''
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }
}

onMounted(async () => {
  try {
    const info = await getTaskStatus(props.task.task_id)
    title.value = info.title || info.url
    status.value = info.status
    targetPercent.value = info.progress || 0
    displayPercent.value = targetPercent.value

    if (info.status === 'completed' || info.status === 'failed') {
      filename.value = info.filename
      error.value = info.error_message
      emit('completed', props.task)

      if (info.status === 'completed' && info.filename) {
        const name = info.filename.split('/').pop()
        const apiKey = import.meta.env.VITE_API_KEY || ''
        const base = `/api/download/${encodeURIComponent(name)}`
        const url = apiKey ? `${base}?api_key=${encodeURIComponent(apiKey)}` : base
        const a = document.createElement('a')
        a.href = url
        a.download = ''
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
      }
      return
    }

    evtSource.value = streamProgress(
      props.task.task_id,
      handleSseData,
      () => {}
    )
  } catch (e) {
    error.value = e.message
  }
})

onUnmounted(() => {
  if (rafId) cancelAnimationFrame(rafId)
  if (evtSource.value) evtSource.value.close()
})
</script>

<style scoped>
@property --progress {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}

.progress-bar {
  position: relative;
  border-radius: var(--radius-md);
  margin-bottom: var(--space-md);
}

.progress-ring {
  position: absolute;
  inset: 0;
  border-radius: var(--radius-md);
  background: conic-gradient(var(--blue-info) var(--progress), transparent var(--progress));
  transition: --progress 80ms linear;
}

.progress-fill {
  position: absolute;
  inset: 2px;
  border-radius: calc(var(--radius-md) - 2px);
  background: var(--bg-card);
}

.progress-content {
  position: relative;
  padding: var(--space-lg);
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.progress-bar:not(.downloading):not(.processing):not(.completed):not(.failed) .progress-ring {
  display: none;
}

.progress-bar.completed .progress-ring {
  background: conic-gradient(var(--green-ok) var(--progress), transparent var(--progress));
}

.progress-bar.processing .progress-ring {
  background: conic-gradient(var(--yellow-warn) var(--progress), transparent var(--progress));
}

.progress-bar.failed .progress-ring {
  background: conic-gradient(var(--red-alert) var(--progress), transparent var(--progress));
}

.progress-bar:not(.downloading):not(.processing):not(.completed):not(.failed) .progress-fill {
  display: none;
}

.progress-bar:not(.downloading):not(.processing):not(.completed):not(.failed) .progress-content {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
}

.details {
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
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-top: var(--space-xs);
}

.status-badge {
  font: var(--p-xs);
  font-weight: 500;
  padding: 2px var(--space-sm);
  border-radius: 9999px;
  background: var(--bg-hover);
  color: var(--text-sub);
}

.status-badge.downloading {
  background: var(--blue-soft-bg);
  color: var(--blue-info);
}

.status-badge.processing {
  background: var(--yellow-soft-bg);
  color: var(--yellow-warn);
}

.status-badge.completed {
  background: var(--green-soft-bg);
  color: var(--green-ok);
}

.status-badge.failed {
  background: var(--red-soft-bg);
  color: var(--red-alert);
}

.percent {
  font: var(--p-xs);
  font-weight: 600;
  color: var(--blue-info);
}

.speed,
.eta {
  font: var(--p-xs);
  color: var(--text-sub);
}

.download-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-md);
  background: var(--blue-soft-bg);
  color: var(--blue-info);
  text-decoration: none;
  border-radius: var(--radius-sm);
  font: var(--p-xs);
  font-weight: 500;
  flex-shrink: 0;
  transition: background 150ms ease-out, color 150ms ease-out;
}

.download-link:hover {
  background: var(--blue-info);
  color: hsl(0, 0%, 100%);
}

.error {
  margin-top: var(--space-sm);
  color: var(--red-alert);
  font: var(--p-xs);
}
</style>
