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
        <el-form :inline="true" class="search-form">
          <el-form-item label="工单号">
            <el-input
              v-model="searchWorkOrderNo"
              placeholder="请输入工单号"
              clearable
              @keyup.enter="searchWorkOrder"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="searching" @click="searchWorkOrder">
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
        
        <!-- 当前工序信息 -->
        <div class="current-process-container">
          <h3>当前工序信息</h3>
          <el-alert v-if="!currentProcess" type="warning" show-icon>
            该工单尚未开始生产或已完成所有工序
          </el-alert>
          <el-descriptions v-else :column="2" border class="current-process-info">
            <el-descriptions-item label="工序号">{{ currentProcess.step_no }}</el-descriptions-item>
            <el-descriptions-item label="工序名称">{{ currentProcess.process_name }}</el-descriptions-item>
            <el-descriptions-item label="工序内容">{{ currentProcess.process_content || '-' }}</el-descriptions-item>
            <el-descriptions-item label="待加工数量">{{ currentProcess.pending_quantity }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 回冲信息表单 -->
        <div v-if="currentProcess" class="feedback-form-container">
          <h3>回冲信息</h3>
          <el-form
            ref="feedbackFormRef"
            :model="feedbackForm"
            :rules="feedbackRules"
            label-width="100px"
            label-position="right"
            class="feedback-form"
          >
            <el-form-item label="成品数量" prop="completedQuantity">
              <el-input-number
                v-model="feedbackForm.completedQuantity"
                :min="0"
                :max="currentProcess.pending_quantity"
                :precision="2"
                class="form-input"
              />
            </el-form-item>
            <el-form-item label="不良品数量" prop="defectiveQuantity">
              <el-input-number
                v-model="feedbackForm.defectiveQuantity"
                :min="0"
                :max="currentProcess.pending_quantity"
                :precision="2"
                class="form-input"
              />
            </el-form-item>
            <el-form-item label="不良原因" prop="defectiveReason" v-if="feedbackForm.defectiveQuantity > 0">
              <el-input
                v-model="feedbackForm.defectiveReason"
                type="textarea"
                rows="3"
                placeholder="请输入不良原因"
                class="form-input"
              />
            </el-form-item>
            <el-form-item label="备注" prop="remark">
              <el-input
                v-model="feedbackForm.remark"
                type="textarea"
                rows="2"
                placeholder="可选"
                class="form-input"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="submitting" @click="submitFeedback">提交回冲信息</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'

// 类型定义
interface WorkOrder {
  id: number;
  workorder_no: string;
  order: number | string;
  order_no?: string;
  product: number;
  product_code?: string;
  product_name?: string;
  quantity: number;
  process_code: number;
  process_code_text?: string;
  plan_start: string;
  plan_end: string;
  status: string;
  remark?: string;
}

interface ProcessDetail {
  id: number;
  workorder: number;
  step_no: number;
  process: number;
  process_name: string;
  process_content?: string;
  pending_quantity: number;
  processed_quantity: number;
  completed_quantity: number;
  status: string;
}

interface FeedbackForm {
  completedQuantity: number;
  defectiveQuantity: number;
  defectiveReason: string;
  remark: string;
}

// 状态定义
const searchWorkOrderNo = ref('')
const searching = ref(false)
const submitting = ref(false)
const currentWorkOrder = ref<WorkOrder>({} as WorkOrder)
const currentProcess = ref<ProcessDetail | null>(null)
const feedbackFormRef = ref<FormInstance>()

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
        if (currentProcess.value && total > currentProcess.value.pending_quantity) {
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
        if (currentProcess.value && total > currentProcess.value.pending_quantity) {
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
  try {
    // 获取工单基本信息
    const workorderRes = await axios.get(`/api/workorders/`, {
      params: { search: searchWorkOrderNo.value }
    })
    
    if (!workorderRes.data.results || workorderRes.data.results.length === 0) {
      ElMessage.error('未找到该工单号')
      resetWorkOrderInfo()
      return
    }

    // 设置当前工单
    currentWorkOrder.value = workorderRes.data.results[0]
    
    // 获取当前工序信息
    const processDetailsRes = await axios.get(`/api/workorder-processes/`, {
      params: { workorder: currentWorkOrder.value.id, current: true }
    })
    
    if (processDetailsRes.data.length > 0) {
      currentProcess.value = processDetailsRes.data[0]
      // 初始化表单
      feedbackForm.completedQuantity = 0
      feedbackForm.defectiveQuantity = 0
      feedbackForm.defectiveReason = ''
      feedbackForm.remark = ''
    } else {
      currentProcess.value = null
      ElMessage.info('该工单尚未开始生产或已完成所有工序')
    }
  } catch (error: any) {
    console.error('工单搜索失败:', error)
    ElMessage.error(error.response?.data?.detail || '工单搜索失败')
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

  // 校验表单
  await feedbackFormRef.value?.validate(async (valid) => {
    if (!valid) return
    
    const total = feedbackForm.completedQuantity + feedbackForm.defectiveQuantity
    if (total <= 0) {
      ElMessage.warning('成品数量和不良品数量之和必须大于0')
      return
    }

    submitting.value = true
    try {
      const response = await axios.post(`/api/workorder-processes/feedback/`, {
        workorder_process_id: currentProcess.value.id,
        completed_quantity: feedbackForm.completedQuantity,
        defective_quantity: feedbackForm.defectiveQuantity,
        defective_reason: feedbackForm.defectiveReason,
        remark: feedbackForm.remark
      })

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
    'processing': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return statusTypes[status] || 'info'
}

const getStatusText = (status: string): string => {
  const statusTexts: Record<string, string> = {
    'draft': '草稿',
    'print': '待打印',
    'processing': '生产中',
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
}
</style> 