<template>
  <div class="app">
    <header>
      <h1>Video Downloader</h1>
      <p>YouTube, VK, Rutube и другие</p>
    </header>

    <main>
      <DownloadForm @download-started="onDownloadStarted" />

      <div v-if="activeTasks.length" class="active-tasks">
        <h2>Скачивание</h2>
        <ProgressBar
          v-for="task in activeTasks"
          :key="task.task_id"
          :task="task"
          @completed="onTaskCompleted"
        />
      </div>

      <DownloadList :downloads="downloads" @download-started="onDownloadStarted" @download-deleted="onDownloadDeleted" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DownloadForm from './components/DownloadForm.vue'
import ProgressBar from './components/ProgressBar.vue'
import DownloadList from './components/DownloadList.vue'
import { getTaskStatus, getActiveTasks } from './api.js'

const activeTasks = ref([])
const downloads = ref([])

function onDownloadStarted(task) {
  const exists = activeTasks.value.some(t => t.task_id === task.task_id)
  if (!exists) {
    activeTasks.value.unshift(task)
  }
}

async function onTaskCompleted(task) {
  activeTasks.value = activeTasks.value.filter(t => t.task_id !== task.task_id)
  try {
    const status = await getTaskStatus(task.task_id)
    downloads.value.unshift(status)
    localStorage.setItem('downloads', JSON.stringify(downloads.value))
  } catch {}
}

function onDownloadDeleted(taskId) {
  downloads.value = downloads.value.filter(t => t.task_id !== taskId)
  localStorage.setItem('downloads', JSON.stringify(downloads.value))
}

onMounted(async () => {
  const saved = localStorage.getItem('downloads')
  if (saved) downloads.value = JSON.parse(saved)

  try {
    const active = await getActiveTasks()
    activeTasks.value = active
  } catch {}
})
</script>

<style>
:root {
  --bg-base: #FFFFFF;
  --bg-subtle: #FAFAFA;
  --bg-card: #FFFFFF;
  --text-primary: #09090B;
  --text-secondary: #6B7280;
  --text-muted: #9CA3AF;
  --border-subtle: #E5E7EB;
  --border-hover: #D1D5DB;
  --accent: #38BDF8;
  --accent-hover: #0284C7;
  --accent-soft-bg: #F0F9FF;
  --accent-soft-border: #E0F2FE;
  --accent-focus: rgba(56, 189, 248, 0.3);
  --shadow-elevation: 0 1px 3px rgba(0, 0, 0, 0.04);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;
  background: var(--bg-subtle);
  color: var(--text-primary);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

.app {
  max-width: 720px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
}

header {
  text-align: center;
  margin-bottom: 3rem;
}

header h1 {
  font-size: 1.875rem;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: var(--text-primary);
}

header p {
  color: var(--text-secondary);
  margin-top: 0.5rem;
  font-size: 0.9375rem;
}

@media (min-width: 640px) {
  .app {
    padding: 4rem 2rem;
  }

  header h1 {
    font-size: 2.25rem;
  }
}

.active-tasks {
  margin-bottom: 2rem;
}

.active-tasks h2 {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
}
</style>
