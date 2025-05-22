import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import type { PaginationParams, ApiResponse, PaginatedResponse, StatusMapping } from '../types/common'

// 销售订单类型接口
export interface SalesOrder {
  id: number;
  order_no: string;
  customer_id: number;
  customer_name?: string;
  contact?: string;
  phone?: string;
  total_amount: number;
  order_date: string | Date;
  delivery_date: string | Date;
  status: string;
  status_display?: string;
  payment_status?: string;
  payment_method?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
  products?: SalesOrderProduct[];
  [key: string]: any;
}

// 销售订单产品接口
export interface SalesOrderProduct {
  id?: number;
  order_id: number;
  product_id: number;
  product_name?: string;
  quantity: number;
  unit_price: number;
  discount?: number;
  amount: number;
  notes?: string;
}

// 订单状态映射
export const SALES_ORDER_STATUS: StatusMapping = {
  'draft': { label: '草稿', type: 'info' },
  'confirmed': { label: '已确认', type: 'primary' },
  'shipped': { label: '已发货', type: 'warning' },
  'delivered': { label: '已送达', type: 'success' },
  'cancelled': { label: '已取消', type: 'danger' }
}

// 支付状态映射
export const PAYMENT_STATUS: StatusMapping = {
  'unpaid': { label: '未支付', type: 'danger' },
  'partial': { label: '部分支付', type: 'warning' },
  'paid': { label: '已支付', type: 'success' }
}

export const useSalesStore = defineStore('sales', () => {
  // 状态
  const salesOrders = ref<SalesOrder[]>([])
  const currentOrder = ref<SalesOrder | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)

  // 获取销售订单列表
  async function fetchSalesOrders(params?: PaginationParams) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get('/api/sales/orders/', { params })
      if (response.data.success) {
        salesOrders.value = response.data.data
        // 如果后端返回了总数，则更新总数
        if (response.data.count !== undefined) {
          totalCount.value = response.data.count
        } else {
          totalCount.value = salesOrders.value.length
        }
      } else {
        error.value = response.data.message || '获取销售订单失败'
      }
    } catch (err: any) {
      error.value = err.message || '获取销售订单时发生错误'
      console.error('获取销售订单错误:', err)
    } finally {
      isLoading.value = false
    }
  }

  // 获取订单详情
  async function fetchOrderDetail(id: number) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get<ApiResponse<SalesOrder>>(`/api/sales/orders/${id}/`)
      if (response.data.success) {
        currentOrder.value = response.data.data
      } else {
        error.value = response.data.message || '获取订单详情失败'
      }
    } catch (err: any) {
      error.value = err.message || '获取订单详情时发生错误'
      console.error('获取订单详情错误:', err)
    } finally {
      isLoading.value = false
    }
  }

  // 创建订单
  async function createOrder(order: Omit<SalesOrder, 'id' | 'order_no'> & { id?: number }) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.post<ApiResponse<SalesOrder>>('/api/sales/orders/', order)
      if (response.data.success) {
        return response.data.data
      } else {
        error.value = response.data.message || '创建订单失败'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '创建订单时发生错误'
      console.error('创建订单错误:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 更新订单
  async function updateOrder(id: number, order: Partial<SalesOrder>) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.put<ApiResponse<SalesOrder>>(`/api/sales/orders/${id}/`, order)
      if (response.data.success) {
        // 更新当前订单
        if (currentOrder.value && currentOrder.value.id === id) {
          currentOrder.value = response.data.data
        }
        // 更新列表中的订单
        const index = salesOrders.value.findIndex(item => item.id === id)
        if (index !== -1) {
          salesOrders.value[index] = response.data.data
        }
        return response.data.data
      } else {
        error.value = response.data.message || '更新订单失败'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '更新订单时发生错误'
      console.error('更新订单错误:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 删除订单
  async function deleteOrder(id: number) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.delete<ApiResponse<null>>(`/api/sales/orders/${id}/`)
      if (response.data.success) {
        // 从列表中移除订单
        salesOrders.value = salesOrders.value.filter(order => order.id !== id)
        // 如果当前订单是被删除的订单，则清空
        if (currentOrder.value && currentOrder.value.id === id) {
          currentOrder.value = null
        }
        return true
      } else {
        error.value = response.data.message || '删除订单失败'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '删除订单时发生错误'
      console.error('删除订单错误:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 更新订单状态
  async function updateOrderStatus(id: number, status: string) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.post<ApiResponse<SalesOrder>>(`/api/sales/orders/${id}/update_status/`, { status })
      if (response.data.success) {
        // 更新当前订单
        if (currentOrder.value && currentOrder.value.id === id) {
          currentOrder.value = response.data.data
        }
        // 更新列表中的订单
        const index = salesOrders.value.findIndex(item => item.id === id)
        if (index !== -1) {
          salesOrders.value[index] = response.data.data
        }
        return response.data.data
      } else {
        error.value = response.data.message || '更新订单状态失败'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '更新订单状态时发生错误'
      console.error('更新订单状态错误:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 获取状态显示文本
  function getStatusLabel(status: string): string {
    return SALES_ORDER_STATUS[status]?.label || status
  }

  // 获取状态类型
  function getStatusType(status: string): string {
    return SALES_ORDER_STATUS[status]?.type || 'info'
  }

  // 获取支付状态显示文本
  function getPaymentStatusLabel(status: string): string {
    return PAYMENT_STATUS[status]?.label || status
  }

  // 获取支付状态类型
  function getPaymentStatusType(status: string): string {
    return PAYMENT_STATUS[status]?.type || 'info'
  }

  // 清空错误
  function clearError() {
    error.value = null
  }

  // 重置状态
  function reset() {
    salesOrders.value = []
    currentOrder.value = null
    isLoading.value = false
    error.value = null
    totalCount.value = 0
  }

  return {
    // 状态
    salesOrders,
    currentOrder,
    isLoading,
    error,
    totalCount,
    
    // 方法
    fetchSalesOrders,
    fetchOrderDetail,
    createOrder,
    updateOrder,
    deleteOrder,
    updateOrderStatus,
    getStatusLabel,
    getStatusType,
    getPaymentStatusLabel,
    getPaymentStatusType,
    clearError,
    reset
  }
}) 