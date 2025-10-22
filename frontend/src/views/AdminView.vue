<template>
  <div class="container-narrow">
    <v-card class="pa-4 rounded-2xl" elevation="2">
      <div class="d-flex align-center justify-space-between mb-2">
        <h1 class="text-h6">Admin (KPU)</h1>
        <v-btn v-if="hasKey" size="small" variant="tonal" @click="clearKey">Keluar</v-btn>
      </div>

      <!-- Admin Key -->
      <v-alert v-if="!hasKey" type="info" variant="tonal" class="mb-4">
        Masukkan <strong>Admin Key</strong> untuk mengelola election.
      </v-alert>
      <v-form v-if="!hasKey" @submit.prevent="saveKey" class="mb-4">
        <v-text-field v-model="adminKeyInput" label="Admin Key (X-Admin-Key)" required />
        <v-btn type="submit" color="primary" block>Simpan</v-btn>
      </v-form>

      <template v-else>
        <!-- Election Controls -->
        <h2 class="text-subtitle-1 mb-2">Election</h2>
        <v-row dense>
          <v-col cols="12" md="6">
            <v-text-field v-model.number="form.year" label="Tahun" type="number" />
          </v-col>
          <v-col cols="12" md="6" class="d-flex align-center">
            <v-switch v-model="form.is_open" inset label="Voting dibuka?" />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field v-model="form.start_date" label="Mulai (YYYY-MM-DD)" placeholder="2025-10-01" />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field v-model="form.end_date" label="Berakhir (YYYY-MM-DD)" placeholder="2025-10-15" />
          </v-col>
          <v-col cols="12" md="6">
            <v-switch v-model="form.show_results" inset label="Tampilkan hasil di beranda?" />
          </v-col>
        </v-row>
        <div class="d-flex gap-2">
          <v-btn :loading="saving" color="primary" class="mr-2" @click="saveElection">Simpan Perubahan</v-btn>
          <v-btn variant="tonal" @click="createElection">Buat Election Baru</v-btn>
        </div>

        <v-divider class="my-6" />

        <!-- Candidate Manager -->
        <h2 class="text-subtitle-1 mb-2">Kandidat</h2>
        <v-form @submit.prevent="addCandidate" class="mb-3">
          <v-row dense>
            <v-col cols="12" md="4"><v-text-field v-model="newCand.name" label="Nama kandidat" required /></v-col>
            <v-col cols="12" md="4"><v-text-field v-model="newCand.vision" label="Visi (singkat)" /></v-col>
            <v-col cols="12" md="4"><v-text-field v-model="newCand.poster_url" label="Poster URL (gambar)" /></v-col>
          </v-row>
          <v-btn type="submit" color="primary" :loading="adding">Tambah Kandidat</v-btn>
        </v-form>

        <v-list density="compact" class="rounded-lg">
          <v-list-item v-for="c in candidates" :key="c.id">
            <template #prepend>
              <v-avatar size="48">
                <v-img :src="c.poster_url || fallbackPoster" />
              </v-avatar>
            </template>
            <v-list-item-title>{{ c.name }}</v-list-item-title>
            <v-list-item-subtitle class="text-truncate">{{ c.vision || '—' }}</v-list-item-subtitle>
            <template #append>
              <v-btn icon size="small" variant="text" @click="editCandidate(c)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon size="small" variant="text" color="error" @click="removeCandidate(c.id)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
          </v-list-item>
        </v-list>

        <v-divider class="my-6" />

        <h2 class="text-subtitle-1 mb-2">Import Voter via CSV</h2>
        <v-row dense class="mb-3">
          <v-col cols="12" md="6">
            <v-file-input v-model="csvFile" accept=".csv,text/csv" label="Pilih file CSV"
              prepend-icon="mdi-file-delimited" />
          </v-col>
          <v-col cols="12" md="6">
            <v-switch v-model="importOverwrite" label="Overwrite token jika email sudah ada?" inset />
          </v-col>
        </v-row>
        <v-btn :disabled="!csvFile || !form.id" color="primary" :loading="importing" @click="doImportCsv">
          Import CSV (Generate Token)
        </v-btn>

        <div v-if="importResult" class="mt-4">
          <v-alert type="info" variant="tonal" class="mb-2">Hasil Import</v-alert>
          <v-table density="compact">
            <tbody>
              <tr>
                <td>Election ID</td>
                <td>{{ importResult.election }}</td>
              </tr>
              <tr>
                <td>Dibuat baru</td>
                <td>{{ importResult.created }}</td>
              </tr>
              <tr>
                <td>Diupdate (overwrite)</td>
                <td>{{ importResult.updated }}</td>
              </tr>
              <tr>
                <td>Invalid</td>
                <td>{{ importResult.skipped_invalid }}</td>
              </tr>
              <tr>
                <td>Duplicate (skip)</td>
                <td>{{ importResult.skipped_duplicate }}</td>
              </tr>
              <tr v-if="importResult.emails_attempted !== undefined">
                <td>Email attempted</td>
                <td>{{ importResult.emails_attempted }}</td>
              </tr>
              <tr v-if="importResult.emails_sent !== undefined">
                <td>Email sent</td>
                <td>{{ importResult.emails_sent }}</td>
              </tr>
              <tr v-if="importResult.email_error">
                <td>Email error</td>
                <td class="text-error">{{ importResult.email_error }}</td>
              </tr>
            </tbody>
          </v-table>
        </div>

        <v-divider class="my-6" />

        <h2 class="text-subtitle-1 mb-2">Kirim Token ke Email Voter</h2>
        <!-- Ringkasan status pengiriman token -->
        <v-skeleton-loader v-if="statsLoading" type="heading, text@2" class="mb-3" />
        <v-alert v-else type="info" variant="tonal" class="mb-3">
          <div class="d-flex flex-wrap align-center justify-space-between">
            <div>
              <div><strong>Voter terdaftar:</strong> {{ stats.total }}</div>
              <div><strong>Belum terkirim:</strong> {{ stats.pending }}</div>
              <div><strong>Sudah terkirim:</strong> {{ stats.sent }}</div>
              <div><strong>Sudah memilih:</strong> {{ stats.used }}</div>
              <div v-if="stats.last_sent_at" class="text-caption mt-1">
                Terakhir kirim: {{ new Date(stats.last_sent_at).toLocaleString() }}
              </div>
            </div>
            <div class="mt-2 mt-sm-0">
              <v-btn color="primary" :loading="sending" :disabled="(!resendAll && stats.pending === 0) || !form.id"
                @click="sendTokens">
                Kirim Token
              </v-btn>
              <v-switch v-model="resendAll" label="Kirim ulang ke SEMUA" inset class="mt-2" />
            </div>
          </div>
        </v-alert>

        <div v-if="sendResult" class="mt-4">
          <v-alert type="info" variant="tonal" class="mb-2">Ringkasan Pengiriman</v-alert>
          <v-table density="compact">
            <tbody>
              <tr>
                <td>Election ID</td>
                <td>{{ sendResult.election }}</td>
              </tr>
              <tr>
                <td>Attempted</td>
                <td>{{ sendResult.attempted }}</td>
              </tr>
              <tr>
                <td>Sent</td>
                <td>{{ sendResult.sent }}</td>
              </tr>
              <tr>
                <td>Failed</td>
                <td>{{ sendResult.failed }}</td>
              </tr>
              <tr v-if="sendResult.resend_all">
                <td>Mode</td>
                <td>Resend All</td>
              </tr>
            </tbody>
          </v-table>
          <div v-if="sendResult.failed_list?.length" class="text-caption mt-2">
            Gagal kirim ke (maks 50 ditampilkan): {{ sendResult.failed_list.join(', ') }}
          </div>
        </div>

        <!-- Dialog edit kandidat -->
        <v-dialog v-model="editDialog" max-width="520">
          <v-card class="pa-3">
            <h3 class="text-subtitle-1 mb-3">Edit Kandidat</h3>
            <v-text-field v-model="editCand.name" label="Nama" />
            <v-text-field v-model="editCand.vision" label="Visi" />
            <v-text-field v-model="editCand.poster_url" label="Poster URL" />
            <div class="d-flex justify-end mt-3">
              <v-btn variant="text" class="mr-2" @click="editDialog = false">Batal</v-btn>
              <v-btn color="primary" :loading="updating" @click="updateCandidate">Simpan</v-btn>
            </div>
          </v-card>
        </v-dialog>
      </template>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import http from '@/api/http'

const hasKey = ref(!!localStorage.getItem('adminKey'))
const adminKeyInput = ref('')
const fallbackPoster = 'https://via.placeholder.com/120x120?text=Poster'

const saving = ref(false)
const adding = ref(false)
const updating = ref(false)
const csvFile = ref(null)
const importOverwrite = ref(false)
const importing = ref(false)
const importResult = ref(null)

const resendAll = ref(false)
const sending = ref(false)
const sendResult = ref(null)

const stats = ref({ total: 0, pending: 0, sent: 0, used: 0, last_sent_at: null })
const statsLoading = ref(false)

const form = reactive({
  id: null,
  year: null,
  start_date: '',
  end_date: '',
  is_open: false,
  show_results: false,
})

const candidates = ref([])

function saveKey() {
  localStorage.setItem('adminKey', adminKeyInput.value.trim())
  hasKey.value = true
  fetchData()
}
function clearKey() {
  localStorage.removeItem('adminKey')
  hasKey.value = false
}

async function fetchStats() {
  if (!form.id) return
  statsLoading.value = true
  try {
    const { data } = await http.get('/api/admin/voters/stats/', { params: { election_id: form.id } })
    stats.value = data
  } catch (e) {
    // optional: silent
  } finally {
    statsLoading.value = false
  }
}

async function sendTokens() {
  if (!form.id) return
  sending.value = true
  sendResult.value = null
  try {
    const { data } = await http.post('/api/admin/voters/send-tokens/', {
      election_id: form.id,
      resend_all: resendAll.value
    })
    sendResult.value = data
    await fetchStats()
    alert('Proses kirim selesai.')
  } catch (e) {
    const msg = e?.response?.data ? JSON.stringify(e.response.data) : e.message
    alert('Gagal mengirim token. Detail: ' + msg)
  } finally {
    sending.value = false
  }
}

async function doImportCsv() {
  if (!form.id || !csvFile.value) return
  importing.value = true
  importResult.value = null
  try {
    const fd = new FormData()
    fd.append('file', csvFile.value)
    fd.append('election_id', String(form.id))
    fd.append('overwrite', String(importOverwrite.value))

    const { data } = await http.post('/api/admin/voters/import/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    importResult.value = data
    await fetchStats()
    alert('Import selesai. Token sudah dibuat/diupdate.')
  } catch (e) {
    const msg = e?.response?.data ? JSON.stringify(e.response.data) : e.message
    alert('Gagal import CSV. Detail: ' + msg)
  } finally {
    importing.value = false
  }
}

async function fetchData() {
  try {
    // coba get active; kalau 404, biarkan form kosong
    const { data: active } = await http.get('/api/admin/election/active/')
    form.id = active.id
    form.year = active.year
    form.start_date = active.start_date
    form.end_date = active.end_date
    form.is_open = active.is_open
    form.show_results = active.show_results

    const { data: cds } = await http.get('/api/candidates/', { params: { election: active.id } })
    candidates.value = cds
    await fetchStats()
  } catch (e) {
    // tidak ada active election atau unauthorized
    if (e.response?.status === 401) {
      alert('Admin key tidak valid.')
      clearKey()
    } else if (e.response?.status === 404) {
      // Tidak ada election aktif, kosongkan form
      form.id = null
      form.year = new Date().getFullYear()
      form.start_date = ''
      form.end_date = ''
      form.is_open = false
      form.show_results = false
      candidates.value = []
    } else {
      console.error('Error fetching data:', e)
    }
  }
}

async function saveElection() {
  saving.value = true
  try {
    const payload = {
      year: form.year,
      start_date: form.start_date,
      end_date: form.end_date,
      is_open: form.is_open,
      show_results: form.show_results,
    }

    const config = form.id ? { params: { id: form.id } } : {}
    const { data } = await http.put('/api/admin/election/active/', payload, config)

    form.id = data.id
    form.year = data.year
    form.start_date = data.start_date
    form.end_date = data.end_date
    form.is_open = data.is_open
    form.show_results = data.show_results

    alert('Perubahan election disimpan.')
  } catch (e) {
    console.error('Save election error:', e.response?.data || e.message)
    alert(`Gagal menyimpan election: ${e.response?.data?.detail || e.message}`)
  } finally {
    saving.value = false
  }
}

async function createElection() {
  try {
    const { data } = await http.post('/api/admin/elections/', {
      year: form.year,
      start_date: form.start_date,
      end_date: form.end_date,
      is_open: false,
      show_results: false,
    })
    form.id = data.id
    form.year = data.year
    form.start_date = data.start_date
    form.end_date = data.end_date
    form.is_open = data.is_open
    form.show_results = data.show_results
    alert('Election baru dibuat.')
  } catch (e) {
    alert('Gagal membuat election.')
  }
}

const newCand = reactive({ name: '', vision: '', poster_url: '' })
async function addCandidate() {
  if (!form.id) return alert('Buat/isi election dulu.')
  adding.value = true
  try {
    const { data } = await http.post('/api/admin/candidates/', {
      election: form.id,
      name: newCand.name,
      vision: newCand.vision,
      poster_url: newCand.poster_url,
    })
    candidates.value.unshift(data)
    newCand.name = newCand.vision = newCand.poster_url = ''
  } catch (e) {
    alert('Gagal menambah kandidat.')
  } finally {
    adding.value = false
  }
}

function editCandidate(c) {
  editCand.id = c.id
  editCand.name = c.name
  editCand.vision = c.vision
  editCand.poster_url = c.poster_url
  editDialog.value = true
}

async function removeCandidate(id) {
  if (!confirm('Hapus kandidat ini?')) return
  try {
    await http.delete(`/api/admin/candidates/${id}/`)
    candidates.value = candidates.value.filter((x) => x.id !== id)
  } catch (e) {
    alert('Gagal menghapus kandidat.')
  }
}

const editDialog = ref(false)
const editCand = reactive({ id: null, name: '', vision: '', poster_url: '' })
async function updateCandidate() {
  updating.value = true
  try {
    const { data } = await http.patch(`/api/admin/candidates/${editCand.id}/`, {
      name: editCand.name,
      vision: editCand.vision,
      poster_url: editCand.poster_url,
    })
    const idx = candidates.value.findIndex((x) => x.id === editCand.id)
    if (idx !== -1) candidates.value[idx] = data
    editDialog.value = false
  } catch (e) {
    alert('Gagal mengupdate kandidat.')
  } finally {
    updating.value = false
  }
}

onMounted(() => {
  if (hasKey.value) fetchData()
})
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}

.text-truncate {
  max-width: 380px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
