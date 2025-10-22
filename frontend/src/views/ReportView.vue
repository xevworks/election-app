<template>
  <div class="container-narrow">
    <v-card class="pa-4 rounded-2xl" elevation="2">
      <h1 class="text-h6 mb-3">Laporkan Kecurangan</h1>
      <v-form @submit.prevent="submitReport">
        <v-text-field v-model="name" label="Nama" required />
        <v-text-field v-model="email" label="Email" type="email" required />
        <v-textarea v-model="message" label="Deskripsi Laporan" rows="5" auto-grow required />
        <v-btn type="submit" color="primary" :loading="loading" block>Kirim</v-btn>
      </v-form>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import http from '@/api/http'

const name = ref(''),
  email = ref(''),
  message = ref(''),
  loading = ref(false)

async function submitReport() {
  loading.value = true
  try {
    await http.post('/api/reports/', {
      name: name.value,
      email: email.value,
      message: message.value,
    })
    name.value = email.value = message.value = ''
    alert('Laporan terkirim. Terima kasih!')
  } catch {
    alert('Gagal mengirim laporan.')
  } finally {
    loading.value = false
  }
}
</script>
