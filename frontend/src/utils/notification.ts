/**
 * 通知工具
 * 统一处理应用中的消息通知，使用 Element Plus 的 ElMessage 和 ElNotification
 */
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'

// 标准选项
const defaultDuration = 3000
const defaultShowClose = false
const defaultNotifyPosition = 'top-right'

/**
 * 显示普通消息
 */
export const toast = (message: string, type?: 'success' | 'warning' | 'info' | 'error', duration?: number) => {
  ElMessage({
    message,
    type,
    duration: duration || defaultDuration,
    showClose: defaultShowClose
  })
}

/**
 * 显示成功消息
 */
export const success = (message: string, duration?: number) => {
  toast(message, 'success', duration)
}

/**
 * 显示错误消息
 */
export const error = (message: string, duration?: number) => {
  toast(message, 'error', duration)
}

/**
 * 显示警告消息
 */
export const warning = (message: string, duration?: number) => {
  toast(message, 'warning', duration)
}

/**
 * 显示提示消息
 */
export const info = (message: string, duration?: number) => {
  toast(message, 'info', duration)
}

/**
 * 显示通知
 */
export const notify = (title: string, message: string, type: 'success' | 'warning' | 'info' | 'error' = 'info') => {
  ElNotification({
    title,
    message,
    type,
    duration: defaultDuration + 1500,
    position: defaultNotifyPosition
  })
}

/**
 * 确认对话框
 */
export const confirm = async (
  message: string, 
  title = '确认操作', 
  type: 'success' | 'warning' | 'info' | 'error' = 'warning'
): Promise<boolean> => {
  try {
    await ElMessageBox.confirm(
      message,
      title,
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type
      }
    )
    return true
  } catch (e) {
    return false
  }
}

/**
 * 警告确认对话框
 */
export const confirmWarning = async (message: string, title = '警告'): Promise<boolean> => {
  return await confirm(message, title, 'warning')
}

/**
 * 危险操作确认对话框
 */
export const confirmDanger = async (message: string, title = '危险操作'): Promise<boolean> => {
  return await confirm(message, title, 'error')
}

// 导出默认对象，方便使用
export default {
  toast,
  success,
  error,
  warning,
  info,
  notify,
  confirm,
  confirmWarning,
  confirmDanger
} 