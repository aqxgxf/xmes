<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <span style="font-size:18px;font-weight:bold;">工单工艺明细</span>
      <div>
        <el-button type="primary" @click="$router.push('/workorders')">返回工单列表</el-button>
        <el-button type="success" @click="generateProcessDetails" v-if="!hasProcessDetails && workorder.process_code && workorder.status === 'draft'">生成工艺明细</el-button>
      </div>
    </div>

    <!-- 工单基本信息 -->
    <el-descriptions :column="4" border class="mt-4" v-if="workorder.id">
      <el-descriptions-item label="工单号">{{ workorder.workorder_no }}</el-descriptions-item>
      <el-descriptions-item label="订单号">{{ workorder.order_no || workorder.order }}</el-descriptions-item>
      <el-descriptions-item label="产品">{{ getProductDisplay(workorder) }}</el-descriptions-item>
      <el-descriptions-item label="数量">{{ workorder.quantity }}</el-descriptions-item>
      <el-descriptions-item label="状态">{{ getStatusText(workorder.status) }}</el-descriptions-item>
      <el-descriptions-item label="计划开始">{{ workorder.plan_start }}</el-descriptions-item>
      <el-descriptions-item label="计划结束">{{ workorder.plan_end }}</el-descriptions-item>
      <el-descriptions-item label="工艺流程">{{ workorder.process_code_text || workorder.process_code }}</el-descriptions-item>
    </el-descriptions>

    <!-- 工艺明细表格 -->
    <div style="margin-top:20px">
      <el-table :data="processDetails" style="width:100%" border>
        <el-table-column prop="step_no" label="工序号" width="80" />
        <el-table-column prop="process_name" label="工序名称" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ getProcessStatusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pending_quantity" label="待加工数量" width="120" />
        <el-table-column prop="processed_quantity" label="已加工数量" width="120" />
        <el-table-column prop="completed_quantity" label="完工数量" width="120" />
        <el-table-column prop="machine_time" label="设备时间(分钟)" width="120" />
        <el-table-column prop="labor_time" label="人工时间(分钟)" width="120" />
        <el-table-column prop="plan_start_time" label="计划开始" width="160" />
        <el-table-column prop="plan_end_time" label="计划结束" width="160" />
        <el-table-column prop="actual_start_time" label="实际开始" width="160" />
        <el-table-column prop="actual_end_time" label="实际结束" width="160" />
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="scope">
            <el-button size="small" @click="editDetail(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteDetail(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑明细弹窗 -->
    <el-dialog v-model="showDetailDialog" :title="currentDetail.id ? '编辑工艺明细' : '新增工艺明细'" width="600px">
      <el-form :model="currentDetail" label-width="120px" ref="detailFormRef">
        <el-form-item label="工序号">
          <el-input-number v-model="currentDetail.step_no" :min="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="工序">
          <el-select v-model="currentDetail.process" filterable style="width:100%">
            <el-option v-for="p in processes" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="待加工数量">
          <el-input-number v-model="currentDetail.pending_quantity" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="已加工数量">
          <el-input-number v-model="currentDetail.processed_quantity" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="完工数量">
          <el-input-number v-model="currentDetail.completed_quantity" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="设备时间(分钟)">
          <el-input-number v-model="currentDetail.machine_time" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="人工时间(分钟)">
          <el-input-number v-model="currentDetail.labor_time" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="currentDetail.status" style="width:100%">
            <el-option v-for="item in processStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划开始时间">
          <el-date-picker v-model="currentDetail.plan_start_time" type="datetime" style="width:100%" />
        </el-form-item>
        <el-form-item label="计划结束时间">
          <el-date-picker v-model="currentDetail.plan_end_time" type="datetime" style="width:100%" />
        </el-form-item>
        <el-form-item label="实际开始时间">
          <el-date-picker v-model="currentDetail.actual_start_time" type="datetime" style="width:100%" />
        </el-form-item>
        <el-form-item label="实际结束时间">
          <el-date-picker v-model="currentDetail.actual_end_time" type="datetime" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="currentDetail.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDetailDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDetail">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const workorderId = route.params.id
const workorder = ref<any>({})
const processDetails = ref<any[]>([])
const processes = ref<any[]>([])
const showDetailDialog = ref(false)
const currentDetail = ref<any>({})
const detailFormRef = ref()

const processStatusOptions = [
  { value: 'pending', label: '待生产' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'skipped', label: '已跳过' }
]

const statusOptions = [
{ value: 'draft', label: '草稿' },
{ value: 'print', label: '待打印' },
{ value: 'released', label: '已下达' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]

const hasProcessDetails = computed(() => processDetails.value.length > 0)

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
    case 'pending': return 'info'
    case 'in_progress': return 'warning'
    case 'completed': return 'success'
    case 'skipped': return 'danger'
    default: return ''
  }
}

function getProductDisplay(workorder: any) {
  if (workorder.product_code && workorder.product_name) {
    return `${workorder.product_code} - ${workorder.product_name}`;
  }
  return workorder.product || '';
}

async function fetchWorkOrder() {
  try {
    const response = await axios.get(`/api/workorders/${workorderId}/`)
    workorder.value = response.data
  } catch (error) {
    ElMessage.error('获取工单信息失败')
    console.error(error)
  }
}

async function fetchProcessDetails() {
  try {
    const response = await axios.get(`/api/workorder-process-details/?workorder=${workorderId}`)
    processDetails.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取工艺明细失败')
    console.error(error)
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

function editDetail(detail: any) {
  currentDetail.value = { ...detail }
  showDetailDialog.value = true
}

async function saveDetail() {
  try {
    let response
    if (currentDetail.value.id) {
      response = await axios.put(`/api/workorder-process-details/${currentDetail.value.id}/`, currentDetail.value)
      ElMessage.success('工艺明细更新成功')
    } else {
      currentDetail.value.workorder = workorderId
      response = await axios.post('/api/workorder-process-details/', currentDetail.value)
      ElMessage.success('工艺明细创建成功')
    }
    showDetailDialog.value = false
    await fetchProcessDetails()
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error?.response?.data?.detail || error.message || '未知错误'))
  }
}

async function deleteDetail(detail: any) {
  try {
    await ElMessageBox.confirm('确定要删除该工艺明细吗？此操作不可恢复。', '删除确认', {
      type: 'warning'
    })
    await axios.delete(`/api/workorder-process-details/${detail.id}/`)
    ElMessage.success('删除成功')
    await fetchProcessDetails()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error?.response?.data?.detail || error.message || '未知错误'))
    }
  }
}

async function generateProcessDetails() {
  try {
    await axios.post(`/api/workorders/${workorderId}/generate-process-details/`)
    ElMessage.success('工艺明细生成成功')
    await fetchProcessDetails()
  } catch (error: any) {
    ElMessage.error('生成工艺明细失败: ' + (error?.response?.data?.detail || error.message || '未知错误'))
  }
}

onMounted(() => {
  fetchWorkOrder()
  fetchProcessDetails()
  fetchProcesses()
})
</script>

<style scoped>
.mt-4 {
  margin-top: 16px;
}
</style> 