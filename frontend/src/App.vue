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

    <footer class="theme-toggle">
      <span class="toggle-label">☀️</span>
      <button
        class="toggle-track"
        :class="{ active: isDark }"
        @click="toggleTheme"
        role="switch"
        :aria-checked="isDark"
        aria-label="Переключить тему"
      >
        <span class="toggle-thumb" />
      </button>
      <span class="toggle-label">🌙</span>
    </footer>
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
const isDark = ref(false)

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

function initTheme() {
  const saved = localStorage.getItem('theme')
  if (saved) {
    isDark.value = saved === 'dark'
  } else {
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  document.documentElement.classList.toggle('dark', isDark.value)
}

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
    downloads.value = downloads.value.filter(t => t.url !== status.url)
    downloads.value.unshift(status)
    localStorage.setItem('downloads', JSON.stringify(downloads.value))
  } catch {}
}

function onDownloadDeleted(taskId) {
  downloads.value = downloads.value.filter(t => t.task_id !== taskId)
  localStorage.setItem('downloads', JSON.stringify(downloads.value))
}

onMounted(async () => {
  initTheme()

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
  --ff: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;

  --display: bold 1.5rem/1.15em var(--ff);
  --h1: bold 1.5rem/1.2em var(--ff);
  --h2: bold 1.25rem/1.3em var(--ff);
  --h3: 600 1.125rem/1.3em var(--ff);
  --p: 1rem/1.4em var(--ff);
  --p-sm: 0.875rem/1.4em var(--ff);
  --p-xs: 0.75rem/1.4em var(--ff);

  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 40px;

  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 16px;

  --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.05), 0 4px 16px rgba(0, 0, 0, 0.08);
  --shadow-dropdown: 0 4px 24px rgba(0, 0, 0, 0.1), 0 8px 32px rgba(0, 0, 0, 0.08);

  --bg-page: hsl(220, 15%, 97%);
  --bg-card: hsl(0, 0%, 100%);
  --bg-elevated: hsl(0, 0%, 100%);
  --bg-input: hsl(0, 0%, 100%);
  --bg-hover: hsl(220, 15%, 96%);

  --text-main: hsl(220, 15%, 10%);
  --text-sub: hsl(220, 10%, 45%);
  --text-muted: hsl(220, 10%, 65%);

  --border: hsl(220, 15%, 90%);
  --border-hover: hsl(220, 15%, 80%);
  --border-focus: hsl(215, 90%, 60%);

  --blue-info: hsl(215, 90%, 60%);
  --blue-soft-bg: hsl(215, 90%, 96%);
  --blue-soft-border: hsl(215, 80%, 90%);
  --blue-focus: hsla(215, 90%, 60%, 0.25);

  --green-ok: hsl(145, 70%, 45%);
  --green-soft-bg: hsl(145, 70%, 95%);

  --red-alert: hsl(355, 80%, 55%);
  --red-soft-bg: hsl(355, 80%, 96%);

  --yellow-warn: hsl(40, 95%, 50%);
  --yellow-soft-bg: hsl(40, 95%, 95%);
  --yellow-focus: hsla(40, 95%, 50%, 0.25);
}

.dark {
  --bg-page: hsl(220, 15%, 4%);
  --bg-card: hsl(220, 15%, 10%);
  --bg-elevated: hsl(220, 15%, 14%);
  --bg-input: hsl(220, 15%, 12%);
  --bg-hover: hsl(220, 15%, 16%);

  --text-main: hsl(0, 0%, 100%);
  --text-sub: hsl(0, 0%, 65%);
  --text-muted: hsl(0, 0%, 45%);

  --border: hsl(0, 0%, 20%);
  --border-hover: hsl(0, 0%, 28%);
  --border-focus: hsl(215, 90%, 55%);

  --blue-info: hsl(215, 90%, 65%);
  --blue-soft-bg: hsla(215, 90%, 65%, 0.12);
  --blue-soft-border: hsla(215, 90%, 65%, 0.2);
  --blue-focus: hsla(215, 90%, 65%, 0.3);

  --green-ok: hsl(145, 70%, 55%);
  --green-soft-bg: hsla(145, 70%, 55%, 0.12);

  --red-alert: hsl(355, 80%, 60%);
  --red-soft-bg: hsla(355, 80%, 60%, 0.12);

  --yellow-warn: hsl(40, 95%, 55%);
  --yellow-soft-bg: hsla(40, 95%, 55%, 0.12);
  --yellow-focus: hsla(40, 95%, 55%, 0.3);

  --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.2), 0 4px 16px rgba(0, 0, 0, 0.15);
  --shadow-dropdown: 0 4px 24px rgba(0, 0, 0, 0.25), 0 8px 32px rgba(0, 0, 0, 0.18);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--ff);
  background: var(--bg-page);
  color: var(--text-main);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

.app {
  max-width: 720px;
  margin: 0 auto;
  padding: var(--space-xl) var(--space-md);
}

header {
  text-align: center;
  margin-bottom: var(--space-2xl);
}

header h1 {
  font: var(--h1);
  letter-spacing: -0.02em;
  color: var(--text-main);
}

header p {
  color: var(--text-sub);
  margin-top: var(--space-xs);
  font: var(--p-sm);
}

@media (min-width: 640px) {
  .app {
    padding: var(--space-2xl) var(--space-lg);
  }

  header h1 {
    font: var(--display);
    letter-spacing: -0.025em;
  }
}

.active-tasks {
  margin-bottom: var(--space-lg);
}

.active-tasks h2 {
  font: var(--p-xs);
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-md);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  margin-top: var(--space-2xl);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--border);
}

.toggle-label {
  font-size: 16px;
  line-height: 1;
  opacity: 0.6;
}

.toggle-track {
  position: relative;
  width: 44px;
  height: 24px;
  background: var(--border);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: background 200ms ease;
  padding: 0;
}

.toggle-track.active {
  background: var(--blue-info);
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: hsl(0, 0%, 100%);
  border-radius: 50%;
  transition: transform 200ms ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}

.toggle-track.active .toggle-thumb {
  transform: translateX(20px);
}

.toggle-track:hover {
  opacity: 0.9;
}

.toggle-track:active .toggle-thumb {
  width: 24px;
}

.toggle-track.active:active .toggle-thumb {
  transform: translateX(16px);
}
</style>
