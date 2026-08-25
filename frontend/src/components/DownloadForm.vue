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
        <span v-else>Далее</span>
      </button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="showSettings" class="modal-overlay" @click.self="showSettings = false">
      <div class="modal">
        <h3>Настройки скачивания</h3>

        <div class="option-group">
          <label>Что скачать</label>
          <div class="radio-group">
            <label class="radio">
              <input type="radio" v-model="mode" value="video" />
              <span>Видео</span>
            </label>
            <label class="radio">
              <input type="radio" v-model="mode" value="audio" />
              <span>Только аудио</span>
            </label>
          </div>
        </div>

        <div v-if="mode === 'video'" class="option-group">
          <label>Качество</label>
          <div class="radio-group">
            <label class="radio">
              <input type="radio" v-model="quality" value="best" />
              <span>Лучшее</span>
            </label>
            <label class="radio">
              <input type="radio" v-model="quality" value="high" />
              <span>1080p</span>
            </label>
            <label class="radio">
              <input type="radio" v-model="quality" value="medium" />
              <span>720p</span>
            </label>
            <label class="radio">
              <input type="radio" v-model="quality" value="low" />
              <span>480p</span>
            </label>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-cancel" @click="showSettings = false">Отмена</button>
          <button class="btn-download" @click="startDownload" :disabled="loading">
            {{ loading ? 'Скачивание...' : 'Скачать' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { downloadVideo } from '../api.js'

const emit = defineEmits(['download-started'])

const url = ref('')
const loading = ref(false)
const error = ref('')
const showSettings = ref(false)
const mode = ref('video')
const quality = ref('best')

function handleSubmit() {
  if (!url.value) return
  error.value = ''
  showSettings.value = true
}

async function startDownload() {
  if (!url.value) return
  loading.value = true
  error.value = ''

  try {
    const task = await downloadVideo(url.value, {
      mode: mode.value,
      quality: quality.value,
    })
    emit('download-started', task)
    url.value = ''
    showSettings.value = false
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

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: #1a1a1a;
  border-radius: 16px;
  padding: 2rem;
  width: 90%;
  max-width: 400px;
  border: 1px solid #333;
}

.modal h3 {
  margin: 0 0 1.5rem;
  font-size: 1.25rem;
  color: #fff;
}

.option-group {
  margin-bottom: 1.25rem;
}

.option-group label {
  display: block;
  font-size: 0.875rem;
  color: #888;
  margin-bottom: 0.5rem;
}

.radio-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.radio {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  background: #262626;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 0.9rem;
}

.radio:hover {
  background: #333;
}

.radio input[type="radio"] {
  display: none;
}

.radio:has(input:checked) {
  background: #667eea;
  color: #fff;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-cancel {
  flex: 1;
  padding: 0.75rem;
  background: #333;
  color: #fff;
  border-radius: 10px;
}

.btn-cancel:hover {
  background: #444;
}

.btn-download {
  flex: 1;
  padding: 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
