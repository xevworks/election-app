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
    { path: '/', name: 'home', component: HomeView },
    { path: '/vote', name: 'vote', component: VoteView },
    { path: '/report', name: 'report', component: ReportView },
    { path: '/admin', name: 'admin', component: AdminView },
    { path: '/thank-you', name: 'thankyou', component: ThankYouView },
    { path: '/already-voted', name: 'alreadyvoted', component: AlreadyVotedView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

// Guard: jika sudah vote untuk election aktif, redirect ke thank you
router.beforeEach((to) => {
  if (to.name === 'vote') {
    try {
      const s = JSON.parse(sessionStorage.getItem('votedInfo') || 'null')
      if (s?.hasVoted && s?.electionId) {
        return { name: 'alreadyvoted', replace: true }
      }
    } catch {}
  }
  return true
})

export default router
