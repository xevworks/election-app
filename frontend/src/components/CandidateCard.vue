<template>
  <v-card class="rounded-2xl" elevation="2">
    <v-img :src="posterUrl" height="200" cover class="rounded-t-2xl" />
    <v-card-title class="text-h6 pt-3">{{ name }}</v-card-title>
    <v-card-subtitle class="pb-1">{{ program }}</v-card-subtitle>
    <v-card-text class="text-body-2"><slot /></v-card-text>
  </v-card>
</template>

<script setup>
defineProps({ name: String, program: String, posterUrl: String })
</script>
