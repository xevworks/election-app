<template>
  <div class="container-narrow">
    <v-card class="pa-6 rounded-2xl text-center" elevation="2">
      <h1 class="text-h5 mb-2">Anda sudah memilih ✅</h1>
      <p class="text-body-2">
        Terima kasih, suara Anda sudah tercatat pada election ini.
        <template v-if="votedFor">
          Anda memilih: <strong>{{ votedFor }}</strong
          >.
        </template>
      </p>
      <div class="mt-4">
        <v-btn color="primary" :to="{ name: 'home' }">Kembali ke Beranda</v-btn>
      </div>
    </v-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const votedFor = ref(null)

onMounted(() => {
  try {
    const s = JSON.parse(sessionStorage.getItem('votedInfo') || 'null')
    votedFor.value = s?.votedFor || null
  } catch {}
})
</script>
