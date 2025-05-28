import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from './stores/user'

// Define public paths (no auth required)
const PUBLIC_PATHS = ['/login', '/', '/welcome', '/pdf-viewer', '/native-pdf-viewer']

// Layouts
const AppLayout = () => import('./views/layout/AppLayout.vue')

// Authentication
const MesLogin = () => import('./components/MesLogin.vue')
const MesWelcome = () => import('./components/MesWelcome.vue')

// PDF Viewer
const PdfViewer = () => import('./components/common/PdfViewer.vue')

// System Management
const UserManage = () => import('./views/sysmgmt/UserManage.vue')
const GroupManage = () => import('./views/sysmgmt/GroupManage.vue')
const MenuManage = () => import('./views/sysmgmt/MenuManage.vue')
const DataImport = () => import('./views/sysmgmt/DataImport.vue')


// Base Data - Product
const CategoryParamList = () => import('./views/basedata/product/CategoryParamList.vue')
const ProductCategoryList = () => import('./views/basedata/product/ProductCategoryList.vue')
const ProductList = () => import('./views/basedata/product/ProductList.vue')
const ProductDetail = () => import('./views/basedata/product/ProductDetail.vue')
const ProductCategoryDetail = () => import('./views/basedata/product/ProductCategoryDetail.vue')
const CategoryMaterialRule = () => import('./views/basedata/product/CategoryMaterialRuleList.vue')

// Base Data - Process
const ProcessList = () => import('./views/basedata/process/ProcessList.vue')
const ProcessCodeList = () => import('./views/basedata/process/ProcessCodeList.vue')
const ProductProcessCodeList = () => import('./views/basedata/process/ProductProcessCodeList.vue')
const CategoryProcessCodeList = () => import('./views/basedata/process/CategoryProcessCodeList.vue')
import ProcessDetailList from './views/basedata/process/ProcessDetailList.vue'

// Base Data - BOM
const BomList = () => import('./views/basedata/bom/BomList.vue')
const BomDetailList = () => import('./views/basedata/bom/BomDetailList.vue')
const MaterialList = () => import('./views/basedata/bom/MaterialList.vue')

// Sales Management
const OrderManage = () => import('./views/salesmgmt/OrderManage.vue')

// Production Management
const WorkOrderList = () => import('./views/productionmgmt/WorkOrderList.vue')
const WorkOrderProcessDetail = () => import('./views/productionmgmt/WorkOrderProcessDetail.vue')
const WorkOrderFeedback = () => import('./views/productionmgmt/WorkOrderFeedback.vue')
const WorkOrderFeedbackList = () => import('./views/productionmgmt/WorkOrderFeedbackList.vue')

const CompanyList = () => import('./views/basedata/other/CompanyList.vue')
const UnitManage = () => import('./views/basedata/other/UnitManage.vue')
const MaterialTypeList = () => import('./views/basedata/other/MaterialTypeList.vue')

// Route definitions
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: MesLogin,
    meta: { title: '登录' }
  },
  {
    path: '/pdf-viewer',
    component: PdfViewer,
    meta: { title: 'PDF查看器' }
  },
  {
    path: '/native-pdf-viewer',
    component: { render: () => null },
    beforeEnter: (to, from, next) => {
      // 直接跳转到HTML模板
      const urlParams = new URLSearchParams(to.fullPath.substring(to.fullPath.indexOf('?')));
      const pdfUrl = urlParams.get('url');
      if (pdfUrl) {
        window.location.href = `/templates/pdfViewer.html?url=${encodeURIComponent(pdfUrl)}`;
      } else {
        window.location.href = '/templates/pdfViewer.html';
      }
    },
    meta: { title: 'PDF查看器' }
  },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      // Dashboard
      {
        path: 'welcome',
        component: MesWelcome,
        meta: {
          requiresAuth: true,
          title: '欢迎'
        }
      },

      // System Management
      {
        path: 'users',
        component: UserManage,
        meta: {
          requiresAuth: true,
          title: '用户管理'
        }
      },
      {
        path: 'groups',
        component: GroupManage,
        meta: {
          requiresAuth: true,
          title: '用户组管理'
        }
      },
      {
        path: 'menus',
        component: MenuManage,
        meta: {
          requiresAuth: true,
          title: '菜单管理'
        }
      },
      {
        path: 'data-import',
        component: DataImport,
        meta: {
          requiresAuth: true,
          title: '数据导入'
        }
      },

      // Base Data - Product
      {
        path: 'product-categories',
        component: ProductCategoryList,
        meta: {
          requiresAuth: true,
          title: '产品类别'
        }
      },
      {
        path: 'product-categories/:id/detail',
        component: ProductCategoryDetail,
        meta: { title: '产品类明细', requiresAuth: true, hidden: true }
      },
      {
        path: 'category-params',
        component: CategoryParamList,
        meta: {
          requiresAuth: true,
          title: '类别参数'
        }
      },
      {
        path: 'products',
        component: ProductList,
        meta: {
          requiresAuth: true,
          title: '产品管理'
        }
      },
      {
        path: 'products/:id/detail',
        component: ProductDetail,
        meta: { title: '产品明细', requiresAuth: true, hidden: true }
      },
      {
        path: 'companies',
        component: CompanyList,
        meta: {
          requiresAuth: true,
          title: '公司管理'
        }
      },
      {
        path: 'units',
        component: UnitManage,
        meta: {
          requiresAuth: true,
          title: '单位管理'
        }
      },
      {
        path: 'MaterialType',
        component: MaterialTypeList,
        meta: {
          requiresAuth: true,
          title: '材质管理'
        }
      },

      // Base Data - Process
      {
        path: 'processes',
        component: ProcessList,
        meta: {
          requiresAuth: true,
          title: '工序管理'
        }
      },
      {
        path: 'process-codes',
        component: ProcessCodeList,
        meta: {
          requiresAuth: true,
          title: '工艺流程'
        }
      },
      {
        path: 'product-process-codes',
        component: ProductProcessCodeList,
        meta: {
          requiresAuth: true,
          title: '产品工艺关联'
        }
      },
      {
        path: 'category-process-codes',
        component: CategoryProcessCodeList,
        meta: {
          requiresAuth: true,
          title: '产品类工艺关联'
        }
      },
      {
        path: 'process-details',
        redirect: '/process-codes',
        meta: {
          requiresAuth: true,
          title: '工艺流程明细'
        }
      },
      {
        path: 'process-details/:id',
        component: ProcessDetailList,
        meta: {
          requiresAuth: true,
          title: '工艺流程明细'
        }
      },

      // Base Data - BOM
      {
        path: 'boms',
        component: BomList,
        meta: {
          requiresAuth: true,
          title: 'BOM管理'
        }
      },
      {
        path: 'bom-details',
        component: BomDetailList,
        meta: {
          requiresAuth: true,
          title: 'BOM明细'
        }
      },
      {
        path: 'materials',
        component: MaterialList,
        meta: {
          requiresAuth: true,
          title: '物料管理'
        }
      },
      {
        path: 'category-material-rule',
        component: CategoryMaterialRule,
        meta: { title: 'BOM物料规则', requiresAuth: true }
      },
      // Sales Management
      {
        path: 'orders',
        component: OrderManage,
        meta: {
          requiresAuth: true,
          title: '订单管理'
        }
      },

      // Production Management
      {
        path: 'workorders',
        component: WorkOrderList,
        meta: {
          requiresAuth: true,
          title: '工单管理'
        }
      },
      {
        path: 'workorder-process-details/:id',
        component: WorkOrderProcessDetail,
        meta: {
          requiresAuth: true,
          title: '工单工艺明细'
        }
      },
      {
        path: 'workorder-feedback',
        component: WorkOrderFeedback,
        meta: {
          requiresAuth: true,
          title: '工单回冲'
        }
      },
      {
        path: 'workorder-feedback-list',
        component: WorkOrderFeedbackList,
        meta: {
          requiresAuth: true,
          title: '工单回冲明细查询'
        }
      },

      // User Profile
      {
        path: 'user-profile',
        component: () => import('./views/sysmgmt/UserProfile.vue'),
        meta: {
          requiresAuth: true,
          title: '个人资料'
        }
      },

      // Default route
      { path: '', redirect: '/welcome' as const }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

// Router instance
const router = createRouter({
  history: createWebHistory(),
  routes
})

/**
 * Extract all paths from a menu structure
 * @param menus - The menu items to extract paths from
 * @returns An array of paths
 */
function extractPaths(menus: any[]): string[] {
  const paths: string[] = []

  for (const menu of menus) {
    if (menu.path) {
      // Normalize path format (ensure it starts with /)
      const path = menu.path.startsWith('/') ? menu.path : `/${menu.path}`
      paths.push(path)
    }

    if (menu.children?.length) {
      paths.push(...extractPaths(menu.children))
    }
  }

  return paths
}

/**
 * Check if a path is allowed based on user permissions
 * @param currentPath - The current path to check
 * @param allowedPaths - List of paths the user has access to
 * @returns Whether the path is allowed
 */
function isPathAllowed(currentPath: string, allowedPaths: string[]): boolean {
  // 让所有登录用户都能访问个人资料页面（兼容带参数、斜杠等）
  if (currentPath.startsWith('user-profile')) {
    return true;
  }
  // Normalize path to ensure it starts with /
  const normalizedPath = currentPath.startsWith('/') ? currentPath : `/${currentPath}`

  // Check if path is directly allowed
  if (allowedPaths.includes(normalizedPath)) {
    return true
  }

  // Check for dynamic route parameters
  for (const allowedPath of allowedPaths) {
    // Skip root and empty paths
    if (allowedPath === '/' || !allowedPath) {
      continue
    }

    // If current path starts with allowed path, it might be a dynamic route
    if (normalizedPath.startsWith(allowedPath)) {
      return true
    }

    // Special case for workorder details (related to workorders)
    if (normalizedPath.includes('workorder-process-details/') &&
      allowedPaths.includes('/workorders')) {
      return true
    }
  }

  // Check public paths
  if (PUBLIC_PATHS.includes(normalizedPath)) {
    return true
  }

  console.log('Permission check failed:', normalizedPath, 'Allowed paths:', allowedPaths)
  return false
}

/**
 * Navigation guard to check authentication and authorization
 */
router.beforeEach(async (
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  // Set page title
  document.title = to.meta.title
    ? `${to.meta.title} - XMes生产管理系统`
    : 'XMes生产管理系统'

  // Always allow access to login page
  if (to.path === '/login') {
    next()
    return
  }

  // Allow access to public paths
  if (PUBLIC_PATHS.includes(to.path)) {
    next()
    return
  }

  // --- 新增：强制刷新Pinia用户状态 ---
  const userStore = useUserStore()
  await userStore.getLoginStatus()
  // ---

  try {
    // Check if user is authenticated
    const userResponse = await axios.get('/api/userinfo/', { withCredentials: true })

    if (userResponse.data.username) {
      // 允许所有已登录用户访问个人资料页面（兼容带斜杠和参数）
      if (to.path.startsWith('user-profile')) {
        next();
        return;
      }
      // Fetch user's menu permissions
      const menuResponse = await axios.get('/api/menus/', { withCredentials: true })
      const allowedPaths = extractPaths(menuResponse.data.menus)

      // Check if user has permission to access the requested path
      if (!isPathAllowed(to.path, allowedPaths)) {
        ElMessage.error('无权限访问该页面')
        next('/welcome')
        return
      }

      next()
    } else {
      // Not authenticated, redirect to login
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    }
  } catch (error: unknown) {
    // Handle authentication errors
    if (typeof error === 'object' && error && 'response' in error) {
      const responseError = error as { response: { status: number } }

      if (responseError.response.status === 401) {
        // Unauthorized, redirect to login
        if (to.path !== '/login') {
          next({
            path: '/login',
            query: { redirect: to.fullPath }
          })
          return
        }
      }
    }

    // For other errors, allow navigation
    next()
  }
})

// 新增原生PDF查看器
function nativePdfViewer() {
  // 直接跳转到HTML模板
  const urlParams = new URLSearchParams(window.location.search);
  const pdfUrl = urlParams.get('url');
  if (pdfUrl) {
    window.location.href = `/templates/pdfViewer.html?url=${encodeURIComponent(pdfUrl)}`;
  } else {
    window.location.href = '/templates/pdfViewer.html';
  }
  return null;
}

export default router

