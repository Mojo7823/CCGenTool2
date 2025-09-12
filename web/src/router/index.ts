import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import QueryData from '../views/QueryData.vue'
import ModifyData from '../views/ModifyData.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/database/query', name: 'query', component: QueryData },
  { path: '/database/modify', name: 'modify', component: ModifyData },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
