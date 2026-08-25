<template>
  <div class="progress-bar">
    <div class="header">
      <span class="title">{{ title }}</span>
      <span class="status" :class="status">{{ statusText }}</span>
    </div>

    <div class="bar">
      <div class="fill" :style="{ width: percent + '%' }"></div>
    </div>

    <div class="info">
      <span>{{ percent }}%</span>
      <span v-if="speed">{{ speed }}</span>
      <span v-if="eta">ETA: {{ eta }}</span>
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

const percent = ref(0)
const speed = ref('')
const eta = ref('')
const status = ref('pending')
const filename = ref('')
const error = ref('')
const title = ref(props.task.url)
const evtSource = ref(null)

const statusText = computed(() => {
  const map = {
    pending: 'Ожидание...',
    downloading: 'Загрузка...',
    completed: 'Готово',
    failed: 'Ошибка',
  }
  return map[status.value] || status.value
})

const downloadUrl = computed(() => {
  if (!filename.value) return ''
  const name = filename.value.split('/').pop()
  return `/api/download/${encodeURIComponent(name)}`
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
  background: #1a1a1a;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.title {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70%;
}

.status {
  font-size: 0.875rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  background: #333;
}

.status.downloading {
  background: #1e40af;
}

.status.completed {
  background: #16a34a;
}

.status.failed {
  background: #dc2626;
}

.bar {
  height: 8px;
  background: #333;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s;
  border-radius: 4px;
}

.info {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #888;
}

.download-link {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #16a34a;
  color: #fff;
  text-decoration: none;
  border-radius: 8px;
  font-size: 0.875rem;
}

.download-link:hover {
  background: #15803d;
}

.error {
  margin-top: 0.75rem;
  color: #ef4444;
  font-size: 0.875rem;
}
</style>
