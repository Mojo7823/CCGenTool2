import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import QueryData from '../views/QueryData.vue'
import ModifyData from '../views/ModifyData.vue'
import XmlParser from '../views/XmlParser.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/database/query', name: 'query', component: QueryData },
  { path: '/database/modify', name: 'modify', component: ModifyData },
  { path: '/xml-parser', name: 'xml-parser', component: XmlParser },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
