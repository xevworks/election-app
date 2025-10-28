<template>
  <div class="container-narrow">
    <v-sheet class="pa-2">
      <!-- Loading Skeleton -->
      <div v-if="loading">
        <v-skeleton-loader type="heading" class="mb-2" />
        <v-skeleton-loader type="text" class="mb-1" width="200" />
        <v-skeleton-loader type="text" class="mb-4" width="150" />

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
          <v-card class="mb-4 rounded-lg" elevation="1" color="blue-grey-lighten-5">
            <v-card-text>
              <div class="text-subtitle-2 font-weight-bold mb-2">
                <v-icon class="mr-2">mdi-calendar-clock</v-icon>
                Periode Voting
              </div>
              <div class="text-body-2 mb-3" style="line-height: 1.6;">
                {{ period }}
              </div>
              <v-chip v-if="active?.is_open" color="success" variant="elevated" prepend-icon="mdi-check-circle"
                size="small">
                Voting Sedang Dibuka
              </v-chip>
              <v-chip v-else color="error" variant="elevated" prepend-icon="mdi-close-circle" size="small">
                Voting Ditutup
              </v-chip>
            </v-card-text>
          </v-card>

          <!-- View PDF Section -->
          <v-card class="mb-4 rounded-lg" elevation="1" color="blue-lighten-5">
            <v-card-text class="d-flex align-center justify-space-between flex-wrap">
              <div class="d-flex align-center">
                <v-icon color="primary" size="large" class="mr-3">mdi-file-pdf-box</v-icon>
                <div>
                  <div class="text-subtitle-1 font-weight-medium">Panduan Pemilih</div>
                  <div class="text-caption text-medium-emphasis">
                    Baca panduan lengkap untuk voter
                  </div>
                </div>
              </div>
              <v-btn color="primary" variant="elevated" prepend-icon="mdi-open-in-new" @click="openPDF"
                class="mt-2 mt-sm-0">
                Buka Panduan
              </v-btn>
            </v-card-text>
          </v-card>

          <h2 class="text-subtitle-1 mb-2">Kandidat Calon Ketua PPI Osaka-Nara</h2>
          <p class="text-body-2 text-medium-emphasis mb-3">
            Klik kartu kandidat untuk melihat detail visi & misi lengkap
          </p>
          <v-row dense>
            <v-col v-for="c in candidates" :key="c.id" cols="12" sm="6">
              <CandidateCard :name="c.name" :institution="c.institution" :poster-url="c.poster_url || fallbackPoster"
                @click="openDetail(c)" />
            </v-col>
          </v-row>

          <v-divider class="my-6" />

          <!-- Results Section with Button to Show Overlay -->
          <div class="d-flex align-center justify-space-between mb-2">
            <h2 class="text-subtitle-1">Hasil Voting</h2>
            <v-btn v-if="active?.show_results && results?.length" color="amber-darken-1" variant="elevated"
              prepend-icon="mdi-trophy" @click="showResultsOverlay = true">
              Lihat Hasil Resmi
            </v-btn>
          </div>
        </template>
      </div>
    </v-sheet>

    <!-- Candidate Detail Dialog -->
    <CandidateDetailDialog v-model="detailDialog" :candidate="selectedCandidate" />

    <!-- Results Overlay -->
    <VotingResultsOverlay v-model="showResultsOverlay" :results="results" :candidates="candidates"
      :election-year="active?.year ? active.year + '/' + (active.year + 1) : '-'" />
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import http from '@/api/http'
import CandidateCard from '@/components/CandidateCard.vue'
import CandidateDetailDialog from '@/components/CandidateDetailDialog.vue'
import ResultsBarChart from '@/components/ResultsBarChart.vue'
import VotingResultsOverlay from '@/components/VotingResultsOverlay.vue'

const active = ref(null)
const candidates = ref([])
const results = ref([])
const loading = ref(true)
const error = ref(null)
const fallbackPoster = 'https://placecats.com/poppy/300/200'

const detailDialog = ref(false)
const selectedCandidate = ref(null)
const showResultsOverlay = ref(false)

const pdfUrl = 'https://election-ppion.muhammadalqaaf.com/api/user-manual/'

// Format datetime dengan lebih readable
function formatDateTime(dateTimeString) {
  if (!dateTimeString) return '-'
  
  const date = new Date(dateTimeString)
  
  // Options for formatting
  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Asia/Tokyo',
    hour12: false
  }
  
  const formatted = new Intl.DateTimeFormat('id-ID', options).format(date)
  return `${formatted} JST`
}

const period = computed(() => {
  if (!active.value?.start_date || !active.value?.end_date) return '—'
  
  const start = formatDateTime(active.value.start_date)
  const end = formatDateTime(active.value.end_date)
  
  return `${start} s/d ${end}`
})

function openDetail(candidate) {
  selectedCandidate.value = candidate
  detailDialog.value = true
}

function openPDF() {
  window.open(pdfUrl, '_blank', 'noopener,noreferrer')
}

onMounted(async () => {
  loading.value = true
  error.value = null

  try {
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
