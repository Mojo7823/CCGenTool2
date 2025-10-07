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

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/cover', name: 'cover', component: Cover },
  { path: '/generator', name: 'generator', component: Generator },
  { path: '/settings', name: 'settings', component: Settings },
  { path: '/st-intro/reference', name: 'st-reference', component: STReference },
  { path: '/st-intro/toe-reference', name: 'toe-reference', component: TOEReference },
  { path: '/st-intro/toe-overview', name: 'toe-overview', component: TOEOverview },
  { path: '/st-intro/toe-description', name: 'toe-description', component: TOEDescription },
  { path: '/security/sfr', name: 'security-sfr', component: SecurityFunctionalRequirements },
  { path: '/security/sar', name: 'security-sar', component: SecurityAssuranceRequirements },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
