<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">工单明细</span>
      <el-button type="primary" @click="openAddDialog">新增明细</el-button>
    </div>
    <el-table :data="details" style="width:100%;margin-top:16px;" row-key="id">
      <el-table-column prop="workorder" label="工单号" />
      <el-table-column prop="product" label="产品" />
      <el-table-column prop="quantity" label="数量" />
      <el-table-column prop="process_code" label="工艺流程代码" />
      <el-table-column prop="plan_start" label="计划开始" />
      <el-table-column prop="plan_end" label="计划结束" />
      <el-table-column prop="status" label="状态" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteDetail(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showDialog" :title="dialogTitle">
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item label="工单号" prop="workorder">
          <el-input v-model="form.workorder" @keyup.enter.native="submitForm" />
        </el-form-item>
        <el-form-item label="产品" prop="product">
          <el-input v-model="form.product" @keyup.enter.native="submitForm" />
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="0" @keyup.enter.native="submitForm" />
        </el-form-item>
        <el-form-item label="工艺流程代码" prop="process_code">
          <el-input v-model="form.process_code" @keyup.enter.native="submitForm" />
        </el-form-item>
        <el-form-item label="计划开始" prop="plan_start">
          <el-date-picker v-model="form.plan_start" type="datetime" placeholder="选择日期时间" />
        </el-form-item>
        <el-form-item label="计划结束" prop="plan_end">
          <el-date-picker v-model="form.plan_end" type="datetime" placeholder="选择日期时间" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
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

const details = ref([])
const showDialog = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const loading = ref(false)
const formRef = ref()
const form = reactive({
  id: undefined,
  workorder: '',
  product: '',
  quantity: 0,
  process_code: '',
  plan_start: '',
  plan_end: '',
  status: '',
  remark: ''
})
const statusOptions = [
  { value: 'pending', label: '待生产' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]
const rules = {
  workorder: [{ required: true, message: '工单号必填', trigger: 'blur' }],
  product: [{ required: true, message: '产品必填', trigger: 'blur' }],
  quantity: [{ required: true, message: '数量必填', trigger: 'blur' }],
  status: [{ required: true, message: '状态必选', trigger: 'change' }]
}

function fetchDetails() {
  axios.get('/api/workorder-details/').then(res => {
    details.value = res.data
  })
}
function openAddDialog() {
  dialogTitle.value = '新增明细'
  isEdit.value = false
  Object.assign(form, { id: undefined, workorder: '', product: '', quantity: 0, process_code: '', plan_start: '', plan_end: '', status: '', remark: '' })
  showDialog.value = true
}
function openEditDialog(row: any) {
  dialogTitle.value = '编辑明细'
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
        await axios.put(`/api/workorder-details/${form.id}/`, form)
        ElMessage.success('编辑成功')
      } else {
        await axios.post('/api/workorder-details/', form)
        ElMessage.success('新增成功')
      }
      showDialog.value = false
      fetchDetails()
    } catch (e) {
      ElMessage.error('操作失败')
    } finally {
      loading.value = false
    }
  })
}
function deleteDetail(row: any) {
  loading.value = true
  axios.delete(`/api/workorder-details/${row.id}/`).then(() => {
    ElMessage.success('删除成功')
    fetchDetails()
  }).catch(() => {
    ElMessage.error('删除失败')
  }).finally(() => {
    loading.value = false
  })
}
onMounted(() => {
  fetchDetails()
})
</script>
<style>
@import '/src/style.css';
</style>
