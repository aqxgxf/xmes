import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchData } from '../api/apiUtils'
import type { PaginationParams, ApiResponse, Product, Customer, Material, Company } from '../types/common'
import { withErrorHandling, withLoading } from '../utils/errorHandler'

// 供应商接口
export interface Supplier extends Company {
  email?: string;
}

export const useBasedataStore = defineStore('basedata', () => {
  // 状态
  const products = ref<Product[]>([])
  const customers = ref<Customer[]>([])
  const materials = ref<Material[]>([])
  const suppliers = ref<Supplier[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 获取所有基础数据
  const fetchAllBasedata = withLoading(async () => {
    error.value = null

    try {
      await Promise.all([
        fetchProducts(),
        fetchCustomers(),
        fetchMaterials(),
        fetchSuppliers()
      ])
    } catch (err: any) {
      error.value = err.message || '获取基础数据失败'
      console.error('获取基础数据错误:', err)
      throw err
    }
  }, isLoading)

  // 获取产品列表
  const fetchProducts = withErrorHandling(async (params?: PaginationParams) => {
    const result = await fetchData<Product[]>('/api/basedata/products/', params)
    if (result.data) {
      products.value = result.data
    } else if (result.error) {
      error.value = result.error
      throw new Error(result.error)
    }
    return result.data
  })

  // 获取客户列表
  const fetchCustomers = withErrorHandling(async (params?: PaginationParams) => {
    const result = await fetchData<Customer[]>('/api/basedata/customers/', params)
    if (result.data) {
      customers.value = result.data
    } else if (result.error) {
      error.value = result.error
      throw new Error(result.error)
    }
    return result.data
  })

  // 获取材料列表
  const fetchMaterials = withErrorHandling(async (params?: PaginationParams) => {
    const result = await fetchData<Material[]>('/api/basedata/materials/', params)
    if (result.data) {
      materials.value = result.data
    } else if (result.error) {
      error.value = result.error
      throw new Error(result.error)
    }
    return result.data
  })

  // 获取供应商列表
  const fetchSuppliers = withErrorHandling(async (params?: PaginationParams) => {
    const result = await fetchData<Supplier[]>('/api/basedata/suppliers/', params)
    if (result.data) {
      suppliers.value = result.data
    } else if (result.error) {
      error.value = result.error
      throw new Error(result.error)
    }
    return result.data
  })

  // 根据ID获取产品
  function getProductById(id: number): Product | undefined {
    return products.value.find(p => p.id === id)
  }

  // 根据ID获取客户
  function getCustomerById(id: number): Customer | undefined {
    return customers.value.find(c => c.id === id)
  }

  // 根据ID获取材料
  function getMaterialById(id: number): Material | undefined {
    return materials.value.find(m => m.id === id)
  }

  // 根据ID获取供应商
  function getSupplierById(id: number): Supplier | undefined {
    return suppliers.value.find(s => s.id === id)
  }

  // 清空错误
  function clearError() {
    error.value = null
  }

  // 重置状态
  function reset() {
    products.value = []
    customers.value = []
    materials.value = []
    suppliers.value = []
    isLoading.value = false
    error.value = null
  }

  return {
    // 状态
    products,
    customers,
    materials,
    suppliers,
    isLoading,
    error,
    
    // 方法
    fetchAllBasedata,
    fetchProducts,
    fetchCustomers,
    fetchMaterials,
    fetchSuppliers,
    getProductById,
    getCustomerById,
    getMaterialById,
    getSupplierById,
    clearError,
    reset
  }
}) 