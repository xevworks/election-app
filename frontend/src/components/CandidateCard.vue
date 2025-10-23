<template>
  <v-card class="rounded-2xl candidate-card" elevation="2" @click="$emit('click')">
    <v-img :src="posterUrl" height="400" cover class="rounded-t-2xl" />
    <v-card-title class="text-h6 pt-3">{{ name }}</v-card-title>
    <v-card-subtitle class="pb-3">
      {{ institution || 'Institusi tidak tersedia' }}
    </v-card-subtitle>
  </v-card>
</template>

<script setup>
defineProps({ 
  name: String, 
  institution: String, 
  posterUrl: String 
})

defineEmits(['click'])
</script>

<style scoped>
.candidate-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.candidate-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15) !important;
}
</style>
