import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchData, createData, updateData } from '../api/apiUtils'
import { api } from '../api'
import type { ApiResponse } from '../types/common'

// 用户接口
export interface User {
  id: number;
  username: string;
  email?: string;
  avatar?: string;
  role?: string;
  permissions?: string[];
  created_at?: string;
  [key: string]: any;
}

// 登录参数接口
export interface LoginParams {
  username: string;
  password: string;
}

// 角色类型
export type UserRole = 'admin' | 'manager' | 'user' | string;

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAuthenticated = computed(() => !!token.value)
  const userFullName = computed(() => user.value?.username || '')
  const userRole = computed(() => user.value?.role || '')

  // 从localStorage初始化
  function initFromStorage() {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    
    if (storedToken) {
      token.value = storedToken
    }
    
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (error) {
        console.error('Failed to parse stored user:', error)
        // 清除无效的user数据
        localStorage.removeItem('user')
      }
    }
  }

  // 登录
  async function login(username: string, password: string) {
    isLoading.value = true
    error.value = null
    
    try {
      // 使用原始api进行登录，因为这里的响应结构可能特殊
      const response = await api.post<ApiResponse<{ token: string; user: User }>>('/api/users/login/', { username, password })
      
      if (response.data.success) {
        const data = response.data.data
        token.value = data.token
        user.value = data.user
        
        // 保存到localStorage
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        
        return true
      } else {
        error.value = response.data.message || '登录失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '登录过程中发生错误'
      console.error('Login error:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 登出
  async function logout() {
    isLoading.value = true
    error.value = null
    
    try {
      // 调用后端登出接口
      await api.post('/api/users/logout/')
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // 清除本地存储和状态
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      isLoading.value = false
    }
  }

  // 获取用户信息
  async function fetchUserInfo() {
    if (!token.value) return false
    
    isLoading.value = true
    error.value = null
    
    const result = await fetchData<User>('/api/users/info/')
    
    if (result.data) {
      user.value = result.data
      localStorage.setItem('user', JSON.stringify(result.data))
      isLoading.value = false
      return true
    } else {
      error.value = result.error
      isLoading.value = false
      return false
    }
  }

  // 更新用户资料
  async function updateProfile(profileData: Partial<User>) {
    if (!user.value) return false
    
    isLoading.value = true
    error.value = null
    
    const result = await updateData<User>('/api/users/profile/', profileData)
    
    if (result.data) {
      // 更新本地用户数据
      user.value = { ...user.value, ...result.data }
      localStorage.setItem('user', JSON.stringify(user.value))
      isLoading.value = false
      return true
    } else {
      error.value = result.error
      isLoading.value = false
      return false
    }
  }

  // 清除错误
  function clearError() {
    error.value = null
  }

  // 检查权限
  function hasPermission(permission: string): boolean {
    if (!user.value || !user.value.permissions) return false
    return user.value.permissions.includes(permission)
  }

  // 重置状态
  function reset() {
    user.value = null
    token.value = null
    isLoading.value = false
    error.value = null
  }

  return {
    // 状态
    user,
    token,
    isLoading,
    error,
    
    // 计算属性
    isLoggedIn,
    isAuthenticated,
    userFullName,
    userRole,
    
    // 方法
    initFromStorage,
    login,
    logout,
    fetchUserInfo,
    updateProfile,
    clearError,
    hasPermission,
    reset
  }
}) 