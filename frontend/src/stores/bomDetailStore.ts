import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import type { Bom, BomDetail, BomDetailForm, Product, PaginationParams } from '../types/common'

export const useBomDetailStore = defineStore('bomDetail', () => {
  // 状态
  const bomDetails = ref<BomDetail[]>([])
  const boms = ref<Bom[]>([])
  const materials = ref<Product[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const loading = ref(false)
  const submitting = ref(false)

  // 当前BOM筛选
  const searchBom = ref<number | null>(null)

  // 获取BOM明细列表
  const fetchBomDetails = async () => {
    loading.value = true
    bomDetails.value = []

    try {
      const params: any = {
        page: currentPage.value,
        page_size: pageSize.value
      }

      if (searchBom.value) {
        params.bom = searchBom.value
      }

      const response = await api.get('/bom-items/', { params })

      if (response.data.results) {
        bomDetails.value = response.data.results
        total.value = response.data.count
      } else {
        bomDetails.value = response.data
        total.value = response.data.length
      }

      return bomDetails.value
    } catch (error) {
      console.error('获取BOM明细列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取BOM列表
  const fetchBoms = async () => {
    try {
      const response = await api.get('/boms/', {
        params: { page_size: 1000 }
      })

      if (response.data.results) {
        boms.value = response.data.results
      } else {
        boms.value = response.data
      }

      return boms.value
    } catch (error) {
      console.error('获取BOM列表失败:', error)
      throw error
    }
  }

  // 获取物料列表
  const fetchMaterials = async () => {
    try {
      const response = await api.get('/materials/', {
        params: { page_size: 1000 }
      })

      if (response.data.results) {
        materials.value = response.data.results
      } else {
        materials.value = response.data
      }

      return materials.value
    } catch (error) {
      console.error('获取物料列表失败:', error)
      throw error
    }
  }

  // 创建BOM明细
  const createBomDetail = async (data: BomDetailForm) => {
    submitting.value = true
    try {
      const response = await api.post('/bom-items/', data)
      await fetchBomDetails()
      return response.data
    } catch (error) {
      console.error('创建BOM明细失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 更新BOM明细
  const updateBomDetail = async (id: number, data: BomDetailForm) => {
    submitting.value = true
    try {
      const response = await api.put(`/bom-items/${id}/`, data)
      await fetchBomDetails()
      return response.data
    } catch (error) {
      console.error('更新BOM明细失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 删除BOM明细
  const deleteBomDetail = async (id: number) => {
    loading.value = true
    try {
      await api.delete(`/bom-items/${id}/`)
      await fetchBomDetails()
      return true
    } catch (error) {
      console.error('删除BOM明细失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 导入BOM明细
  const importBomDetails = async (formData: FormData) => {
    loading.value = true
    try {
      const response = await api.post('/bom-items/import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await fetchBomDetails()
      return response.data
    } catch (error) {
      console.error('导入BOM明细失败:', error)
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
      fetchBoms(),
      fetchMaterials(),
      fetchBomDetails()
    ])
  }

  // 设置BOM筛选
  const setBomFilter = (bomId: number | null) => {
    searchBom.value = bomId
    currentPage.value = 1
    fetchBomDetails()
  }

  // 处理页面大小变化
  const handleSizeChange = (val: number) => {
    pageSize.value = val
    currentPage.value = 1
    fetchBomDetails()
  }

  // 处理页码变化
  const handleCurrentChange = (val: number) => {
    currentPage.value = val
    fetchBomDetails()
  }

  return {
    // 状态
    bomDetails,
    boms,
    materials,
    total,
    currentPage,
    pageSize,
    loading,
    submitting,
    searchBom,

    // 方法
    fetchBomDetails,
    fetchBoms,
    fetchMaterials,
    createBomDetail,
    updateBomDetail,
    deleteBomDetail,
    importBomDetails,
    handleApiError,
    initialize,
    setBomFilter,
    handleSizeChange,
    handleCurrentChange
  }
})
