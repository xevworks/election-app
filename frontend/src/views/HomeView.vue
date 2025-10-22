<template>
  <div class="container-narrow">
    <v-sheet class="pa-2">
      <h1 class="text-h5 font-weight-bold mb-2">
        Pemilihan Calon Ketua PPI Osaka-Nara {{ active?.year || '-' }}
      </h1>
      <div class="text-body-2 mb-4">
        Periode voting: <strong>{{ period }}</strong>
        <div v-if="active?.is_open" class="text-success">Status: Sedang dibuka</div>
        <div v-else class="text-error">Status: Ditutup</div>
      </div>

      <h2 class="text-subtitle-1 mb-2">Kandidat Calon Ketua PPI Osaka-Nara</h2>
      <v-row dense>
        <v-col v-for="c in candidates" :key="c.id" cols="12" sm="6">
          <CandidateCard
            :name="c.name"
            :program="c.vision || '—'"
            :poster-url="c.poster_url || fallbackPoster"
          />
        </v-col>
      </v-row>

      <v-divider class="my-6" />

      <h2 class="text-subtitle-1 mb-2">Hasil Voting (jika dirilis KPU)</h2>
      <div v-if="active?.show_results && results?.length">
        <v-list density="compact" class="rounded-lg">
          <v-list-item v-for="r in results" :key="r.candidate_id">
            <v-list-item-title>{{ r.candidate_name }}</v-list-item-title>
            <v-list-item-subtitle>{{ r.votes }} suara</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </div>
      <div v-else class="text-body-2 text-medium-emphasis">Hasil belum dirilis.</div>
    </v-sheet>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import http from '@/api/http'
import CandidateCard from '@/components/CandidateCard.vue'

const active = ref(null)
const candidates = ref([])
const results = ref([])
const fallbackPoster = 'https://via.placeholder.com/600x400?text=Poster+Kandidat'

const period = computed(() =>
  active.value ? `${active.value.start_date} s/d ${active.value.end_date}` : '—',
)

onMounted(async () => {
  const { data } = await http.get('/api/elections/active/')
  active.value = data

  const { data: cds } = await http.get('/api/candidates/', { params: { election: data.id } })
  candidates.value = cds

  if (data.show_results) {
    const { data: res } = await http.get('/api/results/', { params: { election: data.id } })
    results.value = res
  }
})
</script>
