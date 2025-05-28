import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import type { MaterialType, MaterialForm, Category, Param, Unit, PaginationParams } from '../types/common'

export const useMaterialStore = defineStore('material', () => {
  // 状态
  const materials = ref<MaterialType[]>([])
  const categories = ref<Category[]>([])
  const params = ref<Param[]>([])
  const units = ref<Unit[]>([])

  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)
  const loading = ref(false)
  const submitting = ref(false)

  // 搜索参数
  const searchQuery = ref('')

  // 获取物料列表
  const fetchMaterials = async (params?: PaginationParams) => {
    loading.value = true
    materials.value = []

    try {
      const queryParams: any = {
        page: params?.page || currentPage.value,
        page_size: params?.page_size || pageSize.value
      }

      if (searchQuery.value) {
        queryParams.search = searchQuery.value
      }

      const response = await api.get('/materials/', { params: queryParams })

      if (response.data.results) {
        materials.value = response.data.results
        total.value = response.data.count
      } else {
        materials.value = response.data
        total.value = response.data.length
      }

      // 更新页码和每页数量
      if (params?.page) currentPage.value = params.page
      if (params?.page_size) pageSize.value = params.page_size

      return materials.value
    } catch (error) {
      console.error('获取物料列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取类别列表
  const fetchCategories = async () => {
    try {
      const response = await api.get('/product-categories/', {
        params: { page_size: 999 }
      })

      if (response.data && Array.isArray(response.data.results)) {
        categories.value = response.data.results
      } else if (Array.isArray(response.data)) {
        categories.value = response.data
      }

      return categories.value
    } catch (error) {
      console.error('获取物料类别失败:', error)
      throw error
    }
  }

  // 获取类别参数
  const fetchCategoryParams = async (categoryId: number) => {
    try {
      const response = await api.get(`/product-categories/${categoryId}/params/`)

      if (response.data && response.data.results) {
        params.value = response.data.results
      } else if (Array.isArray(response.data)) {
        params.value = response.data
      } else {
        params.value = []
      }

      return params.value
    } catch (error) {
      console.error('获取类别参数失败:', error)
      params.value = []
      throw error
    }
  }

  // 获取单位列表
  const fetchUnits = async () => {
    try {
      const response = await api.get('/units/', {
        params: { page_size: 999 }
      })

      if (response.data && Array.isArray(response.data.results)) {
        units.value = response.data.results
      } else if (Array.isArray(response.data)) {
        units.value = response.data
      }

      return units.value
    } catch (error) {
      console.error('获取单位列表失败:', error)
      throw error
    }
  }

  // 创建物料
  const createMaterial = async (data: MaterialForm) => {
    submitting.value = true
    try {
      const formData = prepareFormData(data)
      const response = await api.post('/products/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await fetchMaterials()
      return response.data
    } catch (error) {
      console.error('创建物料失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 更新物料
  const updateMaterial = async (id: number, data: MaterialForm) => {
    submitting.value = true
    try {
      const formData = prepareFormData(data)

      // 先尝试使用materials API端点
      try {
        const response = await api.patch(`/materials/${id}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        await fetchMaterials()
        return response.data
      } catch (materialError) {
        // 如果materials API失败，尝试products API
        console.warn('通过materials API更新失败，尝试使用products API:', materialError)
        const response = await api.patch(`/products/${id}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        await fetchMaterials()
        return response.data
      }
    } catch (error: any) {
      console.error('更新物料失败:', error)
      // 提供更详细的错误信息
      if (error.response?.data?.error) {
        console.error('API返回的错误详情:', error.response.data.error)
      }
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 准备表单数据
  const prepareFormData = (data: MaterialForm) => {
    const formData = new FormData()
    formData.append('code', data.code)
    formData.append('name', data.name)
    formData.append('price', String(data.price))
    formData.append('category', String(data.category || ''))
    formData.append('is_material', 'true')

    // 添加单位（如果存在）
    if (data.unit !== null) {
      formData.append('unit', String(data.unit))
    }

    // 添加图纸文件（如果存在）
    if (data.drawing_pdf instanceof File) {
      formData.append('drawing_pdf', data.drawing_pdf)
    }

    // 添加参数值
    if (data.paramValues && Object.keys(data.paramValues).length > 0) {
      const paramValues = Object.entries(data.paramValues)
        .filter(([, value]) => typeof value === 'string' && value.trim() !== '')
        .map(([paramId, value]) => ({
          param: parseInt(paramId),
          value: typeof value === 'string' ? value.trim() : ''
        }))

      if (paramValues.length > 0) {
        formData.append('param_values', JSON.stringify(paramValues))
      }
    }

    return formData
  }

  // 删除物料
  const deleteMaterial = async (id: number) => {
    loading.value = true
    try {
      // 先尝试使用物料API端点
      try {
        await api.delete(`/materials/${id}/`)
        await fetchMaterials()
        return true
      } catch (materialError) {
        // 如果物料API失败，尝试使用产品API端点作为回退方案
        console.warn('通过materials API删除失败，尝试使用products API:', materialError)
        await api.delete(`/products/${id}/`)
        await fetchMaterials()
        return true
      }
    } catch (error) {
      console.error('删除物料失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 导入物料
  const importMaterial = async (file: File) => {
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      await api.post('/products/import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await fetchMaterials()
      return true
    } catch (error) {
      console.error('导入物料失败:', error)
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

  // 设置搜索内容
  const setSearchQuery = (query: string) => {
    searchQuery.value = query
    currentPage.value = 1
    fetchMaterials()
  }

  // 处理页面大小变化
  const handleSizeChange = (val: number) => {
    pageSize.value = val
    currentPage.value = 1
    fetchMaterials()
  }

  // 处理页码变化
  const handleCurrentChange = (val: number) => {
    currentPage.value = val
    fetchMaterials()
  }

  // 初始化
  const initialize = async () => {
    await Promise.all([
      fetchCategories(),
      fetchUnits(),
      fetchMaterials()
    ])
  }

  // 材质类型状态
  const materialTypes = ref<MaterialType[]>([])

  // 获取材质类型列表
  const fetchMaterialTypes = async () => {
    loading.value = true
    try {
      const response = await api.get('/material-types/', { params: { page_size: 999 } })
      if (response.data && Array.isArray(response.data.results)) {
        materialTypes.value = response.data.results
      } else if (Array.isArray(response.data)) {
        materialTypes.value = response.data
      }
      return materialTypes.value
    } catch (error) {
      console.error('获取材质类型失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    materials,
    categories,
    params,
    units,
    materialTypes, // 新增
    currentPage,
    pageSize,
    total,
    loading,
    submitting,
    searchQuery,

    // 方法
    fetchMaterials,
    fetchCategories,
    fetchCategoryParams,
    fetchUnits,
    fetchMaterialTypes, // 新增
    createMaterial,
    updateMaterial,
    deleteMaterial,
    importMaterial,
    handleApiError,
    setSearchQuery,
    handleSizeChange,
    handleCurrentChange,
    initialize
  }
})
