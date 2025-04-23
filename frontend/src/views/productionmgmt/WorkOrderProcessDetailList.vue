<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">工单工艺明细</span>
      <el-button type="primary" @click="openAddDialog">新增工艺明细</el-button>
    </div>
    <el-table :data="processDetails" style="width:100%;margin-top:16px;" row-key="id">
      <el-table-column prop="workorder_detail" label="工单明细ID" />
      <el-table-column prop="process_code" label="工艺流程代码" />
      <el-table-column prop="step_no" label="工序号" />
      <el-table-column prop="step" label="工序名" />
      <el-table-column prop="machine_time" label="设备时间(分钟)" />
      <el-table-column prop="labor_time" label="人工时间(分钟)" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="actual_start" label="实际开始" />
      <el-table-column prop="actual_end" label="实际结束" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteProcessDetail(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showDialog" :title="dialogTitle">
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item label="工单明细ID" prop="workorder_detail">
          <el-input v-model="form.workorder_detail" @keyup.enter.native="submitForm" />
        </el-form-item>
        <el-form-item label="工艺流程代码" prop="process_code">
          <el-input v-model="form.process_code" @keyup.enter.native="submitForm" />
        </el-form-item>
        <el-form-item label="工序号" prop="step_no">
          <el-input-number v-model="form.step_no" :min="1" @keyup.enter.native="submitForm" />
        </el-form-item>
        <el-form-item label="工序名" prop="step">
          <el-input v-model="form.step" @keyup.enter.native="submitForm" />
        </el-form-item>
        <el-form-item label="设备时间(分钟)" prop="machine_time">
          <el-input-number v-model="form.machine_time" :min="0" @keyup.enter.native="submitForm" />
        </el-form-item>
        <el-form-item label="人工时间(分钟)" prop="labor_time">
          <el-input-number v-model="form.labor_time" :min="0" @keyup.enter.native="submitForm" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="实际开始" prop="actual_start">
          <el-date-picker v-model="form.actual_start" type="datetime" placeholder="选择日期时间" />
        </el-form-item>
        <el-form-item label="实际结束" prop="actual_end">
          <el-date-picker v-model="form.actual_end" type="datetime" placeholder="选择日期时间" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" @keyup.enter.native="submitForm" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog=false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const processDetails = ref([])
const showDialog = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const loading = ref(false)
const formRef = ref()
const form = reactive({
  id: undefined,
  workorder_detail: '',
  process_code: '',
  step_no: 1,
  step: '',
  machine_time: 0,
  labor_time: 0,
  status: '',
  actual_start: '',
  actual_end: '',
  remark: ''
})
const statusOptions = [
  { value: 'pending', label: '待生产' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]
const rules = {
  workorder_detail: [{ required: true, message: '工单明细ID必填', trigger: 'blur' }],
  process_code: [{ required: true, message: '工艺流程代码必填', trigger: 'blur' }],
  step_no: [{ required: true, message: '工序号必填', trigger: 'blur' }],
  step: [{ required: true, message: '工序名必填', trigger: 'blur' }],
  status: [{ required: true, message: '状态必选', trigger: 'change' }]
}

function fetchProcessDetails() {
  axios.get('/api/workorder-process-details/').then(res => {
    processDetails.value = res.data
  })
}
function openAddDialog() {
  dialogTitle.value = '新增工艺明细'
  isEdit.value = false
  Object.assign(form, { id: undefined, workorder_detail: '', process_code: '', step_no: 1, step: '', machine_time: 0, labor_time: 0, status: '', actual_start: '', actual_end: '', remark: '' })
  showDialog.value = true
}
function openEditDialog(row: any) {
  dialogTitle.value = '编辑工艺明细'
  isEdit.value = true
  Object.assign(form, row)
  showDialog.value = true
}
function submitForm() {
  formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    loading.value = true
    try {
      if (isEdit.value) {
        await axios.put(`/api/workorder-process-details/${form.id}/`, form)
        ElMessage.success('编辑成功')
      } else {
        await axios.post('/api/workorder-process-details/', form)
        ElMessage.success('新增成功')
      }
      showDialog.value = false
      fetchProcessDetails()
    } catch (e) {
      ElMessage.error('操作失败')
    } finally {
      loading.value = false
    }
  })
}
function deleteProcessDetail(row: any) {
  loading.value = true
  axios.delete(`/api/workorder-process-details/${row.id}/`).then(() => {
    ElMessage.success('删除成功')
    fetchProcessDetails()
  }).catch(() => {
    ElMessage.error('删除失败')
  }).finally(() => {
    loading.value = false
  })
}
onMounted(() => {
  fetchProcessDetails()
})
</script>
<style>
@import '/src/style.css';
</style>
