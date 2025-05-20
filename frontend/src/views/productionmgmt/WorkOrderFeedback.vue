<template>
  <div class="workorder-feedback-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工单回冲</h2>
        </div>
      </template>

      <!-- 工单搜索 -->
      <div class="search-section">
        <el-form :inline="true" class="search-form" @submit.prevent="searchWorkOrder">
          <el-form-item label="工单号">
            <el-input
              v-model="searchWorkOrderNo"
              placeholder="请输入工单号"
              clearable
              @keyup.enter.prevent="searchWorkOrder"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="searching" @click.prevent="searchWorkOrder">
              <el-icon><Search /></el-icon> 查询
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 工单信息 -->
      <div v-if="currentWorkOrder.id" class="workorder-info-container">
        <el-descriptions title="工单信息" :column="3" border>
          <el-descriptions-item label="工单号">{{ currentWorkOrder.workorder_no }}</el-descriptions-item>
          <el-descriptions-item label="产品">{{ getProductDisplay(currentWorkOrder) }}</el-descriptions-item>
          <el-descriptions-item label="数量">{{ currentWorkOrder.quantity }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentWorkOrder.status)">
              {{ getStatusText(currentWorkOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="工艺流程">{{ currentWorkOrder.process_code_text }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ currentWorkOrder.remark || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- 显示错误信息 -->
        <div v-if="loadError" class="error-message">
          <el-alert :title="loadError" type="error" :closable="false" show-icon />
        </div>
        
        <!-- 当前工序信息 -->
        <div class="current-process-container" v-if="!loadError || loadError.indexOf('未开始生产') !== -1">
          <h3>当前工序信息</h3>
          <el-alert v-if="!currentProcess" type="warning" show-icon>
            {{ loadError || '该工单尚未开始生产或已完成所有工序' }}
          </el-alert>
          <el-descriptions v-else :column="2" border class="current-process-info">
            <el-descriptions-item label="工序号">{{ currentProcess.step_no }}</el-descriptions-item>
            <el-descriptions-item label="工序名称">{{ currentProcess.process_name }}</el-descriptions-item>
            <el-descriptions-item label="工序内容">{{ currentProcess.process_content || '-' }}</el-descriptions-item>
            <el-descriptions-item label="待加工数量">{{ currentProcess.pending_quantity }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 回冲信息表单 -->
        <div v-if="currentProcess && (currentWorkOrder.status === 'in_progress' || currentWorkOrder.status === 'released')" class="feedback-form-container">
          <h3>回冲信息</h3>
          <el-form
            ref="feedbackFormRef"
            :model="feedbackForm"
            :rules="feedbackRules"
            label-width="100px"
            label-position="right"
            class="feedback-form"
            @submit.prevent
          >
            <el-form-item label="成品数量" prop="completedQuantity">
              <el-input-number
                v-model="feedbackForm.completedQuantity"
                :min="0"
                :max="Number(currentProcess.pending_quantity)"
                :precision="2"
                class="form-input"
              />
            </el-form-item>
            <el-form-item label="不良品数量" prop="defectiveQuantity">
              <el-input-number
                v-model="feedbackForm.defectiveQuantity"
                :min="0"
                :max="Number(currentProcess.pending_quantity)"
                :precision="2"
                class="form-input"
              />
            </el-form-item>
            <el-form-item label="不良原因" prop="defectiveReason" v-if="feedbackForm.defectiveQuantity > 0">
              <el-input
                v-model="feedbackForm.defectiveReason"
                type="textarea"
                :rows="3"
                placeholder="请输入不良原因"
                class="form-input"
              />
            </el-form-item>
            <el-form-item label="备注" prop="remark">
              <el-input
                v-model="feedbackForm.remark"
                type="textarea"
                :rows="2"
                placeholder="可选"
                class="form-input"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="submitting" @click.prevent="submitFeedback">提交回冲信息</el-button>
              <el-button @click.prevent="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'
import type { WorkOrder, ProcessDetailType, FeedbackForm, FormInstance } from '../../types/index'

// 状态定义
const searchWorkOrderNo = ref('')
const searching = ref(false)
const submitting = ref(false)
const currentWorkOrder = ref<WorkOrder>({} as WorkOrder)
const currentProcess = ref<ProcessDetailType | null>(null)
const feedbackFormRef = ref<FormInstance>()
const loadError = ref<string>('') // 添加错误信息状态

// 表单定义
const feedbackForm = reactive<FeedbackForm>({
  completedQuantity: 0,
  defectiveQuantity: 0,
  defectiveReason: '',
  remark: ''
})

// 表单校验规则
const feedbackRules = {
  completedQuantity: [
    { required: true, message: '请输入成品数量', trigger: 'blur' },
    { 
      validator: (rule: any, value: number, callback: any) => {
        const total = feedbackForm.completedQuantity + feedbackForm.defectiveQuantity
        if (currentProcess.value && total > Number(currentProcess.value.pending_quantity)) {
          callback(new Error(`成品数量和不良品数量之和不能超过待加工数量 ${currentProcess.value.pending_quantity}`))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  defectiveQuantity: [
    { required: true, message: '请输入不良品数量', trigger: 'blur' },
    { 
      validator: (rule: any, value: number, callback: any) => {
        const total = feedbackForm.completedQuantity + feedbackForm.defectiveQuantity
        if (currentProcess.value && total > Number(currentProcess.value.pending_quantity)) {
          callback(new Error(`成品数量和不良品数量之和不能超过待加工数量 ${currentProcess.value.pending_quantity}`))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  defectiveReason: [
    { 
      required: true, 
      message: '存在不良品时必须填写不良原因', 
      trigger: 'blur',
      validator: (rule: any, value: string, callback: any) => {
        if (feedbackForm.defectiveQuantity > 0 && !value) {
          callback(new Error('存在不良品时必须填写不良原因'))
        } else {
          callback()
        }
      }
    }
  ]
}

// 计算属性
const totalQuantity = computed(() => {
  return feedbackForm.completedQuantity + feedbackForm.defectiveQuantity
})

// 搜索工单
const searchWorkOrder = async () => {
  if (!searchWorkOrderNo.value) {
    ElMessage.warning('请输入工单号')
    return
  }

  searching.value = true
  loadError.value = '' // 重置错误信息
  
  try {
    console.log('开始搜索工单:', searchWorkOrderNo.value)
    // 获取工单基本信息 - 修改为精确匹配
    const workorderRes = await axios.get(`/api/workorders/`, {
      params: { workorder_no: searchWorkOrderNo.value }
    })
    
    console.log('工单搜索结果:', workorderRes.data)
    
    if (!workorderRes.data.results || workorderRes.data.results.length === 0) {
      loadError.value = '未找到该工单号'
      ElMessage.error(loadError.value)
      resetWorkOrderInfo()
      return
    }

    // 从结果中找出精确匹配的工单
    const exactMatch = workorderRes.data.results.find(
      (workorder: any) => workorder.workorder_no === searchWorkOrderNo.value
    )

    if (!exactMatch) {
      loadError.value = '未找到该工单号'
      ElMessage.error(loadError.value)
      resetWorkOrderInfo()
      return
    }

    // 设置当前工单
    currentWorkOrder.value = exactMatch
    console.log('找到工单:', currentWorkOrder.value.workorder_no, currentWorkOrder.value.id)
    
    // 检查工单状态是否允许回冲
    if (currentWorkOrder.value.status !== 'in_progress' && currentWorkOrder.value.status !== 'released') {
      loadError.value = '只有已下达或生产中的工单才能回冲'
      ElMessage.warning(loadError.value)
      // 继续显示工单信息，但不允许操作
    }
    
    // 获取当前工序信息
    console.log('开始查询当前工序, 工单ID:', currentWorkOrder.value.id)
    try {
      const processDetailsRes = await axios.get(`/api/workorder-process-details/`, {
        params: { workorder: currentWorkOrder.value.id, current: true }
      })
      
      console.log('当前工序查询结果:', processDetailsRes.data)
      
      // 修改判断逻辑，处理不同的响应格式
      if (processDetailsRes.data && (
          (Array.isArray(processDetailsRes.data) && processDetailsRes.data.length > 0) || 
          (processDetailsRes.data.results && processDetailsRes.data.results.length > 0)
        )) {
        // 根据响应格式获取第一个工序
        const processData = Array.isArray(processDetailsRes.data) 
          ? processDetailsRes.data[0] 
          : processDetailsRes.data.results[0]
          
        currentProcess.value = processData
        
        // 确保待加工数量是数字类型
        if (currentProcess.value && typeof currentProcess.value.pending_quantity === 'string') {
          currentProcess.value.pending_quantity = parseFloat(currentProcess.value.pending_quantity)
        }
        
        if (currentProcess.value) {
          console.log('找到当前工序:', currentProcess.value.step_no, currentProcess.value.process_name)
        }
        
        // 初始化表单
        feedbackForm.completedQuantity = 0
        feedbackForm.defectiveQuantity = 0
        feedbackForm.defectiveReason = ''
        feedbackForm.remark = ''
      } else {
        currentProcess.value = null
        console.log('未找到当前工序')
        loadError.value = '该工单尚未开始生产或已完成所有工序'
        ElMessage.info(loadError.value)
      }
    } catch (processError: any) {
      console.error('获取工序信息失败:', processError)
      loadError.value = processError.response?.data?.detail || '获取工序信息失败'
      ElMessage.error(loadError.value)
      // 即使获取工序失败，仍保留工单信息
    }
  } catch (error: any) {
    console.error('工单搜索失败:', error)
    console.error('错误详情:', error.response?.data)
    loadError.value = error.response?.data?.detail || '工单搜索失败'
    ElMessage.error(loadError.value)
    resetWorkOrderInfo()
  } finally {
    searching.value = false
  }
}

// 重置工单信息
const resetWorkOrderInfo = () => {
  currentWorkOrder.value = {} as WorkOrder
  currentProcess.value = null
  feedbackForm.completedQuantity = 0
  feedbackForm.defectiveQuantity = 0
  feedbackForm.defectiveReason = ''
  feedbackForm.remark = ''
  // 不在这里重置错误信息，因为需要显示错误给用户
}

// 重置搜索
const resetSearch = () => {
  searchWorkOrderNo.value = ''
  resetWorkOrderInfo()
  loadError.value = '' // 清除错误信息
}

// 重置表单
const resetForm = () => {
  feedbackFormRef.value?.resetFields()
}

// 提交回冲信息
const submitFeedback = async () => {
  if (!currentProcess.value || !currentWorkOrder.value.id) {
    ElMessage.warning('无有效工序信息')
    return
  }

  // 检查工单状态
  if (currentWorkOrder.value.status !== 'in_progress' && currentWorkOrder.value.status !== 'released') {
    ElMessage.warning('只有已下达或生产中的工单才能回冲')
    return
  }

  // 校验表单
  if (!feedbackFormRef.value) return;
  
  feedbackFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    const total = feedbackForm.completedQuantity + feedbackForm.defectiveQuantity
    if (total <= 0) {
      ElMessage.warning('成品数量和不良品数量之和必须大于0')
      return
    }

    submitting.value = true
    try {
      const response = await axios.post(`/api/workorder-process-details/feedback/`, {
        workorder_process_id: currentProcess.value?.id,
        completed_quantity: feedbackForm.completedQuantity,
        defective_quantity: feedbackForm.defectiveQuantity,
        defective_reason: feedbackForm.defectiveReason,
        remark: feedbackForm.remark
      })

      // 如果工单状态由已下达变为生产中，更新本地状态
      if (currentWorkOrder.value.status === 'released') {
        currentWorkOrder.value.status = 'in_progress'
      }

      ElMessage.success('工序回冲信息提交成功')
      
      // 处理工序转移或入库的消息
      if (response.data.message) {
        ElMessageBox.alert(response.data.message, '操作成功', {
          type: 'success',
          confirmButtonText: '确定'
        })
      }
      
      // 清空表单并重新搜索工单，更新状态
      resetForm()
      await searchWorkOrder()
    } catch (error: any) {
      console.error('提交回冲信息失败:', error)
      ElMessage.error(error.response?.data?.detail || '提交回冲信息失败')
    } finally {
      submitting.value = false
    }
  })
}

// 工具函数
const getProductDisplay = (workorder: WorkOrder): string => {
  return workorder.product_code && workorder.product_name 
    ? `${workorder.product_code} - ${workorder.product_name}` 
    : String(workorder.product)
}

const getStatusType = (status: string): string => {
  const statusTypes: Record<string, string> = {
    'draft': 'info',
    'print': 'warning',
    'released': 'info',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return statusTypes[status] || 'info'
}

const getStatusText = (status: string): string => {
  const statusTexts: Record<string, string> = {
    'draft': '草稿',
    'print': '待打印',
    'released': '已下达',
    'in_progress': '生产中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusTexts[status] || status
}
</script>

<style lang="scss" scoped>
.workorder-feedback-container {
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .page-title {
    margin: 0;
    font-size: 18px;
  }
  
  .search-section {
    margin-bottom: 24px;
  }
  
  .workorder-info-container {
    margin-top: 24px;
  }
  
  .current-process-container {
    margin-top: 24px;
    
    h3 {
      margin-bottom: 16px;
    }
    
    .current-process-info {
      margin-top: 16px;
    }
  }
  
  .feedback-form-container {
    margin-top: 24px;
    
    h3 {
      margin-bottom: 16px;
    }
    
    .feedback-form {
      max-width: 600px;
    }
    
    .form-input {
      width: 100%;
    }
  }

  .error-message {
    margin: 20px 0;
  }
}
</style> 