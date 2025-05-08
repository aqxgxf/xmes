import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../api'
import { fetchData, createData, updateData, deleteData } from '../api/apiUtils'
import type { PaginationParams, ApiResponse, PaginatedResponse, StatusMapping, Product, Customer, Material } from '../types/common'
import { withErrorHandling, withLoading } from '../utils/errorHandler'

// 定义生产订单类型接口
export interface ProductionOrder {
  id: number;
  order_number: string;
  product_id: number;
  product_name?: string;
  customer_id: number;
  customer_name?: string;
  quantity: number;
  delivery_date: string | Date;
  status: string;
  status_display?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
  product_detail?: Product;
  customer_detail?: Customer;
  materials?: ProductionMaterial[];
  logs?: ProductionLog[];
  [key: string]: any;
}

// 定义材料类型接口
export interface ProductionMaterial {
  id?: number;
  order: number;
  material: number;
  material_name?: string;
  material_detail?: Material;
  specification?: string;
  quantity: number;
  unit: string;
  notes?: string;
}

// 定义日志类型接口
export interface ProductionLog {
  id?: number;
  order: number;
  title: string;
  content: string;
  log_type: string;
  operator?: number;
  operator_name?: string;
  created_at?: string;
}

// 订单状态映射
export const PRODUCTION_ORDER_STATUS: StatusMapping = {
  'draft': { label: '草稿', type: 'info' },
  'planned': { label: '已计划', type: 'warning' },
  'in_progress': { label: '生产中', type: 'primary' },
  'completed': { label: '已完成', type: 'success' },
  'cancelled': { label: '已取消', type: 'danger' }
}

export const useProductionStore = defineStore('production', () => {
  // 状态
  const productionOrders = ref<ProductionOrder[]>([])
  const currentOrder = ref<ProductionOrder | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)
  
  // 获取生产订单列表
  const fetchProductionOrders = withLoading(async (params?: PaginationParams) => {
    error.value = null

    try {
      const result = await fetchData<ProductionOrder[]>('/api/production/orders/', params)
      if (result.data) {
        productionOrders.value = result.data
        totalCount.value = result.count || result.data.length
      } else if (result.error) {
        error.value = result.error
        throw new Error(result.error)
      }
      return result.data
    } catch (err: any) {
      error.value = err.message || '获取生产订单失败'
      console.error('获取生产订单错误:', err)
      throw err
    }
  }, isLoading)

  // 获取订单详情
  const fetchOrderDetail = withLoading(async (id: number) => {
    error.value = null

    try {
      const result = await fetchData<ProductionOrder>(`/api/production/orders/${id}/`)
      if (result.data) {
        currentOrder.value = result.data
        return result.data
      } else if (result.error) {
        error.value = result.error
        throw new Error(result.error)
      }
      return null
    } catch (err: any) {
      error.value = err.message || '获取订单详情失败'
      console.error('获取订单详情错误:', err)
      throw err
    }
  }, isLoading)

  // 创建订单
  const createOrder = withLoading(async (order: Omit<ProductionOrder, 'id' | 'order_number'> & { id?: number }) => {
    error.value = null

    try {
      const result = await createData<ProductionOrder>('/api/production/orders/', order)
      if (result.data) {
        return result.data
      } else if (result.error) {
        error.value = result.error
        throw new Error(result.error)
      }
      return null
    } catch (err: any) {
      error.value = err.message || '创建订单失败'
      console.error('创建订单错误:', err)
      throw err
    }
  }, isLoading)

  // 更新订单
  const updateOrder = withLoading(async (id: number, order: Partial<ProductionOrder>) => {
    error.value = null

    try {
      const result = await updateData<ProductionOrder>(`/api/production/orders/${id}/`, order)
      if (result.data) {
        // 更新当前订单
        if (currentOrder.value && currentOrder.value.id === id) {
          currentOrder.value = result.data
        }
        // 更新列表中的订单
        const index = productionOrders.value.findIndex(item => item.id === id)
        if (index !== -1) {
          productionOrders.value[index] = result.data
        }
        return result.data
      } else if (result.error) {
        error.value = result.error
        throw new Error(result.error)
      }
      return null
    } catch (err: any) {
      error.value = err.message || '更新订单失败'
      console.error('更新订单错误:', err)
      throw err
    }
  }, isLoading)

  // 删除订单
  const deleteOrder = withLoading(async (id: number) => {
    error.value = null

    try {
      const result = await deleteData(`/api/production/orders/${id}/`)
      if (result.success) {
        // 从列表中移除订单
        productionOrders.value = productionOrders.value.filter(order => order.id !== id)
        // 如果当前订单是被删除的订单，则清空
        if (currentOrder.value && currentOrder.value.id === id) {
          currentOrder.value = null
        }
        return true
      } else if (result.error) {
        error.value = result.error
        throw new Error(result.error)
      }
      return false
    } catch (err: any) {
      error.value = err.message || '删除订单失败'
      console.error('删除订单错误:', err)
      throw err
    }
  }, isLoading)

  // 更新订单状态
  const updateOrderStatus = withLoading(async (id: number, status: string) => {
    error.value = null

    try {
      const response = await api.post<ApiResponse<ProductionOrder>>(`/api/production/orders/${id}/update_status/`, { status })
      if (response.data.success) {
        // 更新当前订单
        if (currentOrder.value && currentOrder.value.id === id) {
          currentOrder.value = response.data.data
        }
        // 更新列表中的订单
        const index = productionOrders.value.findIndex(item => item.id === id)
        if (index !== -1) {
          productionOrders.value[index] = response.data.data
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
    }
  }, isLoading)

  // 获取状态显示文本
  function getStatusLabel(status: string): string {
    return PRODUCTION_ORDER_STATUS[status]?.label || status
  }

  // 获取状态类型
  function getStatusType(status: string): string {
    return PRODUCTION_ORDER_STATUS[status]?.type || 'info'
  }

  // 根据ID获取订单
  function getOrderById(id: number): ProductionOrder | undefined {
    return productionOrders.value.find(order => order.id === id)
  }

  // 清空错误
  function clearError() {
    error.value = null
  }

  // 重置状态
  function reset() {
    productionOrders.value = []
    currentOrder.value = null
    isLoading.value = false
    error.value = null
    totalCount.value = 0
  }

  return {
    // 状态
    productionOrders,
    currentOrder,
    isLoading,
    error,
    totalCount,
    
    // 方法
    fetchProductionOrders,
    fetchOrderDetail,
    createOrder,
    updateOrder,
    deleteOrder,
    updateOrderStatus,
    getStatusLabel,
    getStatusType,
    getOrderById,
    clearError,
    reset
  }
}) 