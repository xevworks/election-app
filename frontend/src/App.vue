<template>
  <v-app>
    <v-app-bar density="comfortable" elevation="1">
      <v-app-bar-title>KPU | PPI Osaka-Nara</v-app-bar-title>
      <v-spacer />
      <v-btn variant="text" :to="{ name: 'home' }">Beranda</v-btn>
      <v-btn variant="text" :to="{ name: 'vote' }">Vote</v-btn>
      <v-btn variant="text" :to="{ name: 'report' }">Laporkan</v-btn>
      <v-btn variant="text" :to="{ name: 'admin' }">Admin</v-btn>
    </v-app-bar>

    <v-main><router-view /></v-main>

    <v-footer app class="pa-4">
      <div class="text-caption mx-auto">© KPU {{ new Date().getFullYear() }} | PPI Osaka-Nara</div>
    </v-footer>
  </v-app>
</template>
