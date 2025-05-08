import axios from 'axios'

// 获取CSRF令牌函数
const getCSRFToken = (): string => {
  const name = 'csrftoken';
  let cookieValue = '';
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

// 创建axios实例
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // 确保请求包含凭证
})

// 请求拦截器：添加token和CSRF令牌
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加CSRF令牌到请求头中
    const csrfToken = getCSRFToken()
    if (csrfToken && ['post', 'put', 'delete', 'patch'].includes(config.method?.toLowerCase() || '')) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器：统一处理响应
api.interceptors.response.use(
  response => {
    // 如果后端返回的数据不是标准格式，这里可以进行转换
    if (!response.data.hasOwnProperty('success')) {
      return {
        ...response,
        data: {
          success: true,
          data: response.data,
          message: ''
        }
      }
    }
    return response
  },
  error => {
    // 统一处理错误
    const errorMsg = error.response?.data?.message || error.message || '请求失败'
    
    // 处理特定状态码
    if (error.response) {
      const status = error.response.status
      
      // 401：未授权，跳转到登录页
      if (status === 401) {
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
      
      // 403：无权限
      if (status === 403) {
        console.error('无权访问')
      }
    }
    
    return Promise.reject({
      ...error,
      message: errorMsg
    })
  }
)

export default {
  // 基础数据API
  basedata: {
    getProducts: () => api.get('/api/basedata/products/'),
    getCustomers: () => api.get('/api/basedata/customers/'),
    getMaterials: () => api.get('/api/basedata/materials/'),
    getSuppliers: () => api.get('/api/basedata/suppliers/'),
    // 新增公司API
    getCompanies: (params?: any) => api.get('/api/basedata/companies/', { params }),
    getCompany: (id: number) => api.get(`/api/basedata/companies/${id}/`),
    createCompany: (data: any) => api.post('/api/basedata/companies/', data),
    updateCompany: (id: number, data: any) => api.put(`/api/basedata/companies/${id}/`, data),
    deleteCompany: (id: number) => api.delete(`/api/basedata/companies/${id}/`),
    // 新增产品类API
    getProductCategories: (params?: any) => api.get('/api/product-categories/', { params }),
    getProductCategory: (id: number) => api.get(`/api/product-categories/${id}/`),
    createProductCategory: (data: any) => api.post('/api/product-categories/', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    updateProductCategory: (id: number, data: any) => api.put(`/api/product-categories/${id}/`, data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    deleteProductCategory: (id: number) => api.delete(`/api/product-categories/${id}/`)
  },
  
  // 生产管理API
  production: {
    getOrders: (params?: any) => api.get('/api/production/orders/', { params }),
    getOrder: (id: number) => api.get(`/api/production/orders/${id}/`),
    createOrder: (data: any) => api.post('/api/production/orders/', data),
    updateOrder: (id: number, data: any) => api.put(`/api/production/orders/${id}/`, data),
    deleteOrder: (id: number) => api.delete(`/api/production/orders/${id}/`),
    updateOrderStatus: (id: number, status: string) => api.post(`/api/production/orders/${id}/update_status/`, { status })
  },
  
  // 销售管理API
  sales: {
    getOrders: (params?: any) => api.get('/api/sales/orders/', { params }),
    getOrder: (id: number) => api.get(`/api/sales/orders/${id}/`),
    createOrder: (data: any) => api.post('/api/sales/orders/', data),
    updateOrder: (id: number, data: any) => api.put(`/api/sales/orders/${id}/`, data),
    deleteOrder: (id: number) => api.delete(`/api/sales/orders/${id}/`)
  },
  
  // 用户管理API
  user: {
    login: (data: { username: string; password: string }) => api.post('/api/users/login/', data),
    getInfo: () => api.get('/api/users/info/'),
    logout: () => api.post('/api/users/logout/')
  }
} 