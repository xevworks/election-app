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
        <v-text-field 
          v-model="adminKeyInput" 
          label="Masukkan admin key" 
          :type="showPassword ? 'text' : 'password'"
          :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
          @click:append-inner="showPassword = !showPassword"
          required 
        />
        <v-btn type="submit" color="primary" block>Masuk</v-btn>
      </v-form>

      <template v-else>
        <!-- Election Controls -->
        <h2 class="text-subtitle-1 mb-2">Election</h2>
        <v-row dense>
          <v-col cols="12" md="6">
            <v-text-field v-model.number="form.year" label="Tahun" type="number" />
          </v-col>
          <v-col cols="12" md="6" class="d-flex align-center">
            <v-switch 
              v-model="form.is_open" 
              inset 
              label="Voting dibuka?" 
              color="success"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field v-model="form.start_date" label="Mulai (YYYY-MM-DD)" placeholder="2025-10-01" />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field v-model="form.end_date" label="Berakhir (YYYY-MM-DD)" placeholder="2025-10-15" />
          </v-col>
          <v-col cols="12" md="6">
            <v-switch 
              v-model="form.show_results" 
              inset 
              label="Tampilkan hasil di beranda?" 
              color="success"
            />
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
            <v-col cols="12" md="6">
              <v-text-field v-model="newCand.name" label="Nama kandidat" required />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="newCand.institution" label="Institusi / Universitas" />
            </v-col>
            <v-col cols="12">
              <v-file-input 
                v-model="newCand.posterFile" 
                label="Upload Poster (JPG/PNG)" 
                accept="image/*"
                prepend-icon="mdi-camera"
                @change="previewImage"
              />
            </v-col>
          </v-row>
          
          <v-img 
            v-if="newCand.posterPreview" 
            :src="newCand.posterPreview" 
            max-height="200" 
            class="mb-3 rounded"
          />

          <v-textarea
            v-model="newCand.vision"
            label="Visi & Misi (Markdown)"
            rows="8"
            auto-grow
            hint="Gunakan format Markdown: **bold**, *italic*, # Heading, - list item, dll."
            persistent-hint
            class="mb-3"
          />

          <!-- Markdown Preview -->
          <v-expansion-panels v-if="newCand.vision" class="mb-3">
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon class="mr-2">mdi-eye</v-icon>
                Preview Markdown
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <div class="markdown-preview pa-4" v-html="previewMarkdown(newCand.vision)"></div>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>

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
            <v-list-item-subtitle class="text-truncate">
              {{ c.institution || 'Institusi tidak tersedia' }}
            </v-list-item-subtitle>
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
            <v-switch 
              v-model="importOverwrite" 
              label="Overwrite token jika email sudah ada?" 
              inset 
              color="success"
            />
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
              <v-switch 
                v-model="resendAll" 
                label="Kirim ulang ke SEMUA" 
                inset 
                color="success"
                class="mt-2" 
              />
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

        <!-- Updated Edit Dialog -->
        <v-dialog v-model="editDialog" max-width="800" scrollable>
          <v-card>
            <v-card-title class="pa-4">
              <span class="text-h6">Edit Kandidat</span>
            </v-card-title>
            <v-divider />
            <v-card-text class="pa-4">
              <v-text-field v-model="editCand.name" label="Nama" class="mb-3" />
              <v-text-field v-model="editCand.institution" label="Institusi" class="mb-3" />
              <v-text-field v-model="editCand.poster_url" label="Poster URL" class="mb-3" />
              
              <v-textarea
                v-model="editCand.vision"
                label="Visi & Misi (Markdown)"
                rows="10"
                auto-grow
                hint="Gunakan format Markdown"
                persistent-hint
                class="mb-3"
              />

              <!-- Preview for edit dialog -->
              <v-expansion-panels v-if="editCand.vision">
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <v-icon class="mr-2">mdi-eye</v-icon>
                    Preview Markdown
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <div class="markdown-preview pa-4" v-html="previewMarkdown(editCand.vision)"></div>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card-text>
            <v-divider />
            <v-card-actions class="pa-4">
              <v-spacer />
              <v-btn variant="text" @click="editDialog = false">Batal</v-btn>
              <v-btn color="primary" :loading="updating" @click="updateCandidate">Simpan</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </template>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import http from '@/api/http'
import { marked } from 'marked'

const hasKey = ref(!!localStorage.getItem('adminKey'))
const adminKeyInput = ref('')
const fallbackPoster = 'https://placecats.com/poppy/300/200'

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
const editDialog = ref(false)
const showPassword = ref(false)

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
  showPassword.value = false  // Reset visibility
  adminKeyInput.value = ''    // Clear input for security
  fetchData()
}

function clearKey() {
  localStorage.removeItem('adminKey')
  hasKey.value = false
  adminKeyInput.value = ''
  showPassword.value = false
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
    // Changed: Use /latest/ instead of /active/ to get latest election regardless of period
    const { data: latest } = await http.get('/api/elections/latest/')
    form.id = latest.id
    form.year = latest.year
    form.start_date = latest.start_date
    form.end_date = latest.end_date
    form.is_open = latest.is_open
    form.show_results = latest.show_results

    const { data: cds } = await http.get('/api/candidates/', { params: { election: latest.id } })
    candidates.value = cds
    await fetchStats()
  } catch (e) {
    // tidak ada election atau unauthorized
    if (e.response?.status === 401) {
      alert('Admin key tidak valid.')
      clearKey()
    } else if (e.response?.status === 404) {
      // Tidak ada election sama sekali, kosongkan form untuk buat baru
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
    await fetchStats() // Refresh stats after save
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
      year: form.year || new Date().getFullYear(),
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
    candidates.value = []
    alert('Election baru dibuat.')
  } catch (e) {
    alert('Gagal membuat election.')
  }
}

const newCand = reactive({ 
  name: '', 
  institution: '',
  vision: '',
  posterFile: null,
  posterPreview: null
})

const editCand = reactive({ 
  id: null, 
  name: '', 
  institution: '',
  vision: '', 
  poster_url: '' 
})

marked.setOptions({
  breaks: true,
  gfm: true,
})

function previewMarkdown(text) {
  if (!text) return ''
  return marked(text)
}

function previewImage(event) {
  const file = event.target.files?.[0] || newCand.posterFile?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      newCand.posterPreview = e.target.result
    }
    reader.readAsDataURL(file)
  } else {
    newCand.posterPreview = null
  }
}

async function addCandidate() {
  if (!form.id) return alert('Buat/isi election dulu.')
  adding.value = true
  try {
    const formData = new FormData()
    formData.append('election', form.id)
    formData.append('name', newCand.name)
    formData.append('institution', newCand.institution)
    formData.append('vision', newCand.vision)
    
    if (newCand.posterFile?.[0]) {
      formData.append('poster', newCand.posterFile[0])
    }

    const { data } = await http.post('/api/admin/candidates/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    candidates.value.unshift(data)
    newCand.name = ''
    newCand.institution = ''
    newCand.vision = ''
    newCand.posterFile = null
    newCand.posterPreview = null
  } catch (e) {
    alert('Gagal menambah kandidat.')
  } finally {
    adding.value = false
  }
}

function editCandidate(c) {
  editCand.id = c.id
  editCand.name = c.name
  editCand.institution = c.institution
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

async function updateCandidate() {
  updating.value = true
  try {
    const { data } = await http.patch(`/api/admin/candidates/${editCand.id}/`, {
      name: editCand.name,
      institution: editCand.institution,
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

.markdown-preview {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #fafafa;
  max-height: 400px;
  overflow-y: auto;
}

.markdown-preview :deep(h1),
.markdown-preview :deep(h2),
.markdown-preview :deep(h3) {
  margin-top: 1em;
  margin-bottom: 0.5em;
}

.markdown-preview :deep(p) {
  margin-bottom: 0.8em;
}

.markdown-preview :deep(ul),
.markdown-preview :deep(ol) {
  margin-left: 1.5em;
  margin-bottom: 0.8em;
}
</style>

