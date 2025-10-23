<template>
  <div class="container-narrow">
    <v-sheet class="pa-2">
      <!-- Loading Skeleton -->
      <div v-if="loading">
        <!-- Header Skeleton -->
        <v-skeleton-loader type="heading" class="mb-2" />
        <v-skeleton-loader type="text" class="mb-1" width="200" />
        <v-skeleton-loader type="text" class="mb-4" width="150" />

        <!-- Candidates Skeleton -->
        <v-skeleton-loader type="heading" class="mb-2" />
        <v-row dense>
          <v-col v-for="i in 2" :key="i" cols="12" sm="6">
            <v-card class="rounded-2xl" elevation="2">
              <v-skeleton-loader type="image" height="400" />
              <v-skeleton-loader type="list-item-two-line" class="px-4" />
            </v-card>
          </v-col>
        </v-row>

        <v-divider class="my-6" />

        <!-- Results Skeleton -->
        <v-skeleton-loader type="heading" class="mb-2" />
        <v-skeleton-loader type="image" height="300" />
      </div>

      <!-- Actual Content -->
      <div v-else>
        <!-- Error State -->
        <v-alert v-if="error" type="error" class="mb-4">
          {{ error }}
        </v-alert>

        <!-- Empty State -->
        <v-alert v-else-if="!active" type="info" class="mb-4">
          Belum ada election yang tersedia saat ini.
        </v-alert>

        <!-- Content -->
        <template v-else>
          <h1 class="text-h5 font-weight-bold mb-2">
            Pemilihan Calon Ketua PPI Osaka-Nara {{ active?.year ? active.year + '/' + (active.year + 1) : '-' }}
          </h1>
          <div class="text-body-2 mb-4">
            Periode voting: <strong>{{ period }}</strong>
            <div v-if="active?.is_open" class="text-success font-weight-bold">
              ✓ Status: Voting Sedang Dibuka
            </div>
            <div v-else class="text-error font-weight-bold">
              ✗ Status: Voting Ditutup
            </div>
          </div>

          <h2 class="text-subtitle-1 mb-2">Kandidat Calon Ketua PPI Osaka-Nara</h2>
          <v-row dense>
            <v-col v-for="c in candidates" :key="c.id" cols="12" sm="6">
              <CandidateCard :name="c.name" :program="c.vision || '—'" :poster-url="c.poster_url || fallbackPoster" />
            </v-col>
          </v-row>

          <v-divider class="my-6" />

          <h2 class="text-subtitle-1 mb-2">Hasil Voting (jika dirilis KPU)</h2>
          <div v-if="active?.show_results && results?.length">
            <ResultsBarChart :data="results" />
          </div>
          <div v-else class="text-body-2 text-medium-emphasis">
            Hasil belum dirilis.
          </div>
        </template>
      </div>
    </v-sheet>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import http from '@/api/http'
import CandidateCard from '@/components/CandidateCard.vue'
import ResultsBarChart from '@/components/ResultsBarChart.vue'

const active = ref(null)
const candidates = ref([])
const results = ref([])
const loading = ref(true)
const error = ref(null)
const fallbackPoster = 'https://via.placeholder.com/600x400?text=Poster+Kandidat'

const period = computed(() =>
  active.value ? `${active.value.start_date} s/d ${active.value.end_date}` : '—',
)

onMounted(async () => {
  loading.value = true
  error.value = null
  
  try {
    // Changed from /active/ to /latest/ to get latest election regardless of date
    const { data } = await http.get('/api/elections/latest/')
    active.value = data

    const { data: cds } = await http.get('/api/candidates/', { params: { election: data.id } })
    candidates.value = cds

    if (data.show_results) {
      const { data: res } = await http.get('/api/results/', { params: { election: data.id } })
      results.value = res
    }
  } catch (err) {
    console.error('Error loading election data:', err)
    
    if (err.response?.status === 404) {
      error.value = 'Belum ada election yang tersedia saat ini.'
    } else {
      error.value = 'Gagal memuat data election. Silakan refresh halaman.'
    }
  } finally {
    loading.value = false
  }
})
</script>
