import { createRouter, createWebHistory } from 'vue-router'
import MesLogin from './components/MesLogin.vue'
import MesWelcome from './components/MesWelcome.vue'
import UserManage from './views/sysmgmt/UserManage.vue'
import GroupManage from './views/sysmgmt/GroupManage.vue'
import MenuManage from './views/sysmgmt/MenuManage.vue'
import CategoryParamList from './views/basedata/product/CategoryParamList.vue'
import ProductCategoryList from './views/basedata/product/ProductCategoryList.vue'
import ProductList from './views/basedata/product/ProductList.vue'
import OrderManage from './views/salesmgmt/OrderManage.vue'
import CompanyList from './views/basedata/product/CompanyList.vue'
import ProcessList from './views/basedata/process/ProcessList.vue'
import ProcessCodeList from './views/basedata/process/ProcessCodeList.vue'
import ProductProcessCodeList from './views/basedata/process/ProductProcessCodeList.vue'
import ProcessDetailList from './views/basedata/process/ProcessDetailList.vue'
import WorkOrderList from './views/productionmgmt/WorkOrderList.vue'
import WorkOrderProcessDetail from './views/productionmgmt/WorkOrderProcessDetail.vue'
import BomList from './views/basedata/bom/BomList.vue'
import BomDetailList from './views/basedata/bom/BomDetailList.vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const routes = [
  { path: '/login', component: MesLogin },
  { path: '/welcome', component: MesWelcome, meta: { requiresAuth: true } },
  { path: '/users', component: UserManage, meta: { requiresAuth: true } },
  { path: '/groups', component: GroupManage, meta: { requiresAuth: true } },
  { path: '/menus', component: MenuManage, meta: { requiresAuth: true } },
  { path: '/product-categories', component: ProductCategoryList, meta: { requiresAuth: true } },
  { path: '/category-params', component: CategoryParamList, meta: { requiresAuth: true } },
  { path: '/products', component: ProductList, meta: { requiresAuth: true } },
  { path: '/orders', component: OrderManage, meta: { requiresAuth: true } },
  { path: '/companies', component: CompanyList, meta: { requiresAuth: true } },
  { path: '/processes', component: ProcessList, meta: { requiresAuth: true } },
  { path: '/boms', component: BomList, meta: { requiresAuth: true } },
  { path: '/bom-details', component: BomDetailList, meta: { requiresAuth: true } },
  { path: '/process-codes', component: ProcessCodeList, meta: { requiresAuth: true } },
  { path: '/product-process-codes', component: ProductProcessCodeList, meta: { requiresAuth: true } },
  { path: '/process-details', component: ProcessDetailList, meta: { requiresAuth: true } },
  { path: '/workorders', component: WorkOrderList, meta: { requiresAuth: true } },
  { path: '/workorder-process-details/:id', component: WorkOrderProcessDetail, meta: { requiresAuth: true } },
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

// 检查路径是否允许访问（支持动态路由参数）
function isPathAllowed(currentPath: string, allowedPaths: string[]): boolean {
  // 直接匹配
  if (allowedPaths.includes(currentPath)) {
    return true
  }
  
  // 检查是否是动态路由参数
  for (const allowedPath of allowedPaths) {
    // 跳过根路径和空路径
    if (allowedPath === '/' || !allowedPath) continue

    // 如果当前路径以允许的路径开头，则可能是动态路由
    if (currentPath.startsWith(allowedPath)) {
      return true
    }
    
    // 特殊处理 /workorder-process-details/:id
    if (currentPath.startsWith('/workorder-process-details/') && 
        allowedPaths.includes('/workorders')) {
      return true
    }
  }
  
  return false
}

router.beforeEach(async (to, _from, next) => {
  if (to.path === '/login') {
    next()
    return
  }
  try {
    const res = await axios.get('/api/userinfo/', { withCredentials: true })
    if (res.data.username) {
      const menuRes = await axios.get('/api/menus/', { withCredentials: true })
      const allowedPaths = extractPaths(menuRes.data.menus)
      
      // 检查是否是工单工艺明细页面
      if (to.path.startsWith('/workorder-process-details/')) {
        // 检查用户是否有权限访问工单列表
        if (allowedPaths.includes('/workorders')) {
          next()
          return
        }
      }
      
      if (to.path !== '/welcome' && to.path !== '/login' && !isPathAllowed(to.path, allowedPaths)) {
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
