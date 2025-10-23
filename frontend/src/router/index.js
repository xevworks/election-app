import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import VoteView from '@/views/VoteView.vue'
import ReportView from '@/views/ReportView.vue'
import AdminView from '@/views/AdminView.vue'
import ThankYouView from '@/views/ThankYouView.vue'
import AlreadyVotedView from '@/views/AlreadyVotedView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { title: 'Beranda' } },
    { path: '/vote', name: 'vote', component: VoteView, meta: { title: 'Vote' } },
    { path: '/report', name: 'report', component: ReportView, meta: { title: 'Laporkan Kecurangan' } },
    { path: '/admin', name: 'admin', component: AdminView, meta: { title: 'Admin Panel' } },
    { path: '/thank-you', name: 'thankyou', component: ThankYouView, meta: { title: 'Terima Kasih' } },
    { path: '/already-voted', name: 'alreadyvoted', component: AlreadyVotedView, meta: { title: 'Anda Sudah Memilih' } },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

// Update document title based on route
router.beforeEach((to, from, next) => {
  const baseTitle = 'KPU PPI Osaka-Nara'
  document.title = to.meta.title ? `${to.meta.title} | ${baseTitle}` : baseTitle
  
  // Guard: jika sudah vote untuk election aktif, redirect ke thank you
  if (to.name === 'vote') {
    try {
      const s = JSON.parse(sessionStorage.getItem('votedInfo') || 'null')
      if (s?.hasVoted && s?.electionId) {
        return next({ name: 'alreadyvoted', replace: true })
      }
    } catch {}
  }
  
  next()
})

export default router
