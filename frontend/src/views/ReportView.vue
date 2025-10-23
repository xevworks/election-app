<template>
  <div class="container-narrow">
    <v-card class="pa-4 rounded-2xl" elevation="2">
      <h1 class="text-h6 mb-3">Laporkan Kecurangan</h1>

      <v-alert
        v-if="success"
        type="success"
        variant="tonal"
        class="mb-3"
        title="Terima kasih"
        text="Laporan Anda telah kami terima."
      />

      <v-form ref="formRef" v-model="valid" @submit.prevent="submitReport">
        <v-text-field
          v-model="name"
          label="Nama"
          :rules="[v => !!v || 'Wajib diisi']"
          required
        />
        <v-text-field
          v-model="email"
          label="Email"
          type="email"
          :rules="[v => !!v || 'Wajib diisi', v => /.+@.+\..+/.test(v) || 'Email tidak valid']"
          required
        />
        <v-textarea
          v-model="message"
          label="Deskripsi Laporan"
          rows="5"
          auto-grow
          :rules="[v => !!v || 'Wajib diisi', v => v?.length >= 20 || 'Minimal 20 karakter']"
          required
        />

        <!-- honeypot sederhana anti-bot -->
        <input v-model="hp" type="text" autocomplete="off" tabindex="-1"
               style="position:absolute;left:-9999px;opacity:0" aria-hidden="true" />

        <v-btn
          type="submit"
          color="primary"
          :loading="loading"
          :disabled="!valid || loading"
          block
        >
          Kirim
        </v-btn>
      </v-form>

      <v-snackbar v-model="snack.show" :timeout="3000">
        {{ snack.text }}
      </v-snackbar>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import http from '@/api/http'

const formRef = ref(null)
const valid = ref(false)
const name = ref('')
const email = ref('')
const message = ref('')
const loading = ref(false)
const success = ref(false)
const snack = ref({ show: false, text: '' })
const hp = ref('') // honeypot

async function submitReport() {
  if (hp.value) return // bot terperangkap, abaikan
  const ok = await formRef.value.validate()
  if (!ok.valid) return
  loading.value = true
  try {
    await http.post('/api/reports/', { name: name.value, email: email.value, message: message.value })
    success.value = true
    name.value = email.value = message.value = ''
    snack.value = { show: true, text: 'Laporan terkirim.' }
  } catch (e) {
    snack.value = { show: true, text: 'Gagal mengirim laporan. Coba lagi.' }
  } finally {
    loading.value = false
  }
}
</script>
