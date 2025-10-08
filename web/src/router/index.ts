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
import STIntroPreview from '../views/STIntroPreview.vue'
import ConformanceClaims from '../views/ConformanceClaims.vue'
import FinalDocumentPreview from '../views/FinalDocumentPreview.vue'
import Assumptions from '../views/Assumptions.vue'
import Threats from '../views/Threats.vue'
import OrganizationalSecurityPolicies from '../views/OrganizationalSecurityPolicies.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/st-intro/cover', name: 'cover', component: Cover },
  { path: '/cover', redirect: '/st-intro/cover' },
  { path: '/generator', name: 'generator', component: Generator },
  { path: '/settings', name: 'settings', component: Settings },
  { path: '/st-intro/reference', name: 'st-reference', component: STReference },
  { path: '/st-intro/toe-reference', name: 'toe-reference', component: TOEReference },
  { path: '/st-intro/toe-overview', name: 'toe-overview', component: TOEOverview },
  { path: '/st-intro/toe-description', name: 'toe-description', component: TOEDescription },
  { path: '/st-intro/preview', name: 'st-intro-preview', component: STIntroPreview },
  { path: '/spd/assumptions', name: 'spd-assumptions', component: Assumptions },
  { path: '/spd/threats', name: 'spd-threats', component: Threats },
  { path: '/spd/osp', name: 'spd-osp', component: OrganizationalSecurityPolicies },
  { path: '/security/sfr', name: 'security-sfr', component: SecurityFunctionalRequirements },
  { path: '/security/sar', name: 'security-sar', component: SecurityAssuranceRequirements },
  { path: '/conformanceclaims', name: 'conformance-claims', component: ConformanceClaims },
  { path: '/final-preview', name: 'final-preview', component: FinalDocumentPreview },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
