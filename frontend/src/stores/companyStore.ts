import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import type { Company, CompanyForm, PaginationParams } from '../types'

export const useCompanyStore = defineStore('company', () => {
  // 状态
  const companies = ref<Company[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const loading = ref(false)
  const submitting = ref(false)
  const search = ref('')
  const error = ref<string | null>(null)

  // 计算属性：过滤后的公司列表
  const filteredCompanies = computed(() => {
    if (!search.value) return companies.value

    const searchTerm = search.value.toLowerCase()
    return companies.value.filter(company =>
      (company.name && company.name.toLowerCase().includes(searchTerm)) ||
      (company.code && company.code.toLowerCase().includes(searchTerm)) ||
      (company.contact && company.contact.toLowerCase().includes(searchTerm))
    )
  })

  // 获取公司列表
  const fetchCompanies = async () => {
    loading.value = true
    error.value = null
    companies.value = []

    try {
      const params: PaginationParams = {
        page: currentPage.value,
        page_size: pageSize.value,
        search: search.value
      }

      const response = await api.get('/companies/', { params })

      // 处理API返回数据
      if (response.data && response.data.results) {
        companies.value = response.data.results
        total.value = response.data.count || 0
      } else if (Array.isArray(response.data)) {
        companies.value = response.data
        total.value = response.data.length
      } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        companies.value = response.data.data
        total.value = response.data.data.length
      } else {
        companies.value = []
        total.value = 0
      }
    } catch (err: any) {
      console.error('获取公司列表失败:', err)
      error.value = err.message || '获取公司列表失败'
      companies.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  // 创建公司
  const createCompany = async (companyData: CompanyForm) => {
    submitting.value = true
    try {
      const response = await api.post('/companies/', companyData)
      await fetchCompanies()
      return { success: true, data: response.data }
    } catch (err: any) {
      console.error('创建公司失败:', err)
      return {
        success: false,
        error: err.response?.data || err.message || '创建公司失败'
      }
    } finally {
      submitting.value = false
    }
  }

  // 更新公司
  const updateCompany = async (id: number, companyData: CompanyForm) => {
    submitting.value = true
    try {
      const response = await api.put(`/companies/${id}/`, companyData)
      await fetchCompanies()
      return { success: true, data: response.data }
    } catch (err: any) {
      console.error('更新公司失败:', err)
      return {
        success: false,
        error: err.response?.data || err.message || '更新公司失败'
      }
    } finally {
      submitting.value = false
    }
  }

  // 删除公司
  const deleteCompany = async (id: number) => {
    loading.value = true
    try {
      await api.delete(`/companies/${id}/`)

      // 如果当前页删除后没有数据了且不是第一页，尝试跳到上一页
      if (companies.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }

      await fetchCompanies()
      return { success: true }
    } catch (err: any) {
      console.error('删除公司失败:', err)
      return {
        success: false,
        error: err.response?.data || err.message || '删除公司失败'
      }
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
    fetchCompanies()
  }

  const handleCurrentChange = (page: number) => {
    currentPage.value = page
    fetchCompanies()
  }

  // 设置搜索内容
  const setSearch = (term: string) => {
    search.value = term
    currentPage.value = 1
  }

  // 设置页码
  const setPage = (page: number) => {
    currentPage.value = page
  }

  // 设置每页数量
  const setPageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
  }

  // 初始化
  const initialize = async () => {
    await fetchCompanies()
  }

  return {
    // 状态
    companies,
    total,
    currentPage,
    pageSize,
    loading,
    submitting,
    search,
    error,
    filteredCompanies,

    // 方法
    fetchCompanies,
    createCompany,
    updateCompany,
    deleteCompany,
    handleApiError,
    handleSizeChange,
    handleCurrentChange,
    setSearch,
    setPage,
    setPageSize,
    initialize
  }
})
