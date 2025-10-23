<template>
  <v-app>
    <v-app-bar density="comfortable" elevation="1">
      <v-app-bar-title>
        <img src="https://osakanara.ppijepang.org/wp-content/uploads/sites/5/2023/12/Logo-2.svg" alt="PPI Osaka-Nara Logo" style="height: 40px; vertical-align: middle;" />
        KPU
      </v-app-bar-title>
      <v-spacer />
      <v-btn variant="text" :to="{ name: 'home' }">Beranda</v-btn>
      <v-btn variant="text" :to="{ name: 'vote' }">Vote</v-btn>
      <v-btn variant="text" :to="{ name: 'report' }">Laporkan</v-btn>
      <v-btn variant="text" :to="{ name: 'admin' }">Admin</v-btn>
    </v-app-bar>

    <v-main><router-view /></v-main>

    <v-footer app class="pa-4">
      <div class="text-caption mx-auto">© KPU {{ new Date().getFullYear() }} | PPI Osaka-Nara</div>
      <div class="text-caption mx-auto">Build with passion by xevworks</div>
    </v-footer>
  </v-app>
</template>
