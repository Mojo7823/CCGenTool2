import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Cover from '../views/Cover.vue'
import Generator from '../views/Generator.vue'
import Settings from '../views/Settings.vue'
import SecurityFunctionalRequirements from '../views/SecurityFunctionalRequirements.vue'
import SecurityAssuranceRequirements from '../views/SecurityAssuranceRequirements.vue'
import STReference from '../views/STReference.vue'
import TOEReference from '../views/TOEReference.vue'
import TOEOverview from '../views/TOEOverview.vue'
import TOEDescription from '../views/TOEDescription.vue'
import STIntroductionPreview from '../views/STIntroductionPreview.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/cover', name: 'cover', component: Cover },
  { path: '/st-introduction/reference', name: 'st-introduction-reference', component: STReference },
  { path: '/st-introduction/toe-reference', name: 'st-introduction-toe-reference', component: TOEReference },
  { path: '/st-introduction/toe-overview', name: 'st-introduction-toe-overview', component: TOEOverview },
  { path: '/st-introduction/toe-description', name: 'st-introduction-toe-description', component: TOEDescription },
  { path: '/st-introduction/preview', name: 'st-introduction-preview', component: STIntroductionPreview },
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
