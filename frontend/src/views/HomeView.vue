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
          <div class="text-body-2 mb-4">
            Periode voting: <strong>{{ period }}</strong>
            <div v-if="active?.is_open" class="text-success font-weight-bold">
              ✓ Status: Voting Sedang Dibuka
            </div>
            <div v-else class="text-error font-weight-bold">
              ✗ Status: Voting Ditutup
            </div>
          </div>

          <!-- Download PDF Section -->
          <v-card class="mb-4 rounded-lg" elevation="1" color="blue-lighten-5">
            <v-card-text class="d-flex align-center justify-space-between flex-wrap">
              <div class="d-flex align-center">
                <v-icon color="primary" size="large" class="mr-3">mdi-file-pdf-box</v-icon>
                <div>
                  <div class="text-subtitle-1 font-weight-medium">Panduan Pemilih</div>
                  <div class="text-caption text-medium-emphasis">
                    Download panduan pemilihan
                  </div>
                </div>
              </div>
              <v-btn
                color="primary"
                variant="elevated"
                prepend-icon="mdi-download"
                :href="pdfUrl"
                target="_blank"
                class="mt-2 mt-sm-0"
              >
                Download PDF
              </v-btn>
            </v-card-text>
          </v-card>

          <h2 class="text-subtitle-1 mb-2">Kandidat Calon Ketua PPI Osaka-Nara</h2>
          <p class="text-body-2 text-medium-emphasis mb-3">
            Klik kartu kandidat untuk melihat detail visi & misi lengkap
          </p>
          <v-row dense>
            <v-col v-for="c in candidates" :key="c.id" cols="12" sm="6">
              <CandidateCard 
                :name="c.name" 
                :institution="c.institution"
                :poster-url="c.poster_url || fallbackPoster"
                @click="openDetail(c)"
              />
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

    <!-- Candidate Detail Dialog -->
    <CandidateDetailDialog 
      v-model="detailDialog" 
      :candidate="selectedCandidate"
    />
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import http from '@/api/http'
import CandidateCard from '@/components/CandidateCard.vue'
import CandidateDetailDialog from '@/components/CandidateDetailDialog.vue'
import ResultsBarChart from '@/components/ResultsBarChart.vue'

const active = ref(null)
const candidates = ref([])
const results = ref([])
const loading = ref(true)
const error = ref(null)
const fallbackPoster = 'https://via.placeholder.com/600x400?text=Poster+Kandidat'

const detailDialog = ref(false)
const selectedCandidate = ref(null)

const pdfUrl = ref('https://github.com/xevworks/election-app/releases/download/v1.0.0/user-manual.pdf')

const period = computed(() =>
  active.value ? `${active.value.start_date} s/d ${active.value.end_date}` : '—',
)

function openDetail(candidate) {
  selectedCandidate.value = candidate
  detailDialog.value = true
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
