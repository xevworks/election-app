<template>
  <v-dialog v-model="dialog" max-width="800" scrollable>
    <v-card v-if="candidate">
      <v-card-title class="d-flex align-center justify-space-between pa-4">
        <span class="text-h5">Detail Kandidat</span>
        <v-btn icon variant="text" @click="dialog = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-0">
        <!-- Poster Image -->
        <v-img :src="candidate.poster_url || fallbackPoster" height="400" cover />

        <div class="pa-6">
          <!-- Name -->
          <h2 class="text-h4 mb-2">{{ candidate.name }}</h2>

          <!-- Institution -->
          <div class="d-flex align-center mb-4">
            <v-icon color="primary" class="mr-2">mdi-school</v-icon>
            <span class="text-h6 text-medium-emphasis">
              {{ candidate.institution || 'Institusi tidak tersedia' }}
            </span>
          </div>

          <v-divider class="my-4" />

          <!-- Vision & Mission (Markdown) -->
          <div v-if="candidate.vision" class="vision-content">
            <h3 class="text-h6 mb-3">Visi & Misi</h3>
            <div class="markdown-content" v-html="renderedVision"></div>
          </div>
          <div v-else class="text-medium-emphasis">
            Visi & misi belum tersedia.
          </div>
        </div>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn color="primary" variant="text" @click="dialog = false">
          Tutup
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  modelValue: Boolean,
  candidate: Object,
})

const emit = defineEmits(['update:modelValue'])

const fallbackPoster = 'https://via.placeholder.com/600x400?text=Poster+Kandidat'

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

// Configure marked options
marked.setOptions({
  breaks: true,
  gfm: true,
})

const renderedVision = computed(() => {
  if (!props.candidate?.vision) return ''
  return marked(props.candidate.vision)
})
</script>

<style scoped>
.vision-content {
  line-height: 1.8;
}

/* Markdown styling */
.markdown-content {
  font-size: 1rem;
  line-height: 1.8;
  color: rgba(0, 0, 0, 0.87);
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
}

.markdown-content :deep(h1) {
  font-size: 1.75rem;
}

.markdown-content :deep(h2) {
  font-size: 1.5rem;
}

.markdown-content :deep(h3) {
  font-size: 1.25rem;
}

.markdown-content :deep(p) {
  margin-bottom: 1em;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin-bottom: 1em;
  padding-left: 2em;
}

.markdown-content :deep(li) {
  margin-bottom: 0.5em;
}

.markdown-content :deep(strong) {
  font-weight: 600;
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #e0e0e0;
  padding-left: 1em;
  margin: 1em 0;
  color: rgba(0, 0, 0, 0.6);
}

.markdown-content :deep(code) {
  background-color: #f5f5f5;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background-color: #f5f5f5;
  padding: 1em;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1em 0;
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
}

.markdown-content :deep(a) {
  color: #1976d2;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid #e0e0e0;
  margin: 2em 0;
}
</style>
