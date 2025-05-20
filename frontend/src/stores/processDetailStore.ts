import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import type { ProcessCode, ProcessDetail, Process, ProcessDetailForm } from '../types/common'

export const useProcessDetailStore = defineStore('processDetail', () => {
  // 状态
  const processDetails = ref<ProcessDetail[]>([])
  const processes = ref<Process[]>([])
  const processCode = ref<ProcessCode>({} as ProcessCode)
  const loading = ref(false)
  const submitting = ref(false)
  const codeId = ref<number | null>(null)

  // 排序后的工艺流程明细列表
  const sortedProcessDetails = computed(() => {
    return [...processDetails.value].sort((a, b) => a.step_no - b.step_no)
  })

  // 获取工艺流程代码信息
  const fetchProcessCode = async (id: number) => {
    if (!id || isNaN(id)) {
      console.error('获取工艺流程代码失败: 无效的ID');
      return null;
    }

    loading.value = true;
    codeId.value = id;

    try {
      const response = await api.get(`/process-codes/${id}/`);
      processCode.value = response.data;
      return processCode.value;
    } catch (error) {
      console.error('获取工艺流程代码失败:', error);
      processCode.value = {} as ProcessCode;
      throw error;
    } finally {
      loading.value = false;
    }
  }

  // 获取工艺流程明细列表
  const fetchProcessDetails = async (id: number) => {
    if (!id || isNaN(id)) {
      console.error('获取工艺流程明细失败: 无效的ID');
      processDetails.value = [];
      return [];
    }

    loading.value = true;
    codeId.value = id;
    processDetails.value = [];

    try {
      // 先获取工艺流程代码详情，拿到code和version
      const codeResp = await api.get(`/process-codes/${id}/`);
      const codeData = codeResp.data;
      if (!codeData.code || !codeData.version) {
        throw new Error('工艺流程代码信息不完整');
      }
      // 精确匹配
      const response = await api.get(`/process-details/`, {
        params: {
          process_code__code: codeData.code,
          process_code__version: codeData.version,
          page_size: 999
        }
      });
      if (response.data && response.data.results) {
        processDetails.value = response.data.results;
      } else if (Array.isArray(response.data)) {
        processDetails.value = response.data;
      } else {
        processDetails.value = [];
      }
      return processDetails.value;
    } catch (error: any) {
      console.error('获取工艺流程明细失败:', error);
      processDetails.value = [];
      if (error.response && error.response.status === 404) {
        console.info('工艺流程明细数据不存在，返回空数组');
        return [];
      }
      throw error;
    } finally {
      loading.value = false;
    }
  }

  // 获取工序列表
  const fetchProcesses = async () => {
    try {
      const params = {
        page_size: 999
      }

      const response = await api.get('/processes/', { params })

      if (response.data && response.data.results) {
        processes.value = response.data.results
      } else if (Array.isArray(response.data)) {
        processes.value = response.data
      } else {
        processes.value = []
      }

      return processes.value
    } catch (error) {
      console.error('获取工序列表失败:', error)
      throw error
    }
  }

  // 创建工艺流程明细
  const createProcessDetail = async (detail: ProcessDetailForm) => {
    submitting.value = true
    try {
      const response = await api.post('/process-details/', detail)
      await fetchProcessDetails(Number(codeId.value))
      return response.data
    } catch (error) {
      console.error('创建工艺流程明细失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 更新工艺流程明细
  const updateProcessDetail = async (id: number, detail: ProcessDetailForm) => {
    submitting.value = true
    try {
      const response = await api.put(`/process-details/${id}/`, detail)
      await fetchProcessDetails(Number(codeId.value))
      return response.data
    } catch (error) {
      console.error('更新工艺流程明细失败:', error)
      throw error
    } finally {
      submitting.value = false
    }
  }

  // 删除工艺流程明细
  const deleteProcessDetail = async (id: number) => {
    loading.value = true
    try {
      await api.delete(`/process-details/${id}/`)
      await fetchProcessDetails(Number(codeId.value))
      return true
    } catch (error) {
      console.error('删除工艺流程明细失败:', error)
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
  const initialize = async (id: number) => {
    if (!id || isNaN(id)) {
      console.error('初始化失败：无效的工艺流程代码ID');
      return;
    }

    codeId.value = id;
    try {
      // 先获取工艺流程代码信息
      await fetchProcessCode(id);

      // 然后尝试获取工艺流程明细，即使失败也继续
      try {
        await fetchProcessDetails(id);
      } catch (error) {
        console.error('获取工艺流程明细失败，但将继续初始化其他数据:', error);
        // 设置为空数组
        processDetails.value = [];
      }

      // 获取所有工序
      await fetchProcesses();
    } catch (error) {
      console.error('初始化失败：', error);
    }
  }

  return {
    // 状态
    processDetails,
    processes,
    processCode,
    loading,
    submitting,
    codeId,
    sortedProcessDetails,

    // 方法
    fetchProcessCode,
    fetchProcessDetails,
    fetchProcesses,
    createProcessDetail,
    updateProcessDetail,
    deleteProcessDetail,
    handleApiError,
    initialize
  }
})
