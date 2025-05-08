<template>
  <div class="process-detail-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工艺流程明细</h2>
          <div class="actions">
            <el-button type="primary" @click="$router.push('/process-codes')">
              <el-icon><Back /></el-icon> 返回工艺流程列表
            </el-button>
            <el-button type="success" @click="openAddDetailDialog" v-if="processCode.id">
              <el-icon><Plus /></el-icon> 添加工序
            </el-button>
          </div>
        </div>
      </template>

      <!-- 工艺流程代码信息 -->
      <el-descriptions
        :column="3"
        border
        v-if="processCode.id"
        class="process-code-info"
      >
        <el-descriptions-item label="工艺流程代码">{{ processCode.code }}</el-descriptions-item>
        <el-descriptions-item label="说明">{{ processCode.description }}</el-descriptions-item>
        <el-descriptions-item label="版本">{{ processCode.version }}</el-descriptions-item>
      </el-descriptions>

      <!-- 工艺流程明细表格 -->
      <div class="table-container">
        <el-table
          :data="processDetails"
          v-loading="loading"
          border
          stripe
          style="width: 100%"
        >
          <el-table-column prop="step_no" label="步骤" width="80" />
          <el-table-column prop="process_name" label="工序" min-width="150" />
          <el-table-column prop="estimated_time" label="工时(分钟)" min-width="120" />
          <el-table-column prop="required_equipment" label="所需设备" min-width="150" />
          <el-table-column prop="remark" label="备注" min-width="200" />
          <el-table-column label="操作" fixed="right" min-width="160">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" type="primary" @click="openEditDetailDialog(row)">
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
    </el-card>

    <!-- 明细编辑对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="currentDetail.id ? '编辑工艺流程明细' : '添加工艺流程明细'"
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
        <el-form-item label="步骤" prop="step_no">
          <el-input-number v-model="currentDetail.step_no" :min="1" class="form-input" />
        </el-form-item>
        <el-form-item label="工序" prop="process">
          <el-select v-model="currentDetail.process" filterable placeholder="请选择工序" class="form-input">
            <el-option
              v-for="process in processes"
              :key="process.id"
              :label="process.name"
              :value="process.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="工时(分钟)" prop="estimated_time">
          <el-input-number v-model="currentDetail.estimated_time" :min="0" :precision="2" class="form-input" />
        </el-form-item>
        <el-form-item label="所需设备" prop="required_equipment">
          <el-input v-model="currentDetail.required_equipment" placeholder="请输入所需设备" class="form-input" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="currentDetail.remark"
            type="textarea"
            rows="3"
            placeholder="请输入备注"
            class="form-input"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDetailDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="saveDetail">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete, Back } from '@element-plus/icons-vue'
import axios from 'axios'

// 类型定义
interface Process {
  id: number;
  code: string;
  name: string;
}

interface ProcessCode {
  id: number;
  code: string;
  description: string;
  version: string;
}

interface ProcessDetail {
  id?: number;
  process_code?: number;
  process_code_id?: number;
  step_no: number;
  process: number;
  process_name?: string;
  estimated_time: number;
  required_equipment: string;
  remark: string;
}

// 状态定义
const route = useRoute()
const codeId = route.params.id
const loading = ref(false)
const submitting = ref(false)
const processCode = ref<ProcessCode>({} as ProcessCode)
const processDetails = ref<ProcessDetail[]>([])
const processes = ref<Process[]>([])
const showDetailDialog = ref(false)
const detailFormRef = ref<FormInstance>()

// 当前编辑的明细对象
const currentDetail = reactive<ProcessDetail>({
  process_code: Number(codeId),
  step_no: 10,
  process: 0,
  estimated_time: 0,
  required_equipment: '',
  remark: ''
})

// 表单验证规则
const detailRules = {
  step_no: [
    { required: true, message: '请输入步骤号', trigger: 'blur' }
  ],
  process: [
    { required: true, message: '请选择工序', trigger: 'change' }
  ],
  estimated_time: [
    { required: true, message: '请输入预计工时', trigger: 'blur' }
  ]
}

// 数据加载方法
async function fetchProcessCode() {
  loading.value = true
  
  try {
    const response = await axios.get(`/api/process-codes/${codeId}/`)
    processCode.value = response.data
  } catch (error) {
    console.error('获取工艺流程代码失败:', error)
    ElMessage.error('获取工艺流程代码失败')
  } finally {
    loading.value = false
  }
}

async function fetchProcessDetails() {
  loading.value = true
  
  try {
    const response = await axios.get(`/api/process-code-details/?process_code=${codeId}`)
    const data = response.data.results || response.data
    
    // 按步骤号排序
    processDetails.value = data.sort((a: ProcessDetail, b: ProcessDetail) => a.step_no - b.step_no)
  } catch (error) {
    console.error('获取工艺流程明细失败:', error)
    ElMessage.error('获取工艺流程明细失败')
    processDetails.value = []
  } finally {
    loading.value = false
  }
}

async function fetchProcesses() {
  try {
    const response = await axios.get('/api/processes/')
    processes.value = response.data.results || response.data
  } catch (error) {
    console.error('获取工序列表失败:', error)
    ElMessage.error('获取工序列表失败')
    processes.value = []
  }
}

// 操作方法
function openAddDetailDialog() {
  // 重置当前明细对象
  Object.assign(currentDetail, {
    id: undefined,
    process_code: Number(codeId),
    step_no: getNextStepNo(),
    process: 0,
    estimated_time: 0,
    required_equipment: '',
    remark: ''
  })
  
  showDetailDialog.value = true
}

function openEditDetailDialog(detail: ProcessDetail) {
  // 复制明细数据到当前编辑对象
  Object.assign(currentDetail, detail)
  
  // 确保正确的process_code
  currentDetail.process_code = Number(codeId)
  
  showDetailDialog.value = true
}

function getNextStepNo(): number {
  // 如果没有明细，从10开始
  if (processDetails.value.length === 0) {
    return 10
  }
  
  // 找到最大的步骤号，然后+10
  const maxStep = Math.max(...processDetails.value.map(d => d.step_no))
  return maxStep + 10
}

async function saveDetail() {
  if (!detailFormRef.value) return
  
  detailFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      // 确保有正确的process_code
      currentDetail.process_code = Number(codeId)
      
      let response
      if (currentDetail.id) {
        // 编辑模式
        response = await axios.put(`/api/process-code-details/${currentDetail.id}/`, currentDetail)
        ElMessage.success('更新工艺流程明细成功')
      } else {
        // 新增模式
        response = await axios.post('/api/process-code-details/', currentDetail)
        ElMessage.success('添加工艺流程明细成功')
      }
      
      showDetailDialog.value = false
      fetchProcessDetails()
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
      console.error('保存工艺流程明细失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

function confirmDeleteDetail(detail: ProcessDetail) {
  ElMessageBox.confirm(
    `确定要删除该工艺流程明细吗？此操作不可恢复。`,
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

async function deleteDetail(detail: ProcessDetail) {
  if (!detail.id) return
  
  loading.value = true
  
  try {
    await axios.delete(`/api/process-code-details/${detail.id}/`)
    ElMessage.success('删除工艺流程明细成功')
    fetchProcessDetails()
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
    console.error('删除工艺流程明细失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchProcessCode()
  fetchProcessDetails()
  fetchProcesses()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.process-detail-container {
  .process-code-info {
    margin-bottom: 20px;
  }
  
  .table-container {
    margin-top: 20px;
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
