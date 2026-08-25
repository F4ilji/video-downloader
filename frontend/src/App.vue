<template>
  <div class="app">
    <header>
      <h1>Video Downloader</h1>
      <p>YouTube, VK, Rutube и другие</p>
    </header>

    <main>
      <DownloadForm @download-started="onDownloadStarted" />

      <ProgressBar
        v-if="currentTask"
        :task="currentTask"
        @completed="onCompleted"
      />

      <DownloadList :downloads="downloads" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DownloadForm from './components/DownloadForm.vue'
import ProgressBar from './components/ProgressBar.vue'
import DownloadList from './components/DownloadList.vue'
import { getTaskStatus, listDownloads } from './api.js'

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

onMounted(async () => {
  try {
    downloads.value = await listDownloads()
  } catch {
    const saved = localStorage.getItem('downloads')
    if (saved) downloads.value = JSON.parse(saved)
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #0f0f0f;
  color: #fff;
  min-height: 100vh;
}

.app {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

header {
  text-align: center;
  margin-bottom: 2rem;
}

header h1 {
  font-size: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

header p {
  color: #888;
  margin-top: 0.5rem;
}
</style>
