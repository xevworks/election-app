<template>
  <v-card class="rounded-2xl" elevation="2">
    <v-img :src="posterUrl" height="400" cover class="rounded-t-2xl" />
    <v-card-title class="text-h6 pt-3">{{ name }}</v-card-title>
    <v-card-subtitle 
      class="pb-1 cursor-pointer" 
      :class="{ 'line-clamp-2': !expanded }"
      @click="expanded = !expanded"
    >
      {{ program }}
      <v-icon v-if="program.length > 80" size="small" class="ml-1">
        {{ expanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
      </v-icon>
    </v-card-subtitle>
    <v-card-text class="text-body-2"><slot /></v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'

defineProps({ name: String, program: String, posterUrl: String })

const expanded = ref(false)
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cursor-pointer {
  cursor: pointer;
}

.cursor-pointer:hover {
  opacity: 0.8;
}
</style>
