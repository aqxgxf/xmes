import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import type { Process, ProcessForm, PaginationParams } from '../types/common'

export const useProcessStore = defineStore('process', () => {
  // 状态
  const processes = ref<Process[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const loading = ref(false)
  const submitting = ref(false)
  const search = ref('')

  // 过滤后的工序列表
  const filteredProcesses = computed(() => {
    if (!search.value) return processes.value

    const searchTerm = search.value.toLowerCase()
    return processes.value.filter(p =>
      (p.name && p.name.toLowerCase().includes(searchTerm)) ||
      (p.code && p.code.toLowerCase().includes(searchTerm))
    )
  })

  // 获取工序列表
  const fetchProcesses = async () => {
    loading.value = true
    processes.value = []

    try {
      const params: PaginationParams = {
        page: currentPage.value,
        page_size: pageSize.value
      }

      const response = await api.get('/processes/', { params })

      // 处理API返回数据
      if (response.data && response.data.results) {
        processes.value = response.data.results
        total.value = response.data.count || 0
      } else if (Array.isArray(response.data)) {
        processes.value = response.data
        total.value = response.data.length
      } else {
        processes.value = []
        total.value = 0
      }
    } catch (error) {
      console.error('获取工序列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建工序
  const createProcess = async (processData: ProcessForm) => {
    submitting.value = true
    try {
      await api.post('/processes/', processData)
      await fetchProcesses()
      return true
    } catch (error) {
      console.error('创建工序失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 更新工序
  const updateProcess = async (id: number, processData: ProcessForm) => {
    submitting.value = true
    try {
      await api.put(`/processes/${id}/`, processData)
      await fetchProcesses()
      return true
    } catch (error) {
      console.error('更新工序失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 删除工序
  const deleteProcess = async (id: number) => {
    loading.value = true
    try {
      await api.delete(`/processes/${id}/`)

      // 如果当前页删除后没有数据了，尝试跳到上一页
      if (processes.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }

      await fetchProcesses()
      return true
    } catch (error) {
      console.error('删除工序失败:', error)
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
          const firstError = Object.values(error.response.data)[0]
          if (Array.isArray(firstError) && firstError.length > 0) {
            errorMsg = firstError[0] as string
          } else if (typeof firstError === 'string') {
            errorMsg = firstError
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
    fetchProcesses()
  }

  const handleCurrentChange = (page: number) => {
    currentPage.value = page
    fetchProcesses()
  }

  // 初始化
  const initialize = () => {
    fetchProcesses()
  }

  return {
    // 状态
    processes,
    total,
    currentPage,
    pageSize,
    loading,
    submitting,
    search,
    filteredProcesses,

    // 方法
    fetchProcesses,
    createProcess,
    updateProcess,
    deleteProcess,
    handleApiError,
    handleSizeChange,
    handleCurrentChange,
    initialize
  }
})
