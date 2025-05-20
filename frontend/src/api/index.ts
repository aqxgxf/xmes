import axios, { type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios';
import { ElMessage } from 'element-plus';
import {
  type User,
  type LoginCredentials,
  type Product,
  type ProductCategory,
  type ProductParam,
  type ProductParamValue,
  type Unit,
  type Material,
  type Process,
  type ProcessCode,
  type ProcessDetail,
  type ProductProcessCode,
  type Bom,
  type BomItem,
  type PaginatedResponse,
  type PaginationParams,
  type CategoryMaterialRule,
  type CategoryMaterialRuleParam,
  type CategoryMaterialRuleForm
} from '../types';

// Base API configuration
const API = axios.create({
  baseURL: '/api',
  timeout: 30000,
  withCredentials: true // Enable sending cookies with requests
});

// Configure CSRF
API.defaults.xsrfCookieName = 'csrftoken';
API.defaults.xsrfHeaderName = 'X-CSRFToken';

// Helper to get a cookie value by name
export const getCookie = (name: string): string | null => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    const part = parts.pop();
    if (part) {
      return part.split(';').shift() || null;
    }
  }
  return null;
};

// Get CSRF token function
export const getCsrfToken = async () => {
  // First check if CSRF token cookie already exists
  const existingToken = getCookie('csrftoken');
  if (existingToken) {
    console.log('Using existing CSRF token from cookie');
    return existingToken;
  }

  try {
    console.log('Fetching new CSRF token');
    const response = await API.get('/csrf/');
    return response.data.csrftoken;
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error);
    return null;
  }
};

// Initialize CSRF token
(async () => {
  await getCsrfToken();
})();

// Request interceptor
API.interceptors.request.use(
  (config) => {
    // For FormData requests, ensure the CSRF token is still sent
    if (config.data instanceof FormData) {
      // The token is automatically added from cookies for regular requests
      // Just ensure content type is not set for FormData to let the browser set it with boundary
      if (config.headers && config.headers['Content-Type']) {
        delete config.headers['Content-Type'];
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
API.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle common API errors
    if (error.response) {
      const status = error.response.status;

      if (status === 401) {
        // Unauthorized - redirect to login
        window.location.href = '/login';
        return Promise.reject(error);
      }

      if (status === 403) {
        // Special handling for CSRF errors
        if (error.response.data && (error.response.data as any).detail &&
          (error.response.data as any).detail.includes('CSRF')) {
          ElMessage.error('CSRF验证失败，请刷新页面后重试');
          // Try to refresh the CSRF token
          getCsrfToken().then(() => {
            console.log('CSRF token refreshed');
          });
        } else {
          ElMessage.error('无权限执行此操作');
        }
        return Promise.reject(error);
      }

      if (status === 404) {
        ElMessage.error('请求的资源不存在');
        return Promise.reject(error);
      }

      if (status === 500) {
        ElMessage.error('服务器内部错误');
        return Promise.reject(error);
      }
    }

    // Network errors
    if (!error.response) {
      ElMessage.error('网络错误，请检查你的网络连接');
    }

    return Promise.reject(error);
  }
);

// API modules
export const authAPI = {
  login: (username: string, password: string) =>
    API.post<{ msg: string, token?: string }>('/login/', { username, password }),

  register: (username: string, password: string, groups: string[] = []) =>
    API.post<User>('/register/', { username, password, groups }),

  getUserInfo: () =>
    API.get<User>('/userinfo/'),

  logout: () =>
    API.post<{ msg: string }>('/logout/')
};

export const userAPI = {
  getUsers: () =>
    API.get<User[] | PaginatedResponse<User>>('/users/'),

  updateUser: (userId: number, data: Partial<User>) =>
    API.post<User>(`/user/${userId}/update/`, data),

  deleteUser: (userId: number) =>
    API.post<{ success: boolean }>(`/user/${userId}/delete/`)
};

export const groupAPI = {
  getGroups: () =>
    API.get<string[]>('/groups/'),

  addGroup: (name: string) =>
    API.post<{ success: boolean }>('/group/add/', { name }),

  updateGroup: (groupName: string, newName: string) =>
    API.post<{ success: boolean }>(`/group/${groupName}/update/`, { new_name: newName }),

  deleteGroup: (groupName: string) =>
    API.post<{ success: boolean }>(`/group/${groupName}/delete/`)
};

export const menuAPI = {
  getMenus: () =>
    API.get<any[]>('/menus/'),

  saveMenu: (data: {
    id?: number;
    name: string;
    path: string;
    parent: number | null;
    groups: string[]
  }) =>
    API.post<any>('/menu/save/', data),

  deleteMenu: (menuId: number) =>
    API.post<{ success: boolean }>(`/menu/${menuId}/delete/`)
};

export const productAPI = {
  getProducts: (params?: PaginationParams) =>
    API.get<Product[] | PaginatedResponse<Product>>('/products/', { params }),

  getProduct: (id: number) =>
    API.get<Product>(`/products/${id}/`),

  createProduct: (data: Partial<Product>) =>
    API.post<Product>('/products/', data),

  updateProduct: (id: number, data: Partial<Product>) =>
    API.put<Product>(`/products/${id}/`, data),

  deleteProduct: (id: number) =>
    API.delete<{ success: boolean }>(`/products/${id}/`),

  importProducts: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return API.post<{
      msg: string;
      total: number;
      success: number;
      fail: number;
      skipped: number;
      fail_msgs: string[];
      skipped_reasons: string[];
      duplicate_codes: string[];
      processed_data: Record<string, any>;
    }>('/products/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};

export const categoryAPI = {
  getCategories: (params?: PaginationParams) =>
    API.get<ProductCategory[] | PaginatedResponse<ProductCategory>>('/product-categories/', { params }),

  getCategory: (id: number) =>
    API.get<ProductCategory>(`/product-categories/${id}/`),

  createCategory: (data: Partial<ProductCategory> | FormData) => {
    // For FormData, we need special handling for CSRF
    const headers: Record<string, string> = {};

    // Don't set Content-Type for FormData to let the browser handle it
    if (!(data instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    return API.post<ProductCategory>('/product-categories/', data, { headers });
  },

  updateCategory: (id: number, data: Partial<ProductCategory> | FormData) => {
    // For FormData, we need special handling for CSRF
    const headers: Record<string, string> = {};

    // Don't set Content-Type for FormData to let the browser handle it
    if (!(data instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    return API.put<ProductCategory>(`/product-categories/${id}/`, data, { headers });
  },

  deleteCategory: (id: number) =>
    API.delete<{ success: boolean }>(`/product-categories/${id}/`),

  importCategories: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    return API.post<{ success: boolean; count: number }>('/product-categories/import/', formData, {
      headers: {} // Let browser set the correct Content-Type with boundary
    });
  }
};

export const paramAPI = {
  getCategoryParams: () =>
    API.get<ProductParam[] | PaginatedResponse<ProductParam>>('/category-params/'),

  createCategoryParam: (data: Partial<ProductParam>) =>
    API.post<ProductParam>('/category-params/', data),

  updateCategoryParam: (id: number, data: Partial<ProductParam>) =>
    API.put<ProductParam>(`/category-params/${id}/`, data),

  deleteCategoryParam: (id: number) =>
    API.delete<{ success: boolean }>(`/category-params/${id}/`),

  getParamValues: (productId: number) =>
    API.get<ProductParamValue[] | PaginatedResponse<ProductParamValue>>('/product-param-values/', { params: { product: productId } }),

  saveParamValue: (data: Partial<ProductParamValue>) =>
    API.post<ProductParamValue>('/product-param-values/', data),

  updateParamValue: (id: number, data: Partial<ProductParamValue>) =>
    API.put<ProductParamValue>(`/product-param-values/${id}/`, data)
};

export const materialAPI = {
  getMaterials: (params?: PaginationParams) =>
    API.get<Material[] | PaginatedResponse<Material>>('/materials/', { params }),

  getMaterial: (id: number) =>
    API.get<Material>(`/materials/${id}/`),

  createMaterial: (data: Partial<Material>) =>
    API.post<Material>('/materials/', data),

  updateMaterial: (id: number, data: Partial<Material>) =>
    API.put<Material>(`/materials/${id}/`, data),

  deleteMaterial: (id: number) =>
    API.delete<{ success: boolean }>(`/materials/${id}/`),

  importMaterials: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return API.post<{ success: boolean; count: number }>('/materials/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};

export const processAPI = {
  getProcesses: () =>
    API.get<Process[] | PaginatedResponse<Process>>('/processes/'),

  getProcess: (id: number) =>
    API.get<Process>(`/processes/${id}/`),

  createProcess: (data: Partial<Process>) =>
    API.post<Process>('/processes/', data),

  updateProcess: (id: number, data: Partial<Process>) =>
    API.put<Process>(`/processes/${id}/`, data),

  deleteProcess: (id: number) =>
    API.delete<{ success: boolean }>(`/processes/${id}/`),

  getProcessCodes: () =>
    API.get<ProcessCode[] | PaginatedResponse<ProcessCode>>('/process-codes/'),

  getProcessCode: (id: number) =>
    API.get<ProcessCode>(`/process-codes/${id}/`),

  createProcessCode: (data: Partial<ProcessCode>) =>
    API.post<ProcessCode>('/process-codes/', data),

  updateProcessCode: (id: number, data: Partial<ProcessCode>) =>
    API.put<ProcessCode>(`/process-codes/${id}/`, data),

  deleteProcessCode: (id: number) =>
    API.delete<{ success: boolean }>(`/process-codes/${id}/`),

  getProductProcessCodes: () =>
    API.get<ProductProcessCode[] | PaginatedResponse<ProductProcessCode>>('/product-process-codes/'),

  createProductProcessCode: (data: Partial<ProductProcessCode>) =>
    API.post<ProductProcessCode>('/product-process-codes/', data),

  updateProductProcessCode: (id: number, data: Partial<ProductProcessCode>) =>
    API.put<ProductProcessCode>(`/product-process-codes/${id}/`, data),

  deleteProductProcessCode: (id: number) =>
    API.delete<{ success: boolean }>(`/product-process-codes/${id}/`),

  getProcessDetails: (codeId?: number) => {
    const params = codeId ? { process_code: codeId } : undefined;
    return API.get<ProcessDetail[] | PaginatedResponse<ProcessDetail>>('/process-details/', { params });
  },

  createProcessDetail: (data: Partial<ProcessDetail>) =>
    API.post<ProcessDetail>('/process-details/', data),

  updateProcessDetail: (id: number, data: Partial<ProcessDetail>) =>
    API.put<ProcessDetail>(`/process-details/${id}/`, data),

  deleteProcessDetail: (id: number) =>
    API.delete<{ success: boolean }>(`/process-details/${id}/`)
};

export const bomAPI = {
  getBoms: () =>
    API.get<Bom[] | PaginatedResponse<Bom>>('/boms/'),

  getBom: (id: number) =>
    API.get<Bom>(`/boms/${id}/`),

  createBom: (data: Partial<Bom>) =>
    API.post<Bom>('/boms/', data),

  updateBom: (id: number, data: Partial<Bom>) =>
    API.put<Bom>(`/boms/${id}/`, data),

  deleteBom: (id: number) =>
    API.delete<{ success: boolean }>(`/boms/${id}/`),

  getBomItems: (bomId: number) =>
    API.get<BomItem[] | PaginatedResponse<BomItem>>('/bom-items/', { params: { bom: bomId } }),

  createBomItem: (data: Partial<BomItem>) =>
    API.post<BomItem>('/bom-items/', data),

  updateBomItem: (id: number, data: Partial<BomItem>) =>
    API.put<BomItem>(`/bom-items/${id}/`, data),

  deleteBomItem: (id: number) =>
    API.delete<{ success: boolean }>(`/bom-items/${id}/`)
};

export const unitAPI = {
  getUnits: (params?: PaginationParams) =>
    API.get<Unit[] | PaginatedResponse<Unit>>('/units/', { params }),

  getUnit: (id: number) =>
    API.get<Unit>(`/units/${id}/`),

  createUnit: (data: Partial<Unit>) =>
    API.post<Unit>('/units/', data),

  updateUnit: (id: number, data: Partial<Unit>) =>
    API.put<Unit>(`/units/${id}/`, data),

  deleteUnit: (id: number) =>
    API.delete<{ success: boolean }>(`/units/${id}/`),

  importUnits: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return API.post<{ success: boolean; count: number }>('/units/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};

export const orderAPI = {
  getOrders: (params?: PaginationParams) =>
    API.get<any[] | PaginatedResponse<any>>('/orders/', { params }),

  getOrder: (id: number) =>
    API.get<any>(`/orders/${id}/`),

  createOrder: (data: any) =>
    API.post<any>('/orders/', data),

  updateOrder: (id: number, data: any) =>
    API.put<any>(`/orders/${id}/`, data),

  deleteOrder: (id: number) =>
    API.delete<{ success: boolean }>(`/orders/${id}/`)
};

export const workOrderAPI = {
  getWorkOrders: (params?: PaginationParams) =>
    API.get<any[] | PaginatedResponse<any>>('/workorders/', { params }),

  getWorkOrder: (id: number) =>
    API.get<any>(`/workorders/${id}/`),

  createWorkOrder: (data: any) =>
    API.post<any>('/workorders/', data),

  updateWorkOrder: (id: number, data: any) =>
    API.put<any>(`/workorders/${id}/`, data),

  deleteWorkOrder: (id: number) =>
    API.delete<{ success: boolean }>(`/workorders/${id}/`),

  getWorkOrderProcessDetails: (workOrderId: number) =>
    API.get<any[] | PaginatedResponse<any>>('/workorder-process-details/', { params: { workorder: workOrderId } }),

  updateWorkOrderProcessDetail: (id: number, data: any) =>
    API.put<any>(`/workorder-process-details/${id}/`, data)
};

export const companyAPI = {
  getCompanies: () =>
    API.get<any[] | PaginatedResponse<any>>('/companies/'),

  getCompany: (id: number) =>
    API.get<any>(`/companies/${id}/`),

  createCompany: (data: any) =>
    API.post<any>('/companies/', data),

  updateCompany: (id: number, data: any) =>
    API.put<any>(`/companies/${id}/`, data),

  deleteCompany: (id: number) =>
    API.delete<{ success: boolean }>(`/companies/${id}/`)
};

export const customerAPI = {
  getCustomers: () =>
    API.get<any[] | PaginatedResponse<any>>('/customers/'),

  getCustomer: (id: number) =>
    API.get<any>(`/customers/${id}/`),

  createCustomer: (data: any) =>
    API.post<any>('/customers/', data),

  updateCustomer: (id: number, data: any) =>
    API.put<any>(`/customers/${id}/`, data),

  deleteCustomer: (id: number) =>
    API.delete<{ success: boolean }>(`/customers/${id}/`)
};

export default API;
