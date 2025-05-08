/**
 * 全局错误处理工具
 */
import notification from './notification'

interface ErrorOptions {
  showNotification?: boolean;
  logToConsole?: boolean;
  defaultMessage?: string;
}

const defaultOptions: ErrorOptions = {
  showNotification: true,
  logToConsole: true,
  defaultMessage: '操作失败，请重试'
}

/**
 * 处理API错误或通用错误
 * @param error 错误对象
 * @param options 错误处理选项
 * @returns 处理后的错误消息
 */
export function handleError(error: any, options?: ErrorOptions): string {
  const mergedOptions = { ...defaultOptions, ...options }
  let errorMessage = mergedOptions.defaultMessage as string

  // 尝试提取错误消息
  if (error) {
    if (typeof error === 'string') {
      errorMessage = error
    } else if (error.message) {
      errorMessage = error.message
    } else if (error.response?.data?.message) {
      errorMessage = error.response.data.message
    }
  }

  // 记录到控制台
  if (mergedOptions.logToConsole) {
    console.error('Error:', error)
  }

  // 显示通知
  if (mergedOptions.showNotification) {
    notification.error(errorMessage)
  }

  return errorMessage
}

/**
 * 创建async/await错误处理包装函数
 * @param fn 要执行的异步函数
 * @param errorOptions 错误处理选项
 * @returns 带有错误处理的异步函数
 */
export function withErrorHandling<T extends any[], R>(
  fn: (...args: T) => Promise<R>,
  errorOptions?: ErrorOptions
): (...args: T) => Promise<R | null> {
  return async (...args: T): Promise<R | null> => {
    try {
      return await fn(...args)
    } catch (error) {
      handleError(error, errorOptions)
      return null
    }
  }
}

/**
 * 创建包含加载状态的异步函数
 * @param fn 要执行的异步函数
 * @param loadingRef 加载状态的ref对象
 * @param errorOptions 错误处理选项
 * @returns 带有加载状态和错误处理的异步函数
 */
export function withLoading<T extends any[], R>(
  fn: (...args: T) => Promise<R>,
  loadingRef: { value: boolean },
  errorOptions?: ErrorOptions
): (...args: T) => Promise<R | null> {
  return async (...args: T): Promise<R | null> => {
    loadingRef.value = true
    try {
      return await fn(...args)
    } catch (error) {
      handleError(error, errorOptions)
      return null
    } finally {
      loadingRef.value = false
    }
  }
}

export default {
  handleError,
  withErrorHandling,
  withLoading
} 