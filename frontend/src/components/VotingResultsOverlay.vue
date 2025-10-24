<template>
    <v-overlay v-model="showOverlay" class="align-center justify-center" :persistent="false" @click:outside="close">
        <v-card class="results-card" :class="{ 'slide-in': showOverlay }" max-width="900" elevation="24">
            <!-- Confetti Canvas -->
            <canvas ref="confettiCanvas" class="confetti-canvas"></canvas>

            <!-- Header with Trophy -->
            <v-card-title class="results-header pa-6 text-center">
                <div class="trophy-container">
                    <v-icon size="80" color="amber-darken-1" class="trophy-icon">
                        mdi-trophy
                    </v-icon>
                    <div class="sparkles">✨</div>
                </div>
                <h2 class="text-h4 font-weight-bold mt-4 mb-2">
                    🎊 Hasil Pemilihan Resmi 🎊
                </h2>
                <p class="text-h6 text-medium-emphasis">
                    Pemilihan Ketua PPI Osaka-Nara {{ electionYear }}
                </p>
            </v-card-title>

            <v-divider></v-divider>

            <!-- Results Content -->
            <v-card-text class="pa-6">
                <!-- Winner Card -->
                <v-card v-if="winner" class="winner-card mb-6 pa-6" color="amber-lighten-5" elevation="4">
                    <div class="d-flex align-center flex-wrap">
                        <div class="winner-avatar-wrapper mr-6">
                            <v-avatar size="120" class="winner-avatar">
                                <v-img :src="winner.poster_url || fallbackPoster" />
                            </v-avatar>
                            <div class="winner-badge">
                                <v-icon color="white" size="32">mdi-crown</v-icon>
                            </div>
                        </div>
                        <div class="flex-grow-1">
                            <div class="text-overline text-amber-darken-2 font-weight-bold">
                                🏆 PEMENANG
                            </div>
                            <h3 class="text-h4 font-weight-bold mb-2">{{ winner.candidate_name }}</h3>
                            <div class="d-flex align-center flex-wrap gap-3">
                                <v-chip color="amber-darken-1" size="large" class="font-weight-bold">
                                    <v-icon start>mdi-vote</v-icon>
                                    {{ winner.votes }} Suara
                                </v-chip>
                                <v-chip color="success" size="large">
                                    <v-icon start>mdi-percent</v-icon>
                                    {{ winner.percentage }}%
                                </v-chip>
                            </div>
                        </div>
                    </div>
                </v-card>

                <!-- All Results -->
                <div class="results-list">
                    <h4 class="text-h6 mb-4">Detail Perolehan Suara</h4>
                    <v-card v-for="(result, index) in sortedResults" :key="result.candidate_id" class="mb-3 result-item"
                        :class="{ 'winner-item': index === 0 }" elevation="2">
                        <v-card-text class="pa-4">
                            <div class="d-flex align-center justify-space-between flex-wrap">
                                <div class="d-flex align-center flex-grow-1 mb-2 mb-sm-0">
                                    <div class="rank-badge" :class="`rank-${index + 1}`">
                                        {{ index + 1 }}
                                    </div>
                                    <v-avatar size="56" class="mx-3">
                                        <v-img :src="result.poster_url || fallbackPoster" />
                                    </v-avatar>
                                    <div>
                                        <div class="text-h6 font-weight-bold">{{ result.candidate_name }}</div>
                                        <div class="text-caption text-medium-emphasis">
                                            {{ result.institution || 'Institusi tidak tersedia' }}
                                        </div>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <div class="text-h5 font-weight-bold">{{ result.votes }}</div>
                                    <div class="text-caption">suara ({{ result.percentage }}%)</div>
                                </div>
                            </div>
                            <!-- Progress Bar -->
                            <v-progress-linear :model-value="result.percentage"
                                :color="index === 0 ? 'amber-darken-1' : 'primary'" height="12" rounded class="mt-3">
                                <template v-slot:default>
                                    <strong class="text-white">{{ result.percentage }}%</strong>
                                </template>
                            </v-progress-linear>
                        </v-card-text>
                    </v-card>
                </div>

                <!-- Statistics -->
                <v-card class="mt-6 stats-card" color="blue-grey-lighten-5" elevation="0">
                    <v-card-text class="pa-4">
                        <v-row dense>
                            <v-col cols="12" sm="4">
                                <div class="text-center">
                                    <v-icon size="40" color="primary">mdi-account-multiple</v-icon>
                                    <div class="text-h5 font-weight-bold mt-2">{{ totalVotes }}</div>
                                    <div class="text-caption">Total Suara</div>
                                </div>
                            </v-col>
                            <v-col cols="12" sm="4">
                                <div class="text-center">
                                    <v-icon size="40" color="success">mdi-account-check</v-icon>
                                    <div class="text-h5 font-weight-bold mt-2">{{ results.length }}</div>
                                    <div class="text-caption">Kandidat</div>
                                </div>
                            </v-col>
                            <v-col cols="12" sm="4">
                                <div class="text-center">
                                    <v-icon size="40" color="amber-darken-1">mdi-trophy-variant</v-icon>
                                    <div class="text-h5 font-weight-bold mt-2">
                                        {{ winner?.percentage || 0 }}%
                                    </div>
                                    <div class="text-caption">Persentase Pemenang</div>
                                </div>
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>
            </v-card-text>

            <v-divider></v-divider>

            <!-- Footer -->
            <v-card-actions class="pa-4 justify-center">
                <v-btn color="primary" size="large" variant="elevated" @click="close">
                    <v-icon start>mdi-close</v-icon>
                    Tutup
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-overlay>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'

const props = defineProps({
    modelValue: Boolean,
    results: {
        type: Array,
        default: () => []
    },
    candidates: {
        type: Array,
        default: () => []
    },
    electionYear: {
        type: null,
        default: new Date().getFullYear()
    }
})

const emit = defineEmits(['update:modelValue'])

const showOverlay = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value)
})

const confettiCanvas = ref(null)
const fallbackPoster = 'https://placecats.com/poppy/300/200'

// Enrich results with candidate data and percentage
const enrichedResults = computed(() => {
    return props.results.map(result => {
        const candidate = props.candidates.find(c => c.id === result.candidate_id)
        return {
            ...result,
            poster_url: candidate?.poster_url,
            institution: candidate?.institution,
            percentage: totalVotes.value > 0
                ? Math.round((result.votes / totalVotes.value) * 100)
                : 0
        }
    })
})

// Sort by votes descending
const sortedResults = computed(() => {
    return [...enrichedResults.value].sort((a, b) => b.votes - a.votes)
})

const winner = computed(() => sortedResults.value[0] || null)

const totalVotes = computed(() => {
    return props.results.reduce((sum, r) => sum + r.votes, 0)
})

function close() {
    showOverlay.value = false
}

// Confetti animation
function createConfetti() {
    if (!confettiCanvas.value) return

    const canvas = confettiCanvas.value
    const ctx = canvas.getContext('2d')

    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    const confetti = []
    const confettiCount = 150
    const colors = ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

    for (let i = 0; i < confettiCount; i++) {
        confetti.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height - canvas.height,
            r: Math.random() * 6 + 4,
            d: Math.random() * confettiCount,
            color: colors[Math.floor(Math.random() * colors.length)],
            tilt: Math.floor(Math.random() * 10) - 10,
            tiltAngleIncremental: Math.random() * 0.07 + 0.05,
            tiltAngle: 0
        })
    }

    let animationId

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height)

        confetti.forEach((c, i) => {
            ctx.beginPath()
            ctx.lineWidth = c.r / 2
            ctx.strokeStyle = c.color
            ctx.moveTo(c.x + c.tilt + c.r / 3, c.y)
            ctx.lineTo(c.x + c.tilt, c.y + c.tilt + c.r / 5)
            ctx.stroke()

            c.tiltAngle += c.tiltAngleIncremental
            c.y += (Math.cos(c.d) + 3 + c.r / 2) / 2
            c.tilt = Math.sin(c.tiltAngle - i / 3) * 15

            if (c.y > canvas.height) {
                confetti[i] = {
                    ...c,
                    x: Math.random() * canvas.width,
                    y: -30,
                    tilt: Math.floor(Math.random() * 10) - 20
                }
            }
        })

        animationId = requestAnimationFrame(draw)
    }

    draw()

    // Stop after 10 seconds
    setTimeout(() => {
        if (animationId) cancelAnimationFrame(animationId)
        ctx.clearRect(0, 0, canvas.width, canvas.height)
    }, 10000)
}

watch(showOverlay, (newVal) => {
    if (newVal) {
        nextTick(() => {
            createConfetti()
        })
    }
})

onMounted(() => {
    if (showOverlay.value) {
        createConfetti()
    }
})
</script>

<style scoped>
.results-card {
  position: relative;
  max-height: 90vh;
  overflow-y: auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.results-card :deep(.v-card-text),
.results-card :deep(.v-card-title) {
  background: white;
  color: rgba(0, 0, 0, 0.87);
}

.confetti-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9999;
}

.slide-in {
  animation: slideDown 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes slideDown {
  0% {
    transform: translateY(-100%) scale(0.8);
    opacity: 0;
  }
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

.results-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  position: relative;
  overflow: hidden;
}

.trophy-container {
  position: relative;
  display: inline-block;
}

.trophy-icon {
  animation: bounce 2s infinite;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.sparkles {
  position: absolute;
  top: -10px;
  right: -10px;
  font-size: 24px;
  animation: sparkle 1.5s infinite;
}

@keyframes sparkle {
  0%, 100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
  50% {
    transform: scale(1.3) rotate(180deg);
    opacity: 0.7;
  }
}

.winner-card {
  border: 3px solid #FFD700;
  box-shadow: 0 8px 24px rgba(255, 215, 0, 0.3);
  animation: glow 2s infinite;
  overflow: visible; /* IMPORTANT: Allow badge to overflow */
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 8px 24px rgba(255, 215, 0, 0.3);
  }
  50% {
    box-shadow: 0 8px 32px rgba(255, 215, 0, 0.6);
  }
}

/* Winner Avatar Container - UPDATED */
.winner-avatar-wrapper {
  position: relative;
  display: inline-block;
  padding: 8px; /* Prevent badge cutoff */
}

.winner-avatar {
  border: 4px solid #FFD700;
}

.winner-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
  animation: rotate 3s linear infinite;
  z-index: 10;
  border: 4px solid white;
}

@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.result-item {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.result-item:hover {
  transform: translateX(8px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.winner-item {
  border-left: 4px solid #FFD700;
  background: linear-gradient(90deg, rgba(255, 215, 0, 0.1) 0%, transparent 100%);
}

.rank-badge {
  min-width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  color: white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.rank-1 {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  animation: pulse 2s infinite;
}

.rank-2 {
  background: linear-gradient(135deg, #C0C0C0, #A8A8A8);
}

.rank-3 {
  background: linear-gradient(135deg, #CD7F32, #B8860B);
}

.rank-badge:not(.rank-1):not(.rank-2):not(.rank-3) {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.stats-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
}

.gap-3 {
  gap: 12px;
}
</style>
