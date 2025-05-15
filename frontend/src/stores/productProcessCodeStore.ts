import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import type { ProductProcessCode, ProductProcessCodeForm, Product, ProcessCode, PaginationParams } from '../types/common'

export const useProductProcessCodeStore = defineStore('productProcessCode', () => {
  // 状态
  const productProcessCodes = ref<ProductProcessCode[]>([])
  const products = ref<Product[]>([])
  const processCodes = ref<ProcessCode[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const loading = ref(false)
  const submitting = ref(false)

  // 搜索参数
  const searchParams = ref({
    product: '',
    processCode: ''
  })

  // 获取产品工艺关联列表
  const fetchProductProcessCodes = async () => {
    loading.value = true
    productProcessCodes.value = []

    try {
      const params: any = {
        page: currentPage.value,
        page_size: pageSize.value
      }

      if (searchParams.value.product) {
        params.product = searchParams.value.product
      }

      if (searchParams.value.processCode) {
        params.process_code = searchParams.value.processCode
      }

      const response = await api.get('/product-process-codes/', { params })

      if (response.data.results) {
        productProcessCodes.value = response.data.results
        total.value = response.data.count
      } else {
        productProcessCodes.value = response.data
        total.value = response.data.length
      }

      return productProcessCodes.value
    } catch (error) {
      console.error('获取产品工艺关联失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取产品列表
  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/')
      products.value = response.data.results || response.data
      return products.value
    } catch (error) {
      console.error('获取产品列表失败:', error)
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

  // 创建产品工艺关联
  const createProductProcessCode = async (data: ProductProcessCodeForm) => {
    submitting.value = true
    try {
      const response = await api.post('/product-process-codes/', data)
      await fetchProductProcessCodes()
      return response.data
    } catch (error) {
      console.error('创建产品工艺关联失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 更新产品工艺关联
  const updateProductProcessCode = async (id: number, data: ProductProcessCodeForm) => {
    submitting.value = true
    try {
      const response = await api.put(`/product-process-codes/${id}/`, data)
      await fetchProductProcessCodes()
      return response.data
    } catch (error) {
      console.error('更新产品工艺关联失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 删除产品工艺关联
  const deleteProductProcessCode = async (id: number) => {
    loading.value = true
    try {
      await api.delete(`/product-process-codes/${id}/`)
      await fetchProductProcessCodes()
      return true
    } catch (error) {
      console.error('删除产品工艺关联失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 设置默认工艺流程
  const setAsDefault = async (id: number) => {
    loading.value = true
    try {
      await api.post(`/product-process-codes/${id}/set-default/`)
      await fetchProductProcessCodes()
      return true
    } catch (error) {
      console.error('设置默认工艺失败:', error)
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
      fetchProcessCodes(),
      fetchProductProcessCodes()
    ])
  }

  // 重置搜索参数
  const resetSearch = () => {
    searchParams.value.product = ''
    searchParams.value.processCode = ''
    currentPage.value = 1
    fetchProductProcessCodes()
  }

  // 处理搜索
  const handleSearch = () => {
    currentPage.value = 1
    fetchProductProcessCodes()
  }

  // 处理页面大小变化
  const handleSizeChange = (val: number) => {
    pageSize.value = val
    currentPage.value = 1
    fetchProductProcessCodes()
  }

  // 处理页码变化
  const handleCurrentChange = (val: number) => {
    currentPage.value = val
    fetchProductProcessCodes()
  }

  return {
    // 状态
    productProcessCodes,
    products,
    processCodes,
    total,
    currentPage,
    pageSize,
    loading,
    submitting,
    searchParams,

    // 方法
    fetchProductProcessCodes,
    fetchProducts,
    fetchProcessCodes,
    createProductProcessCode,
    updateProductProcessCode,
    deleteProductProcessCode,
    setAsDefault,
    handleApiError,
    initialize,
    resetSearch,
    handleSearch,
    handleSizeChange,
    handleCurrentChange
  }
})
