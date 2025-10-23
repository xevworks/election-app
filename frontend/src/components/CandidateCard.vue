<template>
  <v-card class="rounded-2xl" elevation="2">
    <v-img :src="posterUrl" height="400" cover class="rounded-t-2xl" />
    <v-card-title class="text-h6 pt-3">{{ name }}</v-card-title>
    <v-card-subtitle 
      class="pb-1 cursor-pointer" 
      :class="{ 'line-clamp-2': !expanded && program.length > 80 }"
      @click="toggleExpand"
    >
      {{ program }}
    </v-card-subtitle>
    <v-btn 
      v-if="program.length > 80"
      variant="text" 
      size="x-small" 
      color="primary"
      @click="toggleExpand"
      class="mt-n2 mb-2"
    >
      {{ expanded ? 'Sembunyikan' : 'Selengkapnya' }}
      <v-icon size="small" class="ml-1">
        {{ expanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
      </v-icon>
    </v-btn>
    <v-card-text class="text-body-2"><slot /></v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'

defineProps({ name: String, program: String, posterUrl: String })

const expanded = ref(false)

const toggleExpand = () => {
  expanded.value = !expanded.value
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5rem;
}

.cursor-pointer {
  cursor: pointer;
  user-select: none;
}

.cursor-pointer:hover {
  opacity: 0.8;
}
</style>
