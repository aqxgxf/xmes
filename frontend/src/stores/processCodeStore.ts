import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import type { ProcessCode, ProcessCodeForm, Product, PaginationParams, ProductCategory } from '../types/common'

export const useProcessCodeStore = defineStore('processCode', () => {
  // 状态
  const processCodes = ref<ProcessCode[]>([])
  const products = ref<Product[]>([])
  const categories = ref<ProductCategory[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)
  const submitting = ref(false)
  const search = ref('')

  // 过滤后的工艺流程代码列表
  const filteredProcessCodes = computed(() => {
    if (!search.value) return processCodes.value

    const searchTerm = search.value.toLowerCase()
    return processCodes.value.filter(pc =>
      (pc.code && pc.code.toLowerCase().includes(searchTerm)) ||
      (pc.description && pc.description.toLowerCase().includes(searchTerm)) ||
      (pc.version && pc.version.toLowerCase().includes(searchTerm))
    )
  })

  // 获取工艺流程代码列表
  const fetchProcessCodes = async () => {
    loading.value = true
    processCodes.value = []

    try {
      const params: PaginationParams = {
        page: currentPage.value,
        page_size: pageSize.value,
        search: search.value
      }

      const response = await api.get('/process-codes/', { params })

      // 处理API返回数据
      if (response.data && response.data.results) {
        processCodes.value = response.data.results
        total.value = response.data.count || 0
      } else if (Array.isArray(response.data)) {
        processCodes.value = response.data
        total.value = response.data.length
      } else {
        processCodes.value = []
        total.value = 0
      }
    } catch (error) {
      console.error('获取工艺流程代码列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取产品列表
  const fetchProducts = async () => {
    try {
      const params = {
        page_size: 999
      }

      const response = await api.get('/products/', { params })

      // 处理API返回数据
      if (response.data && response.data.results) {
        products.value = response.data.results
      } else if (Array.isArray(response.data)) {
        products.value = response.data
      } else {
        products.value = []
      }
    } catch (error) {
      console.error('获取产品列表失败:', error)
      throw error
    }
  }

  // 获取产品类列表
  const fetchCategories = async () => {
    try {
      const params = {
        page_size: 999
      }

      const response = await api.get('/product-categories/', { params })

      // 处理API返回数据
      if (response.data && response.data.results) {
        categories.value = response.data.results
      } else if (Array.isArray(response.data)) {
        categories.value = response.data
      } else {
        categories.value = []
      }
    } catch (error) {
      console.error('获取产品类列表失败:', error)
      throw error
    }
  }

  // 创建工艺流程代码
  const createProcessCode = async (formData: FormData) => {
    submitting.value = true
    try {
      const response = await api.post('/process-codes/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      // 获取新创建的记录ID
      let processCodeId = null
      if (response.data && response.data.id) {
        processCodeId = response.data.id
      } else if (response.data && response.data.data && response.data.data.id) {
        processCodeId = response.data.data.id
      }

      // 如果有产品ID，保存产品-工艺流程代码关系
      const productId = formData.get('product')
      if (productId && processCodeId) {
        await api.post('/product-process-codes/', {
          product: productId,
          process_code: processCodeId,
          is_default: true
        })
      }

      // 如果有产品类ID，保存产品类-工艺流程代码关系
      const categoryId = formData.get('category')
      if (categoryId && processCodeId) {
        await api.post('/category-process-codes/', {
          category: categoryId,
          process_code: processCodeId,
          is_default: true
        })
      }

      await fetchProcessCodes()
      return processCodeId
    } catch (error) {
      console.error('创建工艺流程代码失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 更新工艺流程代码
  const updateProcessCode = async (id: number, formData: FormData) => {
    submitting.value = true
    try {
      await api.patch(`/process-codes/${id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      // 如果有产品ID，保存产品-工艺流程代码关系
      const productId = formData.get('product')
      if (productId) {
        try {
          await api.post('/product-process-codes/', {
            product: productId,
            process_code: id,
            is_default: true
          })
        } catch (error) {
          console.error('保存产品-工艺流程代码关系失败:', error)
        }
      }

      // 如果有产品类ID，保存产品类-工艺流程代码关系
      const categoryId = formData.get('category')
      if (categoryId) {
        try {
          await api.post('/category-process-codes/', {
            category: categoryId,
            process_code: id,
            is_default: true
          })
        } catch (error) {
          console.error('保存产品类-工艺流程代码关系失败:', error)
        }
      }

      await fetchProcessCodes()
      return true
    } catch (error) {
      console.error('更新工艺流程代码失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 删除工艺流程代码
  const deleteProcessCode = async (id: number) => {
    loading.value = true
    try {
      await api.delete(`/process-codes/${id}/`)

      // 如果当前页删除后没有数据了，尝试跳到上一页
      if (processCodes.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }

      await fetchProcessCodes()
      return true
    } catch (error) {
      console.error('删除工艺流程代码失败:', error)
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

  // 分页处理
  const handleSizeChange = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    fetchProcessCodes()
  }

  const handleCurrentChange = (page: number) => {
    currentPage.value = page
    fetchProcessCodes()
  }

  // 初始化
  const initialize = async () => {
    await Promise.all([
      fetchProcessCodes(),
      fetchProducts(),
      fetchCategories()
    ])
  }

  return {
    // 状态
    processCodes,
    products,
    categories,
    total,
    currentPage,
    pageSize,
    loading,
    submitting,
    search,

    // 计算属性
    filteredProcessCodes,

    // 方法
    fetchProcessCodes,
    fetchProducts,
    fetchCategories,
    createProcessCode,
    updateProcessCode,
    deleteProcessCode,
    handleApiError,
    handleSizeChange,
    handleCurrentChange,
    initialize
  }
})
