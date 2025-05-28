import { defineStore } from 'pinia';
import { authAPI } from '../api';
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import router from '../router';
import { type LoginCredentials } from '../types';

export interface User {
  id: number;
  username: string;
  email?: string;
  groups?: string[];
  is_active?: boolean;
  last_login?: string;
  date_joined?: string;
  avatar?: string;
}

export interface LoginForm {
  username: string;
  password: string;
}

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User>({} as User);
  const token = ref<string | null>(null);
  const loading = ref(false);
  const isAuthenticated = ref(false);
  const username = ref<string>('');
  const avatar = ref<string>('');
  const groups = ref<string[]>([]);
  const isLoading = ref<boolean>(false);
  const isLoggedIn = ref<boolean>(false);
  const error = ref<string | null>(null);
  
  // Getters
  const isSuperAdmin = computed(() => {
    return groups.value.includes('超级管理员');
  });
  
  const hasPermission = computed(() => {
    return (requiredGroup: string) => {
      return groups.value.includes(requiredGroup) || isSuperAdmin.value;
    };
  });
  
  // Actions
  const getLoginStatus = async () => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await authAPI.getUserInfo();
      const userData = response.data as User;
      if (userData && userData.username) {
        username.value = userData.username;
        avatar.value = userData.avatar || '';
        groups.value = userData.groups || [];
        isLoggedIn.value = true;
        isAuthenticated.value = true;
        user.value = { ...userData };
      } else {
        isLoggedIn.value = false;
        isAuthenticated.value = false;
        user.value = {} as User;
      }
    } catch (err) {
      console.error('Failed to get user info:', err);
      isLoggedIn.value = false;
      isAuthenticated.value = false;
      error.value = '获取用户信息失败';
      user.value = {} as User;
    } finally {
      isLoading.value = false;
    }
    return isLoggedIn.value;
  };

  const login = async (userCredentials: LoginCredentials) => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await authAPI.login(
        userCredentials.username,
        userCredentials.password
      );
      
      if (response.data) {
        // Store token if it exists in the response
        if (response.data.token) {
          token.value = response.data.token;
          localStorage.setItem('token', response.data.token);
        }
        
        await getLoginStatus();
        ElMessage.success('登录成功');
        return true;
      } else {
        error.value = '用户名或密码错误';
        ElMessage.error('用户名或密码错误');
        return false;
      }
    } catch (err: any) {
      console.error('Login failed:', err);
      error.value = err.response?.data?.error || '登录失败';
      
      if (error.value) {
        ElMessage.error(error.value);
      } else {
        ElMessage.error('登录失败');
      }
      
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const logout = async () => {
    loading.value = true;
    
    try {
      await authAPI.logout();
      clearUserState();
      ElMessage.success('退出登录成功');
      router.push('/login');
      return { success: true };
    } catch (err) {
      console.error('Logout failed:', err);
      ElMessage.error('退出登录失败');
      return { success: false, error: '退出登录失败' };
    } finally {
      loading.value = false;
    }
  };

  const clearUserState = () => {
    username.value = '';
    avatar.value = '';
    groups.value = [];
    isLoggedIn.value = false;
    isAuthenticated.value = false;
    user.value = {} as User;
    token.value = null;
    localStorage.removeItem('token');
  };

  // Initialize user data from localStorage if available
  const initFromStorage = () => {
    try {
      // Get token from local storage if available
      const storedToken = localStorage.getItem('token');
      
      if (storedToken) {
        // Store token in state
        token.value = storedToken;
        // Use existing auth methods to restore session
        getLoginStatus();
      }
    } catch (error) {
      console.error('Failed to initialize from storage:', error);
    }
  };

  return {
    // State
    user,
    token,
    loading,
    isAuthenticated,
    username,
    avatar,
    groups,
    isLoading,
    isLoggedIn,
    error,
    
    // Getters
    isSuperAdmin,
    hasPermission,
    
    // Actions
    getLoginStatus,
    login,
    logout,
    clearUserState,
    initFromStorage
  };
}); 