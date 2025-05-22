import api from './index'
import type { ApiResponse, PaginatedResponse } from '../types/common'

/**
 * 处理API错误，提供统一的错误处理方式
 */
export function handleApiError(err: any, defaultMessage: string): string {
  const errorMessage = err.response?.data?.message || err.message || defaultMessage
  console.error(`API Error: ${defaultMessage}`, err)
  return errorMessage
}

/**
 * 执行GET请求
 */
export async function fetchData<T>(url: string, params?: any): Promise<{ 
  data: T | null; 
  error: string | null;
  count?: number;
}> {
  try {
    const response = await api.get<ApiResponse<T>>(url, { params })
    if (response.data.success) {
      return { 
        data: response.data.data, 
        error: null,
        count: 'count' in response.data ? (response.data.count as number) : undefined
      }
    } else {
      return { 
        data: null, 
        error: response.data.message || `获取${url}数据失败` 
      }
    }
  } catch (err: any) {
    return { 
      data: null, 
      error: handleApiError(err, `获取${url}数据出错`) 
    }
  }
}

/**
 * 执行POST请求
 */
export async function createData<T>(url: string, data: any): Promise<{ 
  data: T | null; 
  error: string | null 
}> {
  try {
    const response = await api.post<ApiResponse<T>>(url, data)
    if (response.data.success) {
      return { data: response.data.data, error: null }
    } else {
      return { 
        data: null, 
        error: response.data.message || `创建${url}数据失败` 
      }
    }
  } catch (err: any) {
    return { 
      data: null, 
      error: handleApiError(err, `创建${url}数据出错`) 
    }
  }
}

/**
 * 执行PUT请求
 */
export async function updateData<T>(url: string, data: any): Promise<{ 
  data: T | null; 
  error: string | null 
}> {
  try {
    const response = await api.put<ApiResponse<T>>(url, data)
    if (response.data.success) {
      return { data: response.data.data, error: null }
    } else {
      return { 
        data: null, 
        error: response.data.message || `更新${url}数据失败` 
      }
    }
  } catch (err: any) {
    return { 
      data: null, 
      error: handleApiError(err, `更新${url}数据出错`) 
    }
  }
}

/**
 * 执行DELETE请求
 */
export async function deleteData(url: string): Promise<{ 
  success: boolean; 
  error: string | null 
}> {
  try {
    const response = await api.delete<ApiResponse<null>>(url)
    if (response.data.success) {
      return { success: true, error: null }
    } else {
      return { 
        success: false, 
        error: response.data.message || `删除${url}数据失败` 
      }
    }
  } catch (err: any) {
    return { 
      success: false, 
      error: handleApiError(err, `删除${url}数据出错`) 
    }
  }
} 