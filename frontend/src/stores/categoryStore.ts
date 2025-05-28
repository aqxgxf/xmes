import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'
import type { ProductCategory, ProductCategoryForm, PaginationParams, Company, Unit } from '../types/common'

export const useCategoryStore = defineStore('category', () => {
  // 状态
  const categories = ref<ProductCategory[]>([])
  const companies = ref<Company[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const loading = ref(false)
  const submitting = ref(false)
  const units = ref<Unit[]>([])

  // 搜索参数
  const searchQuery = ref('')
  const sortBy = ref<string>('')
  const sortOrder = ref<'ascending' | 'descending' | null>(null)

  // 获取产品类列表
  const fetchCategories = async (params?: PaginationParams) => {
    loading.value = true
    categories.value = []

    try {
      const queryParams: any = {
        page: params?.page || currentPage.value,
        page_size: params?.page_size || pageSize.value
      }

      if (searchQuery.value) {
        queryParams.search = searchQuery.value
      }

      // 添加排序参数
      if (sortBy.value) {
        queryParams.ordering = sortOrder.value === 'descending' ? `-${sortBy.value}` : sortBy.value
        console.log('排序参数:', queryParams.ordering)
      }

      console.log('API请求参数:', queryParams)
      const response = await api.get('/product-categories/', { params: queryParams })

      if (response.data.results) {
        categories.value = response.data.results
        total.value = response.data.count
      } else {
        categories.value = response.data
        total.value = response.data.length
      }

      // 更新页码和每页数量
      if (params?.page) currentPage.value = params.page
      if (params?.page_size) pageSize.value = params.page_size

      return categories.value
    } catch (error) {
      console.error('获取产品类列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取公司列表
  const fetchCompanies = async () => {
    try {
      const response = await api.get('/companies/', {
        params: { page_size: 1000 }
      })

      if (response.data.results) {
        companies.value = response.data.results
      } else {
        companies.value = response.data
      }

      return companies.value
    } catch (error) {
      console.error('获取公司列表失败:', error)
      throw error
    }
  }

  // 获取单位列表
  const fetchUnits = async () => {
    try {
      const res = await api.get('/units/', { params: { page_size: 999 } })
      if (res.data && Array.isArray(res.data.results)) {
        units.value = res.data.results
      } else if (Array.isArray(res.data)) {
        units.value = res.data
      }
      return units.value
    } catch (error) {
      console.error('获取单位列表失败:', error)
      throw error
    }
  }

  // 创建产品类
  const createCategory = async (data: ProductCategoryForm) => {
    submitting.value = true
    try {
      const formData = prepareFormData(data)
      const response = await api.post('/product-categories/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await fetchCategories()
      return response.data
    } catch (error) {
      console.error('创建产品类失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 更新产品类
  const updateCategory = async (id: number, data: ProductCategoryForm) => {
    submitting.value = true
    try {
      const formData = prepareFormData(data)
      const response = await api.patch(`/product-categories/${id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await fetchCategories()
      return response.data
    } catch (error) {
      console.error('更新产品类失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 准备表单数据
  const prepareFormData = (data: ProductCategoryForm | any) => {
    const formData = new FormData()
    formData.append('code', data.code || '')
    formData.append('display_name', data.display_name || '')

    // Use the already processed xxx_id fields from the payload
    if (data.company_id !== null && data.company_id !== undefined) {
      formData.append('company_id', String(data.company_id))
    } else {
      // If backend requires the field to be present even if null, uncomment next line
      // formData.append('company_id', ''); 
    }

    if (data.unit_id !== null && data.unit_id !== undefined) {
      formData.append('unit_id', String(data.unit_id))
    } else {
      // formData.append('unit_id', '');
    }

    if (data.material_type_id !== null && data.material_type_id !== undefined) {
      formData.append('material_type_id', String(data.material_type_id))
    } else {
      // formData.append('material_type_id', '');
    }

    // 添加图纸文件（如果存在且是 File 对象）
    if (data.drawing_pdf instanceof File) {
      formData.append('drawing_pdf', data.drawing_pdf)
    }

    // 添加工艺文件（如果存在且是 File 对象）
    if (data.process_pdf instanceof File) {
      formData.append('process_pdf', data.process_pdf)
    }

    return formData
  }

  // 删除产品类
  const deleteCategory = async (id: number) => {
    loading.value = true
    try {
      await api.delete(`/product-categories/${id}/`)
      
      // 计算删除后的总记录数和总页数
      const remainingItems = total.value - 1;
      const totalPages = Math.ceil(remainingItems / pageSize.value);
      
      // 如果当前页大于总页数，跳转到最后一页
      if (totalPages > 0 && currentPage.value > totalPages) {
        currentPage.value = totalPages;
      } else if (totalPages === 0) {
        // 如果没有记录了，则跳到第1页
        currentPage.value = 1;
      }
      
      // 获取更新后的数据
      await fetchCategories();
      
      return true
    } catch (error) {
      console.error('删除产品类失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 导入产品类
  const importCategories = async (file: File) => {
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      await api.post('/product-categories/import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await fetchCategories()
      return true
    } catch (error) {
      console.error('导入产品类失败:', error)
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
    fetchCategories()
  }

  // 设置排序
  const setSorting = (prop: string, order: 'ascending' | 'descending' | null) => {
    sortBy.value = prop
    sortOrder.value = order
    fetchCategories()
  }

  // 根据ID获取产品类名称
  const getCategoryName = (categoryId: number): string => {
    const category = categories.value.find(c => c.id === categoryId);
    return category ? `${category.code}-${category.display_name}` : '';
  }

  // 处理页面大小变化
  const handleSizeChange = (val: number) => {
    pageSize.value = val
    currentPage.value = 1
    fetchCategories()
  }

  // 处理页码变化
  const handleCurrentChange = (val: number) => {
    currentPage.value = val
    fetchCategories()
  }

  // 初始化
  const initialize = async () => {
    await Promise.all([
      fetchCompanies(),
      fetchUnits(),
      fetchCategories()
    ])
  }

  return {
    // 状态
    categories,
    companies,
    total,
    currentPage,
    pageSize,
    loading,
    submitting,
    searchQuery,
    sortBy,
    sortOrder,
    units,

    // 方法
    fetchCategories,
    fetchCompanies,
    fetchUnits,
    createCategory,
    updateCategory,
    deleteCategory,
    importCategories,
    handleApiError,
    setSearchQuery,
    setSorting,
    handleSizeChange,
    handleCurrentChange,
    initialize,
    getCategoryName
  }
})
