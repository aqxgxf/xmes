import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ProductCategoryProcessCode } from '../types/common'
import api from '../api'

interface ProductCategoryProcessCodeForm {
  id?: number
  category: number
  process_code: number
  is_default: boolean
}

export const useCategoryProcessCodeStore = defineStore('categoryProcessCode', () => {
  // 状态
  const categoryProcessCodes = ref<ProductCategoryProcessCode[]>([])
  const categories = ref<any[]>([])
  const processCodes = ref<any[]>([])
  const loading = ref(false)
  const submitting = ref(false)
  const searchParams = ref({
    category: null as number | null,
    processCode: null as number | null,
  })

  // 获取产品类工艺关联列表
  const fetchCategoryProcessCodes = async () => {
    loading.value = true
    try {
      const queryParams = new URLSearchParams()
      if (searchParams.value.category) {
        queryParams.append('category', searchParams.value.category.toString())
      }
      if (searchParams.value.processCode) {
        queryParams.append('process_code', searchParams.value.processCode.toString())
      }

      const response = await api.get(`/category-process-codes/?${queryParams.toString()}`)
      categoryProcessCodes.value = response.data.results || response.data
      return categoryProcessCodes.value
    } catch (error) {
      console.error('获取产品类工艺关联列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取产品类列表
  const fetchCategories = async () => {
    try {
      const response = await api.get('/product-categories/')
      categories.value = response.data.results || response.data
      return categories.value
    } catch (error) {
      console.error('获取产品类列表失败:', error)
      throw error
    }
  }

  // 获取工艺流程代码列表
  const fetchProcessCodes = async () => {
    try {
      const response = await api.get('/process-codes/')
      processCodes.value = response.data.results || response.data
      return processCodes.value
    } catch (error) {
      console.error('获取工艺流程代码列表失败:', error)
      throw error
    }
  }

  // 创建产品类工艺关联
  const createCategoryProcessCode = async (data: ProductCategoryProcessCodeForm) => {
    submitting.value = true
    try {
      const response = await api.post('/category-process-codes/', data)
      await fetchCategoryProcessCodes()
      return response.data
    } catch (error) {
      console.error('创建产品类工艺关联失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 更新产品类工艺关联
  const updateCategoryProcessCode = async (id: number, data: ProductCategoryProcessCodeForm) => {
    submitting.value = true
    try {
      const response = await api.put(`/category-process-codes/${id}/`, data)
      await fetchCategoryProcessCodes()
      return response.data
    } catch (error) {
      console.error('更新产品类工艺关联失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 删除产品类工艺关联
  const deleteCategoryProcessCode = async (id: number) => {
    loading.value = true
    try {
      await api.delete(`/category-process-codes/${id}/`)
      await fetchCategoryProcessCodes()
      return true
    } catch (error) {
      console.error('删除产品类工艺关联失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 处理搜索
  const handleSearch = async () => {
    await fetchCategoryProcessCodes()
  }

  // 重置搜索
  const resetSearch = async () => {
    searchParams.value.category = null
    searchParams.value.processCode = null
    await fetchCategoryProcessCodes()
  }

  // 初始化
  const initialize = async () => {
    await Promise.all([
      fetchCategories(),
      fetchProcessCodes(),
      fetchCategoryProcessCodes()
    ])
  }

  return {
    categoryProcessCodes,
    categories,
    processCodes,
    loading,
    submitting,
    searchParams,
    fetchCategoryProcessCodes,
    fetchCategories,
    fetchProcessCodes,
    createCategoryProcessCode,
    updateCategoryProcessCode,
    deleteCategoryProcessCode,
    handleSearch,
    resetSearch,
    initialize
  }
}) 