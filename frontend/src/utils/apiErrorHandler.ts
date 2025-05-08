/**
 * API错误处理工具
 * 集中处理API请求中的各种错误类型，提供统一的错误处理方式
 */
import notification from './notification'
import { handleError } from './errorHandler'
import type { AxiosError } from 'axios'

/**
 * 错误代码与对应消息的映射
 */
interface ErrorMessages {
  [key: string]: string;
}

const ERROR_MESSAGES: ErrorMessages = {
  // 通用错误
  'default': '发生未知错误，请稍后重试',
  'network_error': '网络连接错误，请检查网络连接',
  'timeout': '请求超时，请稍后重试',
  'server_error': '服务器错误，请联系管理员',
  
  // HTTP状态错误
  '400': '请求参数有误',
  '401': '未授权，请重新登录',
  '403': '无权访问该资源',
  '404': '请求的资源不存在',
  '405': '不支持的请求方法',
  '408': '请求超时',
  '409': '资源冲突',
  '413': '请求实体过大',
  '429': '请求过于频繁，请稍后重试',
  '500': '服务器内部错误',
  '502': '网关错误',
  '503': '服务不可用',
  '504': '网关超时',
  
  // 业务错误
  'validation_error': '提交的数据未通过验证',
  'duplicate_key': '数据已存在',
  'foreign_key': '数据被其他记录引用，无法操作',
  'not_found': '请求的资源不存在'
}

interface ErrorDetail {
  message?: string;
  error?: string;
  detail?: string;
  [key: string]: any;
}

/**
 * 获取API错误的详细信息
 * @param error API错误对象
 * @returns 格式化的错误信息
 */
export function getApiErrorDetails(error: any): {
  code: string;
  message: string;
  status: number | null;
  details: any;
} {
  // 默认错误信息
  let code = 'default'
  let message = ERROR_MESSAGES.default
  let status: number | null = null
  let details = null
  
  if (error) {
    // 处理Axios错误
    if ('isAxiosError' in error && error.isAxiosError) {
      const axiosError = error as AxiosError
      
      // 获取HTTP状态码
      status = axiosError.response?.status || null
      
      // 网络错误
      if (axiosError.message.includes('Network Error')) {
        code = 'network_error'
        message = ERROR_MESSAGES.network_error
      } 
      // 超时错误
      else if (axiosError.message.includes('timeout')) {
        code = 'timeout'
        message = ERROR_MESSAGES.timeout
      } 
      // 有HTTP状态码的错误
      else if (status) {
        code = status.toString()
        message = ERROR_MESSAGES[code] || ERROR_MESSAGES.server_error
        details = axiosError.response?.data || null
        
        // 检查后端返回的详细错误信息
        if (details && typeof details === 'object') {
          const errorDetail = details as ErrorDetail
          if (errorDetail.message) {
            message = errorDetail.message
          } else if (errorDetail.error) {
            message = errorDetail.error
          } else if (errorDetail.detail) {
            message = errorDetail.detail
          }
        }
      }
    } 
    // 处理后端业务错误
    else if (error.code && typeof error.code === 'string') {
      code = error.code
      message = error.message || ERROR_MESSAGES[code] || ERROR_MESSAGES.default
      details = error.details || null
    }
    // 处理普通错误
    else if (error.message) {
      message = error.message
    } else if (typeof error === 'string') {
      message = error
    }
  }
  
  return { 
    code, 
    message, 
    status, 
    details 
  }
}

/**
 * 处理API错误并显示通知
 * @param error API错误对象
 * @param options 错误处理选项
 * @returns 格式化的错误信息
 */
export function handleApiError(
  error: any, 
  options: { 
    showNotification?: boolean; 
    logToConsole?: boolean;
    defaultMessage?: string;
    notificationType?: 'error' | 'warning' | 'info';
    notificationTitle?: string;
    notificationDuration?: number;
  } = {}
): { 
  code: string;
  message: string;
  status: number | null;
  details: any;
} {
  // 默认选项
  const defaultOptions = {
    showNotification: true,
    logToConsole: true,
    defaultMessage: ERROR_MESSAGES.default,
    notificationType: 'error' as const,
    notificationTitle: '请求错误',
    notificationDuration: 4500
  }
  
  const mergedOptions = { ...defaultOptions, ...options }
  
  // 获取错误详情
  const errorDetails = getApiErrorDetails(error)
  
  // 使用默认消息（如果提供）
  if (!errorDetails.message && mergedOptions.defaultMessage) {
    errorDetails.message = mergedOptions.defaultMessage
  }
  
  // 记录到控制台
  if (mergedOptions.logToConsole) {
    console.error(`API Error (${errorDetails.code}): ${errorDetails.message}`, error)
  }
  
  // 显示通知
  if (mergedOptions.showNotification) {
    if (mergedOptions.notificationType === 'error') {
      notification.error(errorDetails.message, mergedOptions.notificationDuration)
    } else if (mergedOptions.notificationType === 'warning') {
      notification.warning(errorDetails.message, mergedOptions.notificationDuration)
    } else {
      notification.info(errorDetails.message, mergedOptions.notificationDuration)
    }

    // 如果有标题，则使用 notify 方法
    if (mergedOptions.notificationTitle && mergedOptions.notificationTitle !== '请求错误') {
      notification.notify(
        mergedOptions.notificationTitle, 
        errorDetails.message, 
        mergedOptions.notificationType || 'error'
      )
    }
  }
  
  return errorDetails
}

/**
 * 创建用于处理API错误的高阶函数
 * @param fn 异步函数
 * @param options 错误处理选项
 * @returns 包装后的异步函数，自动处理API错误
 */
export function withApiErrorHandling<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  options: {
    showNotification?: boolean;
    logToConsole?: boolean;
    defaultMessage?: string;
    notificationType?: 'error' | 'warning' | 'info';
    rethrowError?: boolean;
  } = {}
): (...funcArgs: Parameters<T>) => Promise<Awaited<ReturnType<T>> | null> {
  // 默认选项
  const defaultOptions = {
    showNotification: true,
    logToConsole: true,
    defaultMessage: '操作失败，请重试',
    notificationType: 'error' as const,
    rethrowError: false
  }
  
  const mergedOptions = { ...defaultOptions, ...options }
  
  return async (...args: Parameters<T>): Promise<Awaited<ReturnType<T>> | null> => {
    try {
      return await fn(...args)
    } catch (error) {
      handleApiError(error, {
        showNotification: mergedOptions.showNotification,
        logToConsole: mergedOptions.logToConsole,
        defaultMessage: mergedOptions.defaultMessage,
        notificationType: mergedOptions.notificationType
      })
      
      if (mergedOptions.rethrowError) {
        throw error
      }
      
      return null
    }
  }
}

export default {
  getApiErrorDetails,
  handleApiError,
  withApiErrorHandling
} 