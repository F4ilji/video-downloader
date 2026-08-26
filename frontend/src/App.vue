<template>
  <div class="app">
    <header>
      <h1>Video Downloader</h1>
      <p>YouTube, VK, Rutube и другие</p>
    </header>

    <main>
      <Transition name="morph" mode="out-in">
        <DownloadForm
          v-if="!currentTask"
          key="form"
          @download-started="onDownloadStarted"
        />
        <ProgressBar
          v-else
          key="progress"
          :task="currentTask"
          @completed="onCompleted"
        />
      </Transition>

      <DownloadList :downloads="downloads" @download-started="onDownloadStarted" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DownloadForm from './components/DownloadForm.vue'
import ProgressBar from './components/ProgressBar.vue'
import DownloadList from './components/DownloadList.vue'
import { getTaskStatus } from './api.js'

const currentTask = ref(null)
const downloads = ref([])

function onDownloadStarted(task) {
  currentTask.value = task
}

async function onCompleted(task) {
  const status = await getTaskStatus(task.task_id)
  downloads.value.unshift(status)
  currentTask.value = null
  localStorage.setItem('downloads', JSON.stringify(downloads.value))
}

onMounted(() => {
  const saved = localStorage.getItem('downloads')
  if (saved) downloads.value = JSON.parse(saved)
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

.morph-enter-active,
.morph-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.morph-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}

.morph-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}
</style>
