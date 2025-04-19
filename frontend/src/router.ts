import { createRouter, createWebHistory } from 'vue-router'
import MesLogin from './components/MesLogin.vue'
import MesWelcome from './components/MesWelcome.vue'
import UserManage from './views/sysmgmt/UserManage.vue'
import GroupManage from './views/sysmgmt/GroupManage.vue'
import MenuManage from './views/sysmgmt/MenuManage.vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const routes = [
  { path: '/login', component: MesLogin },
  { path: '/welcome', component: MesWelcome, meta: { requiresAuth: true } },
  { path: '/users', component: UserManage, meta: { requiresAuth: true } },
  { path: '/groups', component: GroupManage, meta: { requiresAuth: true } },
  { path: '/menus', component: MenuManage, meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

function extractPaths(menus: any[]): string[] {
  let paths: string[] = []
  for (const m of menus) {
    if (m.path) paths.push(m.path)
    if (m.children && m.children.length) {
      paths = paths.concat(extractPaths(m.children))
    }
  }
  return paths
}

router.beforeEach(async (to, from, next) => {
  if (to.path === '/login') {
    next()
    return
  }
  try {
    const res = await axios.get('/api/userinfo/', { withCredentials: true })
    if (res.data.username) {
      const menuRes = await axios.get('/api/menus/', { withCredentials: true })
      const allowedPaths = extractPaths(menuRes.data.menus)
      if (to.path !== '/welcome' && to.path !== '/login' && !allowedPaths.includes(to.path)) {
        ElMessage.error('无权限访问该页面')
        next('/welcome')
        return
      }
      next()
    } else {
      next('/login')
    }
  } catch (e: unknown) {
    if (typeof e === 'object' && e && 'response' in e && (e as any).response.status === 401) {
      if (to.path !== '/login') next('/login')
    } else {
      next()
    }
  }
})

export default router
