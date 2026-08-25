<template>
  <div class="download-form">
    <form @submit.prevent="handleSubmit">
      <input
        v-model="url"
        type="url"
        placeholder="Вставьте URL видео..."
        :disabled="loading"
        required
      />
      <button type="submit" :disabled="loading || !url">
        <span v-if="loading">Загрузка...</span>
        <span v-else>Скачать</span>
      </button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { downloadVideo } from '../api.js'

const emit = defineEmits(['download-started'])

const url = ref('')
const loading = ref(false)
const error = ref('')

async function handleSubmit() {
  if (!url.value) return
  loading.value = true
  error.value = ''

  try {
    const task = await downloadVideo(url.value)
    emit('download-started', task)
    url.value = ''
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.download-form {
  margin-bottom: 2rem;
}

form {
  display: flex;
  gap: 0.5rem;
}

input {
  flex: 1;
  padding: 1rem 1.5rem;
  border: 2px solid #333;
  border-radius: 12px;
  background: #1a1a1a;
  color: #fff;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

input::placeholder {
  color: #666;
}

button {
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

button:hover:not(:disabled) {
  opacity: 0.9;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  margin-top: 0.75rem;
  color: #ef4444;
  font-size: 0.875rem;
}
</style>
