import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Cover from '../views/Cover.vue'
import StReference from '../views/StReference.vue'
import ToeReference from '../views/ToeReference.vue'
import ToeOverview from '../views/ToeOverview.vue'
import ToeDescription from '../views/ToeDescription.vue'
import StIntroductionPreview from '../views/StIntroductionPreview.vue'
import Generator from '../views/Generator.vue'
import Settings from '../views/Settings.vue'
import SecurityFunctionalRequirements from '../views/SecurityFunctionalRequirements.vue'
import SecurityAssuranceRequirements from '../views/SecurityAssuranceRequirements.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/cover', name: 'cover', component: Cover },
  { path: '/st-introduction/reference', name: 'st-reference', component: StReference },
  { path: '/st-introduction/toe-reference', name: 'toe-reference', component: ToeReference },
  { path: '/st-introduction/toe-overview', name: 'toe-overview', component: ToeOverview },
  { path: '/st-introduction/toe-description', name: 'toe-description', component: ToeDescription },
  { path: '/st-introduction/preview', name: 'st-introduction-preview', component: StIntroductionPreview },
  { path: '/generator', name: 'generator', component: Generator },
  { path: '/settings', name: 'settings', component: Settings },
  { path: '/security/sfr', name: 'security-sfr', component: SecurityFunctionalRequirements },
  { path: '/security/sar', name: 'security-sar', component: SecurityAssuranceRequirements },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
