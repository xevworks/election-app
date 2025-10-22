<template>
  <div class="container-narrow">
    <v-card class="pa-4 rounded-2xl" elevation="2">
      <h1 class="text-h6 mb-3">Masuk & Vote</h1>

      <!-- STEP 1: Login dengan email+token -->
      <v-alert v-if="notice" type="info" variant="tonal" class="mb-3">{{ notice }}</v-alert>
      <v-form @submit.prevent="handleLogin" v-if="!isAuthenticated">
        <v-text-field v-model="email" label="Email terdaftar" type="email" required />
        <v-text-field v-model="token" label="Token unik" required />
        <v-btn type="submit" :loading="loading" color="primary" class="mt-2" block>Masuk</v-btn>
        <div class="text-caption mt-2">* Token dikirim via email oleh KPU.</div>
      </v-form>

      <!-- STEP 2: Pilih kandidat -->
      <template v-else>
        <v-skeleton-loader v-if="loadingCandidates" type="list-item-two-line" class="mb-3" />
        <div v-else>
          <div class="mb-2 text-body-2">Pilih salah satu kandidat:</div>
          <v-radio-group v-model="selectedCandidate">
            <template v-for="c in candidates" :key="c.id">
              <v-card class="mb-2 rounded-xl" variant="tonal">
                <v-card-text class="d-flex align-center">
                  <v-avatar size="56" class="mr-3">
                    <v-img :src="c.poster_url || fallbackPoster" />
                  </v-avatar>
                  <div class="flex-grow-1">
                    <div class="text-subtitle-2">{{ c.name }}</div>
                    <div class="text-caption">{{ c.vision || '—' }}</div>
                  </div>
                  <v-radio :value="c.id" />
                </v-card-text>
              </v-card>
            </template>
          </v-radio-group>
          <v-btn
            color="primary"
            :disabled="!selectedCandidate || submitting"
            :loading="submitting"
            @click="submitVote"
            block
          >
            Kirim Vote
          </v-btn>
        </div>
      </template>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import http from '@/api/http'
import { useRouter } from 'vue-router'

const router = useRouter()

const email = ref('')
const token = ref('')
const loading = ref(false)
const isAuthenticated = ref(false)
const loadingCandidates = ref(false)
const candidates = ref([])
const selectedCandidate = ref(null)
const submitting = ref(false)
const fallbackPoster = 'https://via.placeholder.com/120x120?text=Poster'
const notice = ref('')

function getNameById(id) {
  const c = candidates.value.find(x => x.id === id)
  return c ? c.name : null
}

// STEP 1: Login
async function handleLogin() {
  loading.value = true
  notice.value = ''
  try {
    const { data } = await http.post('/api/auth/token-login/', {
      email: email.value,
      token: token.value,
    })
    isAuthenticated.value = true
    sessionStorage.setItem(
      'voteSession',
      JSON.stringify({
        email: email.value,
        token: token.value,
        electionId: data?.election_id || null,
      }),
    )

    // load kandidat
    loadingCandidates.value = true
    const { data: cds } = await http.get('/api/candidates/', {
      params: { election: data.election_id },
    })
    candidates.value = cds
  } catch (e) {
    const code = e?.response?.data?.code
    if (code === 'ELECTION_CLOSED') {
      notice.value = 'Voting sudah ditutup.'
    } else if (code === 'ALREADY_VOTED') {
      // simpan info agar halaman "Sudah Memilih" bisa menampilkan kandidat
      try {
        const votedFor = e?.response?.data?.voted_for || null
        const electionId = e?.response?.data?.election_id || null
        sessionStorage.setItem(
          'votedInfo',
          JSON.stringify({ hasVoted: true, electionId, votedFor }),
        )
      } catch {}
      router.replace({ name: 'alreadyvoted' })
      return
    } else if (code === 'INVALID_CREDENTIALS') {
      notice.value = 'Email/token tidak valid.'
    } else {
      notice.value = e?.response?.data?.detail || 'Email/token tidak valid.'
    }
  } finally {
    loading.value = false
    loadingCandidates.value = false
  }
}

// STEP 2: Submit vote
async function submitVote() {
  const sess = JSON.parse(sessionStorage.getItem('voteSession') || 'null')
  if (!sess) return
  submitting.value = true
  try {
    await http.post('/api/vote/', {
      candidate_id: selectedCandidate.value,
      email: sess.email,
      token: sess.token,
    })
    sessionStorage.setItem(
      'votedInfo',
      JSON.stringify({
        hasVoted: true,
        electionId: sess.electionId,
        votedFor: getNameById(selectedCandidate.value),
      }),
    )
    sessionStorage.removeItem('voteSession')
    router.replace({ name: 'thankyou' })
  } catch (e) {
    const code = e?.response?.data?.code
    if (code === 'ALREADY_VOTED') {
      sessionStorage.setItem(
        'votedInfo',
        JSON.stringify({ hasVoted: true, electionId: sess.electionId }),
      )
      router.replace({ name: 'thankyou' })
    } else if (code === 'ELECTION_CLOSED') {
      alert('Voting ditutup.')
      router.replace({ name: 'home' })
    } else {
      alert('Gagal mengirim vote. Silakan coba lagi.')
    }
  } finally {
    submitting.value = false
  }
}
</script>
