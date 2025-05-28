<template>
  <el-container class="app-container">
    <!-- 顶部导航栏 -->
    <el-header height="60px" class="header-bar">
      <div class="logo-area">
        <img alt="logo" class="logo" src="/logo.svg" style="height:32px;width:32px;" />
        <span class="logo-title">XMes</span>
      </div>
      <div class="collapse-btn" @click="isCollapse = !isCollapse">
        <el-icon><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
      </div>
      <div class="user-area">
        <el-dropdown>
          <span class="el-dropdown-link">
            <el-avatar :size="32" :src="user?.avatar || ''" style="margin-right:8px" />
            <span>{{ user?.username || '' }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled>
                <el-avatar :size="24" :src="user?.avatar || ''" style="margin-right:8px" />
                {{ user?.username || '' }}
              </el-dropdown-item>
              <el-dropdown-item @click="navigateTo('/user-profile')">
                <el-icon><User /></el-icon> 个人资料
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">
                <el-icon><SwitchButton /></el-icon> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container class="main-container">
      <!-- 实际菜单侧边栏 -->
      <el-aside width="auto" class="aside-container" :class="{ 'collapsed': isCollapse }">
        <div class="custom-menu">
          <!-- 固定菜单项 -->
          <div 
            class="custom-menu-item" 
            :class="{ 'active': activeMenu === '/welcome' }"
            @click="navigateTo('/welcome')"
          >
            <el-icon><HomeFilled /></el-icon>
            <span class="item-text" v-show="!isCollapse">首页</span>
          </div>

          <!-- 动态菜单项 -->
          <template v-for="(menu, idx) in menus">
            <!-- 顶级父菜单 -->
            <div 
              v-if="menu.children && menu.children.length" 
              :key="'menu-parent-' + idx"
              class="submenu-container"
            >
              <div 
                class="custom-menu-item submenu-title" 
                @click="toggleSubmenu(idx)"
              >
                <div style="display: flex; align-items: center;">
                  <el-icon><component :is="getIconComponent(menu.icon)" /></el-icon>
                  <span class="item-text" v-show="!isCollapse">{{ menu.title || menu.name }}</span>
                </div>
                <el-icon class="arrow-icon" v-show="!isCollapse">
                  <ArrowRight style="transform: rotate(90deg);" v-if="openedSubmenus.includes(idx)" />
                  <ArrowRight v-else />
                </el-icon>
              </div>

              <!-- 子菜单 -->
              <div 
                class="submenu" 
                v-show="!isCollapse && openedSubmenus.includes(idx)"
              >
                <template v-for="(submenu, subIdx) in menu.children">
                  <!-- 多级子菜单 -->
                  <div 
                    v-if="submenu.children && submenu.children.length"
                    :key="'submenu-parent-' + subIdx + '-' + submenu.id"
                    class="custom-menu-item submenu-item multi-level-parent" 
                    :class="{ 'active': isMenuActive(submenu.path) }"
                    @click="handleMenuItemClick(submenu)"
                  >
                    <span class="item-text multi-level-menu">
                      {{ submenu.title || submenu.name }}
                      <el-icon class="sub-arrow-icon">
                        <ArrowDown v-if="isMenuExpanded(submenu.id)" />
                        <ArrowRight v-else />
                      </el-icon>
                    </span>
                  </div>
                  <!-- 递归处理更深层的子菜单 -->
                  <div 
                    v-if="submenu.children && submenu.children.length && isMenuExpanded(submenu.id)"
                    :key="'submenu-children-' + subIdx + '-' + submenu.id"
                    class="deep-submenu"
                  >
                    <div 
                      v-for="(childItem, childIdx) in submenu.children" 
                      :key="childItem.id || childIdx"
                      class="custom-menu-item deep-submenu-item"
                      :class="{ 'active': isMenuActive(childItem.path) }"
                      @click="handleMenuItemClick(childItem)"
                    >
                      <span class="item-text">{{ childItem.title || childItem.name }}</span>
                    </div>
                  </div>
                  <!-- 非多级子菜单 -->
                  <div 
                    v-else-if="!submenu.children || !submenu.children.length"
                    :key="'submenu-leaf-' + subIdx + '-' + submenu.id"
                    class="custom-menu-item submenu-item"
                    :class="{ 'active': isMenuActive(submenu.path) }"
                    @click="handleMenuItemClick(submenu)"
                  >
                    <span class="item-text">{{ submenu.title || submenu.name }}</span>
                  </div>
                </template>
              </div>
            </div>
            
            <!-- 无子菜单的菜单项 -->
            <div 
              v-else
              :key="'menu-leaf-' + idx"
              class="custom-menu-item" 
              :class="{ 'active': isMenuActive(menu.path) }"
              @click="handleMenuItemClick(menu)"
            >
              <el-icon><component :is="getIconComponent(menu.icon)" /></el-icon>
              <span class="item-text" v-show="!isCollapse">{{ menu.title || menu.name }}</span>
            </div>
          </template>
        </div>
      </el-aside>
      
      <!-- 主内容区域 -->
      <el-container>
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
        

      </el-container>
    </el-container>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { 
  HomeFilled, Tools, ShoppingCart, DataLine, UserFilled,
  ArrowDown, User, SwitchButton, Fold, Expand, ArrowRight
} from '@element-plus/icons-vue'
import { useUserStore } from '../../stores/user'
import { storeToRefs } from 'pinia'

// 菜单项类型定义
interface MenuItem {
  id: number | string;
  name: string;
  title?: string;
  path: string;
  icon?: string;
  parent?: number | null;
  groups?: string[];
  children?: MenuItem[];
}

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const { user } = storeToRefs(userStore)

// 调试模式
// const showDebug = ref(false)

// 菜单数据
const menus = ref<MenuItem[]>([])

// 侧边栏折叠状态
const isCollapse = ref(false)

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})

// 计算菜单项是否激活
function isMenuActive(menuPath: string): boolean {
  const routePath = route.path;
  const normalizedMenuPath = ensureLeadingSlash(menuPath);
  return routePath === normalizedMenuPath;
}

// 检查菜单数据是否加载
// const hasMenus = computed(() => menus.value.length > 0)


// 处理图标组件
function getIconComponent(iconName?: string) {
  if (!iconName) return null
  
  // 映射后端图标名称到前端组件
  const iconMap: Record<string, any> = {
    'home': HomeFilled,
    'tools': Tools,
    'cart': ShoppingCart,
    'data': DataLine,
    'user': UserFilled,
    'default': HomeFilled
  }
  
  return iconMap[iconName] || null
}

// 导航到指定路径
function navigateTo(path: string) {
  router.push(path)
}

// 加载菜单数据
async function loadMenus() {
  try {
    const response = await axios.get('/api/menus/', { withCredentials: true })
    
    // 检查是否有菜单数据
    let menuData = []
    
    if (response.data && response.data.success && response.data.data) {
      menuData = response.data.data
    } else if (response.data && response.data.menus) {
      menuData = response.data.menus
    }
    
    // 有菜单数据时进行处理
    if (menuData && menuData.length > 0) {
      // 处理菜单路径 - 保留原始路径格式，以便于统一处理
      const processMenus = (items: MenuItem[]): MenuItem[] => {
        return items.map(item => {
          // 创建新对象避免修改原对象
          const newItem = { ...item }
          
          // 递归处理子菜单
          if (newItem.children && newItem.children.length) {
            newItem.children = processMenus(newItem.children)
          }
          
          return newItem
        })
      }
      
      // 处理菜单路径
      menus.value = processMenus(menuData)
      // console.log('处理后的菜单:', menus.value)
    } else {
      console.warn('没有找到菜单数据')
      
      // 如果没有菜单数据，提供基本菜单保障系统可用
      menus.value = [
        {
          id: 1,
          name: '基础数据',
          path: '',
          children: [
            { id: 11, name: '公司管理', path: 'companies', parent: 1 },
            { id: 12, name: '产品类管理', path: 'product-categories', parent: 1 }
          ]
        },
        {
          id: 2,
          name: '系统管理',
          path: '',
          children: [
            { id: 21, name: '用户管理', path: 'users', parent: 2 }
          ]
        }
      ]
    }
  } catch (error) {
    console.error('加载菜单失败:', error)
    
    // 如果加载失败，提供基本菜单保障系统可用
    menus.value = [
      {
        id: 1,
        name: '基础数据',
        path: '',
        children: [
          { id: 11, name: '公司管理', path: 'companies', parent: 1 },
          { id: 12, name: '产品类管理', path: 'product-categories', parent: 1 }
        ]
      },
      {
        id: 2,
        name: '系统管理',
        path: '',
        children: [
          { id: 21, name: '用户管理', path: 'users', parent: 2 }
        ]
      }
    ]
  }
}

// 退出登录
async function handleLogout() {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await userStore.logout()
    ElMessage.success('已成功退出')
    router.push('/login')
  } catch {
    // 用户取消操作
  }
}

// 组件加载时获取菜单数据
onMounted(async () => {
  await userStore.getLoginStatus();
  loadMenus();
})

// 子菜单展开状态
const openedSubmenus = ref<number[]>([])

// 切换子菜单展开状态
function toggleSubmenu(index: number) {
  if (openedSubmenus.value.includes(index)) {
    openedSubmenus.value = openedSubmenus.value.filter(i => i !== index)
  } else {
    openedSubmenus.value.push(index)
  }
}

// 获取菜单路径
// function getMenuPath(path: string): string {
//   return path.startsWith('/') ? path.substring(1) : path
// }

// 确保路径以斜杠开头
function ensureLeadingSlash(path: string): string {
  return path.startsWith('/') ? path : '/' + path
}

// 处理菜单项点击
function handleMenuItemClick(item: MenuItem) {
  // console.log('点击菜单项:', item);

  // 检查菜单项是否有子菜单
  if (item.children && item.children.length > 0) {
    // 如果有子菜单，切换展开状态
    toggleMenuExpand(item.id);
    
    // 如果不是顶级菜单，需要确保其父菜单展开
    if (item.parent) {
      // 查找其父菜单在顶级菜单中的索引
      const parentIdx = menus.value.findIndex(m => m.id === item.parent);
      if (parentIdx !== -1 && !openedSubmenus.value.includes(parentIdx)) {
        // 确保父菜单展开
        toggleSubmenu(parentIdx);
      }
    }
  } else if (item.path) {
    // 如果没有子菜单但有路径，则导航到该路径
    navigateTo(ensureLeadingSlash(item.path));
  }
}

// 存储菜单展开状态
interface MenuState {
  [key: string]: boolean; // 使用菜单ID作为键，存储展开状态
}

// 存储所有菜单的展开状态
const menuExpandedState = ref<MenuState>({})

// 切换菜单展开状态
function toggleMenuExpand(menuId: string | number) {
  const id = String(menuId);
  menuExpandedState.value[id] = !menuExpandedState.value[id];
}

// 获取菜单是否展开
function isMenuExpanded(menuId: string | number): boolean {
  const id = String(menuId);
  return Boolean(menuExpandedState.value[id]);
}
</script>

<style>
/* 自定义菜单样式 */
.aside-container {
  background-color: #304156;
  width: 220px;
  transition: width 0.3s;
  overflow-x: hidden;
  overflow-y: auto;
  height: calc(100vh - 60px);
}

.aside-container.collapsed {
  width: 64px;
}

.custom-menu {
  padding: 16px 0;
}

.custom-menu-item {
  display: flex;
  align-items: center;
  height: 50px;
  padding: 0 16px;
  color: white !important;
  cursor: pointer;
  transition: background-color 0.3s;
  position: relative;
  margin-bottom: 4px;
}

.custom-menu-item:hover {
  background-color: #263445;
}

.custom-menu-item.active {
  background-color: #1890ff;
}

.custom-menu-item .el-icon {
  font-size: 18px;
  margin-right: 16px;
  color: white !important;
}

.item-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
  color: white !important;
  font-weight: 500;
}

.submenu-container {
  margin-bottom: 4px;
}

.submenu-title {
  background-color: #304156;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.submenu {
  background-color: #1f2d3d;
  padding-left: 16px;
}

.submenu-item {
  padding-left: 32px;
}

.multi-level-parent {
  position: relative;
}

.multi-level-menu {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.sub-arrow-icon {
  margin-left: 5px;
  font-size: 12px;
}

.deep-submenu {
  background-color: #1a2533;
  margin-top: 2px;
}

.deep-submenu-item {
  padding-left: 48px !important;
  font-size: 13px;
}

/* 调试面板样式 */
.debug-sidebar {
  background-color: #1a2533;
  color: white;
  overflow-y: auto;
  height: 100%;
  padding: 10px;
  border-left: 1px solid #444;
  z-index: 10;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);
}

.debug-menu-section {
  margin-bottom: 20px;
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  padding: 8px;
}

.debug-menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.debug-menu-item {
  padding: 8px 10px;
  margin: 4px 0;
  background-color: #2c3e50;
  border-radius: 4px;
  cursor: pointer;
  color: white;
  font-size: 13px;
}

.debug-menu-item:hover {
  background-color: #34495e;
}

.debug-menu-item.submenu-item {
  padding-left: 20px;
  background-color: #263238;
  margin-left: 10px;
  margin-right: 2px;
  font-size: 12px;
}

.debug-data {
  background-color: #263238;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 300px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>

<style scoped>
.app-container {
  height: 100vh;
  overflow: hidden;
}

.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #2d3a4b;
  color: #fff;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 10;
}

.logo-area {
  display: flex;
  align-items: center;
  height: 100%;
}

.logo-title {
  margin-left: 12px;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  transition: color 0.3s;
}

.collapse-btn:hover {
  color: #409EFF;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.debug-toggle-btn {
  background-color: #e6a23c;
  color: white;
  border: none;
}

.debug-toggle-btn:hover {
  background-color: #f0ad4e;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #fff;
}

.main-container {
  height: calc(100vh - 60px);
}

.el-menu-vertical {
  border-right: none;
  height: 100%;
  overflow-y: auto;
}

.el-menu-vertical:not(.el-menu--collapse) {
  width: 220px;
}

.main-content {
  padding: 20px;
  background-color: #f0f2f5;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 增强菜单可读性 */
:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
}

:deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
}

:deep(.el-menu-item.is-active) {
  background-color: #263445 !important;
}

:deep(.el-menu-item):hover, 
:deep(.el-sub-menu__title):hover {
  background-color: #263445 !important;
}

.arrow-icon {
  margin-left: 5px;
  font-size: 12px;
}
</style> 