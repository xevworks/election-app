<template>
  <div class="container-narrow">
    <v-card class="pa-6 rounded-2xl text-center" elevation="2">
      <h1 class="text-h5 mb-2">Terima kasih! 🎉</h1>
      <p class="text-body-2">
        Suara Anda sudah tercatat. Jika ada kendala atau kecurangan, silakan gunakan menu
        <strong>Laporkan</strong>.
      </p>
      <div class="mt-4">
        <v-btn color="primary" :to="{ name: 'home' }">Kembali ke Beranda</v-btn>
      </div>
    </v-card>
  </div>
</template>
