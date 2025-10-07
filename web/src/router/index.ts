import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Cover from '../views/Cover.vue'
import Generator from '../views/Generator.vue'
import Settings from '../views/Settings.vue'
import SecurityFunctionalRequirements from '../views/SecurityFunctionalRequirements.vue'
import SecurityAssuranceRequirements from '../views/SecurityAssuranceRequirements.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/cover', name: 'cover', component: Cover },
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
