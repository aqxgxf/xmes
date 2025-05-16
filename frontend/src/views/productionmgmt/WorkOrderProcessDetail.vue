<template>
  <div class="process-detail-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工单工艺明细</h2>
          <div class="actions">
            <el-button type="primary" @click="$router.push('/workorders')">
              <el-icon><Back /></el-icon> 返回工单列表
            </el-button>
            <el-button 
              v-if="!hasProcessDetails && workorder.process_code && workorder.status === 'draft'" 
              type="success" 
              @click="generateProcessDetails"
            >
              <el-icon><Plus /></el-icon> 生成工艺明细
            </el-button>
          </div>
        </div>
      </template>

      <!-- 工单基本信息 -->
      <el-descriptions 
        :column="4" 
        border 
        v-if="workorder.id"
        class="workorder-info"
      >
        <el-descriptions-item label="工单号">{{ workorder.workorder_no }}</el-descriptions-item>
        <el-descriptions-item label="订单号">{{ workorder.order_no || workorder.order }}</el-descriptions-item>
        <el-descriptions-item label="产品">{{ getProductDisplay(workorder) }}</el-descriptions-item>
        <el-descriptions-item label="数量">{{ workorder.quantity }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(workorder.status)">{{ getStatusText(workorder.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="计划开始">{{ workorder.plan_start }}</el-descriptions-item>
        <el-descriptions-item label="计划结束">{{ workorder.plan_end }}</el-descriptions-item>
        <el-descriptions-item label="工艺流程">{{ workorder.process_code_text || workorder.process_code }}</el-descriptions-item>
      </el-descriptions>

      <!-- 工艺明细表格 -->
      <div class="table-container">
        <div class="table-header">
          <h3>工艺明细列表</h3>
          <el-button 
            v-if="hasProcessDetails" 
            type="primary" 
            size="small"
            @click="openAddDetailDialog"
          >
            <el-icon><Plus /></el-icon> 新增明细
          </el-button>
        </div>
        
        <el-table 
          :data="processDetails" 
          v-loading="loading" 
          border
          stripe
          style="width:100%"
        >
          <el-table-column prop="step_no" label="工序号" width="80" />
          <el-table-column prop="process_name" label="工序名称" min-width="120" />
          <el-table-column prop="process_content" label="工序内容" min-width="180" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getProcessStatusType(row.status)">{{ getProcessStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="pending_quantity" label="待加工数量" min-width="120" />
          <el-table-column prop="processed_quantity" label="已加工数量" min-width="120" />
          <el-table-column prop="completed_quantity" label="完工数量" min-width="120" />
          <el-table-column prop="machine_time" label="设备时间(分钟)" min-width="120" />
          <el-table-column prop="labor_time" label="人工时间(分钟)" min-width="120" />
          <el-table-column prop="plan_start_time" label="计划开始" min-width="160" />
          <el-table-column prop="plan_end_time" label="计划结束" min-width="160" />
          <el-table-column prop="actual_start_time" label="实际开始" min-width="160" />
          <el-table-column prop="actual_end_time" label="实际结束" min-width="160" />
          <el-table-column label="操作" fixed="right" width="180">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" type="primary" @click="editDetail(row)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
                <el-button size="small" type="danger" @click="confirmDeleteDetail(row)">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 编辑明细弹窗 -->
      <el-dialog 
        v-model="showDetailDialog" 
        :title="currentDetail.id ? '编辑工艺明细' : '新增工艺明细'" 
        width="600px"
        destroy-on-close
      >
        <el-form 
          :model="currentDetail" 
          :rules="detailRules"
          ref="detailFormRef" 
          label-width="120px"
          label-position="left"
        >
          <el-form-item label="工序号" prop="step_no">
            <el-input-number v-model="currentDetail.step_no" :min="1" class="form-input" />
          </el-form-item>
          <el-form-item label="工序" prop="process">
            <el-select v-model="currentDetail.process" filterable class="form-input">
              <el-option v-for="p in processes" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="工序内容" prop="process_content">
            <el-input v-model="currentDetail.process_content" placeholder="请输入工序内容" class="form-input" />
          </el-form-item>
          <el-form-item label="待加工数量" prop="pending_quantity">
            <el-input-number v-model="currentDetail.pending_quantity" :min="0" :precision="2" class="form-input" />
          </el-form-item>
          <el-form-item label="已加工数量" prop="processed_quantity">
            <el-input-number v-model="currentDetail.processed_quantity" :min="0" :precision="2" class="form-input" />
          </el-form-item>
          <el-form-item label="完工数量" prop="completed_quantity">
            <el-input-number v-model="currentDetail.completed_quantity" :min="0" :precision="2" class="form-input" />
          </el-form-item>
          <el-form-item label="设备时间(分钟)" prop="machine_time">
            <el-input-number v-model="currentDetail.machine_time" :min="0" :precision="2" class="form-input" />
          </el-form-item>
          <el-form-item label="人工时间(分钟)" prop="labor_time">
            <el-input-number v-model="currentDetail.labor_time" :min="0" :precision="2" class="form-input" />
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-select v-model="currentDetail.status" class="form-input">
              <el-option v-for="item in processStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="计划开始时间" prop="plan_start_time">
            <el-date-picker v-model="currentDetail.plan_start_time" type="datetime" class="form-input" />
          </el-form-item>
          <el-form-item label="计划结束时间" prop="plan_end_time">
            <el-date-picker v-model="currentDetail.plan_end_time" type="datetime" class="form-input" />
          </el-form-item>
          <el-form-item label="实际开始时间" prop="actual_start_time">
            <el-date-picker v-model="currentDetail.actual_start_time" type="datetime" class="form-input" />
          </el-form-item>
          <el-form-item label="实际结束时间" prop="actual_end_time">
            <el-date-picker v-model="currentDetail.actual_end_time" type="datetime" class="form-input" />
          </el-form-item>
          <el-form-item label="备注" prop="remark">
            <el-input v-model="currentDetail.remark" type="textarea" rows="2" class="form-input" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showDetailDialog = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="saveDetail">保存</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Back, Plus, Edit, Delete } from '@element-plus/icons-vue'
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
  process_code: number | string;
  process_code_text?: string;
  plan_start: string;
  plan_end: string;
  status: string;
  remark?: string;
}

interface ProcessDetail {
  id?: number;
  workorder?: number;
  step_no: number;
  process: number;
  process_name?: string;
  process_content?: string;
  pending_quantity: number;
  processed_quantity: number;
  completed_quantity: number;
  machine_time: number;
  labor_time: number;
  status: string;
  plan_start_time: string | null;
  plan_end_time: string | null;
  actual_start_time: string | null;
  actual_end_time: string | null;
  remark?: string;
}

interface Process {
  id: number;
  code: string;
  name: string;
}

// 状态定义
const route = useRoute()
const workorderId = route.params.id
const loading = ref(false)
const submitting = ref(false)
const workorder = ref<WorkOrder>({} as WorkOrder)
const processDetails = ref<ProcessDetail[]>([])
const processes = ref<Process[]>([])
const showDetailDialog = ref(false)
const detailFormRef = ref<FormInstance>()

// 定义表单验证规则
const detailRules = {
  step_no: [
    { required: true, message: '请输入工序号', trigger: 'blur' }
  ],
  process: [
    { required: true, message: '请选择工序', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 工艺明细状态选项
const processStatusOptions = [
  { value: 'pending', label: '待生产' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'skipped', label: '已跳过' }
]

// 工单状态选项
const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'print', label: '待打印' },
  { value: 'released', label: '已下达' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]

// 工艺明细表单对象
const currentDetail = reactive<ProcessDetail>({
  id: undefined,
  workorder: Number(workorderId),
  step_no: 0,
  process: 0,
  process_content: '',
  pending_quantity: 0,
  processed_quantity: 0,
  completed_quantity: 0,
  machine_time: 0,
  labor_time: 0,
  status: 'pending',
  plan_start_time: null,
  plan_end_time: null,
  actual_start_time: null,
  actual_end_time: null,
  remark: ''
})

// 计算属性
const hasProcessDetails = computed(() => processDetails.value.length > 0)

// 状态相关方法
function getStatusText(status: string) {
  const found = statusOptions.find(s => s.value === status)
  return found ? found.label : status
}

function getProcessStatusText(status: string) {
  const found = processStatusOptions.find(s => s.value === status)
  return found ? found.label : status
}

function getStatusType(status: string) {
  switch (status) {
    case 'draft': return ''
    case 'print': return 'warning'
    case 'released': return 'info'
    case 'in_progress': return 'primary'
    case 'completed': return 'success'
    case 'cancelled': return 'danger'
    default: return ''
  }
}

function getProcessStatusType(status: string) {
  switch (status) {
    case 'pending': return 'info'
    case 'in_progress': return 'warning'
    case 'completed': return 'success'
    case 'skipped': return 'danger'
    default: return ''
  }
}

function getProductDisplay(workorder: WorkOrder) {
  if (workorder.product_code && workorder.product_name) {
    return `${workorder.product_code} - ${workorder.product_name}`;
  }
  return workorder.product || '';
}

// 数据加载方法
async function fetchWorkOrder() {
  loading.value = true
  
  try {
    const response = await axios.get(`/api/workorders/${workorderId}/`)
    workorder.value = response.data
  } catch (error) {
    ElMessage.error('获取工单信息失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function fetchProcessDetails() {
  loading.value = true
  
  try {
    const response = await axios.get(`/api/workorder-process-details/?workorder=${workorderId}`)
    processDetails.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取工艺明细失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function fetchProcesses() {
  try {
    const response = await axios.get('/api/processes/')
    processes.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取工序列表失败')
    console.error(error)
  }
}

// 表单处理方法
function openAddDetailDialog() {
  resetDetailForm()
  currentDetail.workorder = Number(workorderId)
  
  // 如果已有明细，自动设置下一个工序号
  if (processDetails.value.length > 0) {
    const maxStepNo = Math.max(...processDetails.value.map(d => d.step_no))
    currentDetail.step_no = maxStepNo + 10
  } else {
    currentDetail.step_no = 10
  }
  
  showDetailDialog.value = true
}

function editDetail(detail: ProcessDetail) {
  resetDetailForm()
  
  Object.assign(currentDetail, detail)
  
  // 确保数值类型正确
  if (typeof currentDetail.pending_quantity === 'string') {
    currentDetail.pending_quantity = parseFloat(currentDetail.pending_quantity)
  }
  if (typeof currentDetail.processed_quantity === 'string') {
    currentDetail.processed_quantity = parseFloat(currentDetail.processed_quantity)
  }
  if (typeof currentDetail.completed_quantity === 'string') {
    currentDetail.completed_quantity = parseFloat(currentDetail.completed_quantity)
  }
  if (typeof currentDetail.machine_time === 'string') {
    currentDetail.machine_time = parseFloat(currentDetail.machine_time)
  }
  if (typeof currentDetail.labor_time === 'string') {
    currentDetail.labor_time = parseFloat(currentDetail.labor_time)
  }
  
  showDetailDialog.value = true
}

function resetDetailForm() {
  Object.assign(currentDetail, {
    id: undefined,
    workorder: Number(workorderId),
    step_no: 0,
    process: 0,
    process_content: '',
    pending_quantity: 0,
    processed_quantity: 0,
    completed_quantity: 0,
    machine_time: 0,
    labor_time: 0,
    status: 'pending',
    plan_start_time: null,
    plan_end_time: null,
    actual_start_time: null,
    actual_end_time: null,
    remark: ''
  })
}

function confirmDeleteDetail(detail: ProcessDetail) {
  ElMessageBox.confirm(
    `确定要删除该工艺明细吗？此操作不可恢复。`, 
    '删除确认', 
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  ).then(() => {
    deleteDetail(detail)
  }).catch(() => {
    // 用户取消操作
  })
}

// API交互方法
async function saveDetail() {
  if (!detailFormRef.value) return
  
  detailFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      if (currentDetail.id) {
        // 编辑模式
        await axios.put(`/api/workorder-process-details/${currentDetail.id}/`, currentDetail)
        ElMessage.success('工艺明细更新成功')
      } else {
        // 新增模式
        currentDetail.workorder = Number(workorderId)
        await axios.post('/api/workorder-process-details/', currentDetail)
        ElMessage.success('工艺明细创建成功')
      }
      
      showDetailDialog.value = false
      await fetchProcessDetails()
    } catch (error: any) {
      let errorMsg = '保存失败'
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMsg = error.response.data
        } else if (typeof error.response.data === 'object') {
          if (error.response.data.detail) {
            errorMsg = error.response.data.detail
          } else {
            const firstError = Object.values(error.response.data)[0]
            if (Array.isArray(firstError) && firstError.length > 0) {
              errorMsg = firstError[0] as string
            }
          }
        }
      }
      
      ElMessage.error(`保存失败: ${errorMsg}`)
      console.error('保存工艺明细失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

async function deleteDetail(detail: ProcessDetail) {
  if (!detail.id) return
  
  loading.value = true
  
  try {
    await axios.delete(`/api/workorder-process-details/${detail.id}/`)
    ElMessage.success('删除成功')
    await fetchProcessDetails()
  } catch (error: any) {
    let errorMsg = '删除失败'
    
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (typeof error.response.data === 'object') {
        if (error.response.data.detail) {
          errorMsg = error.response.data.detail
        }
      }
    }
    
    ElMessage.error(`删除失败: ${errorMsg}`)
    console.error('删除工艺明细失败:', error)
  } finally {
    loading.value = false
  }
}

async function generateProcessDetails() {
  loading.value = true
  
  try {
    await axios.post(`/api/workorders/${workorderId}/generate-process-details/`)
    ElMessage.success('工艺明细生成成功')
    await fetchProcessDetails()
  } catch (error: any) {
    let errorMsg = '生成工艺明细失败'
    
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (typeof error.response.data === 'object') {
        if (error.response.data.detail) {
          errorMsg = error.response.data.detail
        }
      }
    }
    
    ElMessage.error(`生成工艺明细失败: ${errorMsg}`)
    console.error('生成工艺明细失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchWorkOrder()
  fetchProcessDetails()
  fetchProcesses()
})
</script>

<style lang="scss" scoped>
@use '../../assets/styles/common.scss' as *;

.process-detail-container {
  .workorder-info {
    margin-bottom: 20px;
  }
  
  .table-container {
    margin-top: 20px;
  }
  
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h3 {
      margin: 0;
      font-size: 16px;
      color: var(--el-text-color-primary);
    }
  }
  
  .form-input {
    width: 100%;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
  }
  
  .actions {
    display: flex;
    gap: 10px;
  }
}
</style> 