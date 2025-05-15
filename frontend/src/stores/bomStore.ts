import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import type { Bom, BomForm, Product, PaginationParams } from '../types/common'

export const useBomStore = defineStore('bomStore', () => {
  // 状态
  const boms = ref<Bom[]>([])
  const products = ref<Product[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)
  const submitting = ref(false)

  // 搜索参数
  const searchQuery = ref('')

  // 版本选项
  const versionOptions = ['A', 'B', 'C', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2']

  // 获取BOM列表
  const fetchBoms = async (params?: PaginationParams) => {
    loading.value = true
    boms.value = []

    try {
      const queryParams: any = {
        page: params?.page || currentPage.value,
        page_size: params?.page_size || pageSize.value
      }

      if (searchQuery.value) {
        queryParams.search = searchQuery.value
      }

      const response = await api.get('/boms/', { params: queryParams })

      if (response.data.results) {
        boms.value = response.data.results
        total.value = response.data.count
      } else {
        boms.value = response.data
        total.value = response.data.length
      }

      // 更新页码和每页数量
      if (params?.page) currentPage.value = params.page
      if (params?.page_size) pageSize.value = params.page_size

      return boms.value
    } catch (error) {
      console.error('获取BOM列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取产品列表
  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/', {
        params: { is_material: false, page_size: 1000 }
      })

      if (response.data.results) {
        products.value = response.data.results
      } else {
        products.value = response.data
      }

      return products.value
    } catch (error) {
      console.error('获取产品列表失败:', error)
      throw error
    }
  }

  // 创建BOM
  const createBom = async (data: BomForm) => {
    submitting.value = true
    try {
      const response = await api.post('/boms/', data)
      await fetchBoms()
      return response.data
    } catch (error) {
      console.error('创建BOM失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 更新BOM
  const updateBom = async (id: number, data: BomForm) => {
    submitting.value = true
    try {
      const response = await api.patch(`/boms/${id}/`, data)
      await fetchBoms()
      return response.data
    } catch (error) {
      console.error('更新BOM失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 删除BOM
  const deleteBom = async (id: number) => {
    loading.value = true
    try {
      await api.delete(`/boms/${id}/`)
      await fetchBoms()
      return true
    } catch (error) {
      console.error('删除BOM失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // API 错误处理
  const handleApiError = (error: any, defaultMessage = '操作失败'): string => {
    let errorMsg = defaultMessage

    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (typeof error.response.data === 'object') {
        if (error.response.data.detail) {
          errorMsg = error.response.data.detail
        } else if (error.response.data.message) {
          errorMsg = error.response.data.message
        } else {
          // 尝试序列化所有错误信息
          try {
            const firstError = Object.values(error.response.data)[0]
            if (Array.isArray(firstError) && firstError.length > 0) {
              errorMsg = firstError[0] as string
            } else if (typeof firstError === 'string') {
              errorMsg = firstError
            } else {
              errorMsg = JSON.stringify(error.response.data)
            }
          } catch (e) {
            errorMsg = '请检查表单数据是否有误'
          }
        }
      }
    }

    return errorMsg
  }

  // 初始化
  const initialize = async () => {
    await Promise.all([
      fetchProducts(),
      fetchBoms()
    ])
  }

  // 设置搜索内容
  const setSearchQuery = (query: string) => {
    searchQuery.value = query
    currentPage.value = 1
    fetchBoms()
  }

  // 处理页面大小变化
  const handleSizeChange = (val: number) => {
    pageSize.value = val
    currentPage.value = 1
    fetchBoms()
  }

  // 处理页码变化
  const handleCurrentChange = (val: number) => {
    currentPage.value = val
    fetchBoms()
  }

  return {
    // 状态
    boms,
    products,
    total,
    currentPage,
    pageSize,
    loading,
    submitting,
    searchQuery,
    versionOptions,

    // 方法
    fetchBoms,
    fetchProducts,
    createBom,
    updateBom,
    deleteBom,
    handleApiError,
    initialize,
    setSearchQuery,
    handleSizeChange,
    handleCurrentChange
  }
})
