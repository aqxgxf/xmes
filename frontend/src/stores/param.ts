import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export interface CategoryParam {
  id: number;
  name: string;
  category: number;
}

export interface ParamForm {
  id: number | null;
  name: string;
  category: number | null;
}

export const useParamStore = defineStore('param', () => {
  // State
  const params = ref<CategoryParam[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const search = ref('')
  const selectedCategory = ref<number | null>(null)

  // Computed
  const filteredParams = computed(() => {
    if (!search.value) return params.value
    
    return params.value.filter(param => 
      param.name.toLowerCase().includes(search.value.toLowerCase())
    )
  })

  // Actions
  const fetchParams = async () => {
    if (!selectedCategory.value) {
      params.value = []
      total.value = 0
      return
    }
    
    loading.value = true
    error.value = null
    
    try {
      const reqParams = {
        page: currentPage.value,
        page_size: pageSize.value
      }
      
      const response = await api.get(`/product-categories/${selectedCategory.value}/params/`, { params: reqParams })
      
      if (response.data && response.data.results) {
        params.value = response.data.results
        total.value = response.data.count || 0
      } else if (Array.isArray(response.data)) {
        params.value = response.data
        total.value = response.data.length
      } else {
        params.value = []
        total.value = 0
      }
    } catch (err: any) {
      console.error(`获取产品类别${selectedCategory.value}的参数项失败:`, err)
      error.value = err.message || '获取参数项列表失败'
      params.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  const createParam = async (paramData: ParamForm) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/category-params/', paramData)
      await fetchParams()
      return { success: true, data: response.data }
    } catch (err: any) {
      console.error('创建参数项失败:', err)
      error.value = err.message || '创建参数项失败'
      return { 
        success: false, 
        error: err.response?.data || err.message || '创建参数项失败' 
      }
    } finally {
      loading.value = false
    }
  }

  const updateParam = async (id: number, paramData: ParamForm) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.put(`/category-params/${id}/`, paramData)
      await fetchParams()
      return { success: true, data: response.data }
    } catch (err: any) {
      console.error('更新参数项失败:', err)
      error.value = err.message || '更新参数项失败'
      return { 
        success: false, 
        error: err.response?.data || err.message || '更新参数项失败' 
      }
    } finally {
      loading.value = false
    }
  }

  const deleteParam = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      await api.delete(`/category-params/${id}/`)
      
      // 如果当前页删除后没有数据了且不是第一页，尝试跳到上一页
      if (params.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }
      
      await fetchParams()
      return { success: true }
    } catch (err: any) {
      console.error('删除参数项失败:', err)
      error.value = err.message || '删除参数项失败'
      return { 
        success: false, 
        error: err.response?.data || err.message || '删除参数项失败' 
      }
    } finally {
      loading.value = false
    }
  }

  const setCategory = (categoryId: number | null) => {
    selectedCategory.value = categoryId
    currentPage.value = 1
    search.value = ''
    if (categoryId) {
      fetchParams()
    } else {
      params.value = []
      total.value = 0
    }
  }

  const setPage = (page: number) => {
    currentPage.value = page
    fetchParams()
  }

  const setPageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    fetchParams()
  }

  const setSearch = (term: string) => {
    search.value = term
  }

  return {
    // State
    params,
    total,
    loading,
    error,
    currentPage,
    pageSize,
    search,
    selectedCategory,
    
    // Computed
    filteredParams,
    
    // Actions
    fetchParams,
    createParam,
    updateParam,
    deleteParam,
    setCategory,
    setPage,
    setPageSize,
    setSearch
  }
}) 