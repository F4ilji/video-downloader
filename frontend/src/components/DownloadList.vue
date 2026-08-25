<template>
  <div class="download-list" v-if="downloads.length">
    <h2>Скачанные видео</h2>
    <div v-for="item in downloads" :key="item.filename || item.task_id" class="item">
      <img v-if="item.thumbnail" :src="item.thumbnail" class="thumb" />
      <div class="info">
        <span class="title">{{ item.title || item.filename }}</span>
        <span class="meta">
          <span v-if="item.duration">{{ formatDuration(item.duration) }}</span>
          <span v-if="item.filename"> • {{ fileName(item.filename) }}</span>
        </span>
      </div>
      <a
        v-if="item.filename"
        :href="downloadUrl(item)"
        class="btn"
        download
      >
        ↓
      </a>
    </div>
  </div>
</template>

<script setup>
defineProps({
  downloads: { type: Array, default: () => [] },
})

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

function fileName(path) {
  return path.split('/').pop()
}

function downloadUrl(item) {
  if (item.url) return item.url
  return `/api/download/${encodeURIComponent(fileName(item.filename))}`
}
</script>

<style scoped>
.download-list {
  margin-top: 2rem;
}

h2 {
  font-size: 1.25rem;
  margin-bottom: 1rem;
  color: #ccc;
}

.item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #1a1a1a;
  border-radius: 12px;
  margin-bottom: 0.5rem;
}

.thumb {
  width: 120px;
  height: 68px;
  object-fit: cover;
  border-radius: 8px;
}

.info {
  flex: 1;
  min-width: 0;
}

.title {
  display: block;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta {
  display: block;
  font-size: 0.875rem;
  color: #888;
  margin-top: 0.25rem;
}

.btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #16a34a;
  color: #fff;
  text-decoration: none;
  border-radius: 8px;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.btn:hover {
  background: #15803d;
}
</style>
