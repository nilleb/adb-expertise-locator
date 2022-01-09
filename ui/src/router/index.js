import { createRouter, createWebHistory } from 'vue-router'
import SearchPage from '@/components/SearchPage.vue'

const routes = [
  {
    path: '/',
    name: 'Search',
    component: SearchPage,
    props: {
      title: "Skills finder",
    },
  },
  {
    path: '/view',
    name: 'ResultPreview',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../components/ResultPreview.vue')
  }
]
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})
export default router
