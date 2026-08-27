<template>
  <div class="progress-bar">
    <div class="progress-left">
      <div class="circle">
        <svg viewBox="0 0 44 44">
          <circle class="track" cx="22" cy="22" :r="RADIUS" :stroke-dasharray="circumference" />
          <circle
            class="fill"
            cx="22"
            cy="22"
            :r="RADIUS"
            :stroke-dasharray="circumference"
            :style="{ strokeDashoffset: dashOffset }"
          />
        </svg>
        <span class="percent">{{ percent }}%</span>
      </div>
      <div class="details">
        <span class="title">{{ title }}</span>
        <div class="meta">
          <span class="status" :class="status">{{ statusText }}</span>
          <span v-if="speed" class="speed">{{ speed }}</span>
          <span v-if="eta" class="eta">Осталось ~{{ eta }}</span>
        </div>
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

const RADIUS = 18
const circumference = 2 * Math.PI * RADIUS

const percent = ref(0)
const speed = ref('')
const eta = ref('')
const status = ref('pending')
const filename = ref('')
const error = ref('')
const title = ref(props.task.url)
const evtSource = ref(null)

const dashOffset = computed(() => {
  const progress = percent.value / 100
  return circumference - progress * circumference
})

const statusText = computed(() => {
  const map = {
    pending: 'Ожидание',
    downloading: 'Загрузка',
    completed: 'Готово',
    failed: 'Ошибка',
  }
  return map[status.value] || status.value
})

const downloadUrl = computed(() => {
  if (!filename.value) return ''
  const apiKey = import.meta.env.VITE_API_KEY || ''
  const name = filename.value.split('/').pop()
  const base = `/api/download/${encodeURIComponent(name)}`
  return apiKey ? `${base}?api_key=${encodeURIComponent(apiKey)}` : base
})

onMounted(async () => {
  try {
    const info = await getTaskStatus(props.task.task_id)
    title.value = info.title || info.url
    status.value = info.status
    percent.value = info.progress || 0

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
      (data) => {
        status.value = data.status
        percent.value = parseFloat(data.percent) || 0
        speed.value = data.speed
        eta.value = data.eta
        filename.value = data.filename
        error.value = data.error

        if (data.status === 'completed' || data.status === 'failed') {
          emit('completed', props.task)
        }

        if (data.status === 'completed' && data.filename) {
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
      },
      () => {}
    )
  } catch (e) {
    error.value = e.message
  }
})

onUnmounted(() => {
  if (evtSource.value) evtSource.value.close()
})
</script>

<style scoped>
.progress-bar {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 0.75rem;
  padding: 1.25rem;
  margin-bottom: 1rem;
  transition: all 150ms ease-out;
}

.progress-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.circle {
  position: relative;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
}

.circle svg {
  transform: rotate(-90deg);
  width: 44px;
  height: 44px;
}

.circle .track {
  fill: none;
  stroke: var(--bg-subtle);
  stroke-width: 3;
}

.circle .fill {
  fill: none;
  stroke: var(--accent);
  stroke-width: 3;
  stroke-linecap: round;
  transition: stroke-dashoffset 300ms ease-out;
}

.percent {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.5625rem;
  font-weight: 500;
  color: var(--text-primary);
}

.details {
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
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.25rem;
}

.status {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  background: var(--bg-subtle);
  color: var(--text-secondary);
}

.status.downloading {
  background: var(--accent-soft-bg);
  color: var(--accent-hover);
}

.status.completed {
  background: #F0FDF4;
  color: #16A34A;
}

.status.failed {
  background: #FEF2F2;
  color: #DC2626;
}

.speed,
.eta {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.download-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: var(--accent-soft-bg);
  color: var(--accent-hover);
  text-decoration: none;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  transition: all 150ms ease-out;
}

.download-link:hover {
  background: var(--accent);
  color: var(--bg-base);
}

.error {
  margin-top: 0.75rem;
  color: #DC2626;
  font-size: 0.8125rem;
}
</style>
