<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">工艺流程明细管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-select v-model="searchProcessCode" filterable clearable placeholder="筛选工艺流程代码" style="width:220px;margin-right:8px;" @change="fetchData">
          <el-option v-for="item in filteredProcessCodes" :key="item.id" :label="item.code + ' (v' + item.version + ')'" :value="item.id" />
        </el-select>
        <el-button type="primary" @click="openAddDialog">新增明细</el-button>
      </div>
    </div>
    <el-table :data="list" style="width: 100%; margin-top: 12px" :loading="loading">
      <el-table-column prop="process_code_display" label="工艺流程代码" min-width="160" />
      <el-table-column prop="process_code_version" label="版本" min-width="80" />
      <el-table-column prop="step_no" label="工序号" min-width="80" />
      <el-table-column prop="step_name" label="工序名" min-width="120" />
      <el-table-column prop="machine_time" label="设备时间(分钟)" min-width="120" />
      <el-table-column prop="labor_time" label="人工时间(分钟)" min-width="120" />
      <el-table-column prop="program_file_url" label="程序文件" min-width="120">
        <template #default="scope">
          <a v-if="scope.row.program_file_url" :href="scope.row.program_file_url" target="_blank">下载</a>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="140">
        <template #default="scope">
          <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="table-pagination">
      <el-pagination
        background
        layout="sizes, prev, pager, next, jumper, ->, total"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        :page-sizes="[5, 10, 20, 50, 100]"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" @close="closeDialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" label-position="left" enctype="multipart/form-data">
        <el-form-item label="工艺流程代码" prop="process_code">
          <el-select v-model="form.process_code" filterable placeholder="请选择工艺流程代码" style="width:320px">
            <el-option v-for="item in processCodes" :key="item.id" :label="item.code + ' (v' + item.version + ')'" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="工序号" prop="step_no">
          <el-input-number v-model="form.step_no" :min="1" style="width:320px" />
        </el-form-item>
        <el-form-item label="工序名" prop="step">
          <el-select v-model="form.step" filterable placeholder="请选择工序" style="width:320px">
            <el-option v-for="item in processes" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备时间(分钟)" prop="machine_time">
          <el-input-number v-model="form.machine_time" :min="0" :step="0.1" style="width:320px" />
        </el-form-item>
        <el-form-item label="人工时间(分钟)" prop="labor_time">
          <el-input-number v-model="form.labor_time" :min="0" :step="0.1" style="width:320px" />
        </el-form-item>
        <el-form-item label="程序文件" prop="program_file">
          <el-upload
            class="upload-demo"
            :action="null"
            :auto-upload="false"
            :show-file-list="true"
            :on-change="handleFileChange"
            :file-list="fileList"
            :limit="1"
            accept=".pdf,.zip,.rar,.txt,.doc,.docx,.xls,.xlsx,.dwg,.dxf"
          >
            <el-button size="small" type="primary">选择文件</el-button>
            <template #tip>
              <div style="font-size:12px;color:#888;">支持常见文档/图纸/压缩包</div>
            </template>
          </el-upload>
          <div v-if="form.program_file_name" style="margin-top:4px;">
            <span style="color:#409EFF">已上传文件：</span>{{ form.program_file_name }}
            <a v-if="form.program_file && typeof form.program_file === 'string'" :href="form.program_file" target="_blank" style="margin-left:8px;">下载</a>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
const loading = ref(false)
const list = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchProcessCode = ref()
const dialogVisible = ref(false)
const dialogTitle = ref('新增工艺流程明细')
const form = reactive({
  id: null,
  process_code: '',
  step_no: 1,
  step: '',
  machine_time: 0,
  labor_time: 0,
  program_file: null,
  program_file_name: ''
})
const fileList = ref<any[]>([])
const formRef = ref()
const processCodes = ref<any[]>([])
const processes = ref<any[]>([])
const rules = {
  process_code: [{ required: true, message: '请选择工艺流程代码', trigger: 'change' }],
  step_no: [{ required: true, message: '请输入工序号', trigger: 'blur' }],
  step: [{ required: true, message: '请选择工序', trigger: 'change' }],
  machine_time: [{ required: true, message: '请输入设备时间', trigger: 'blur' }],
  labor_time: [{ required: true, message: '请输入人工时间', trigger: 'blur' }]
}
const filteredProcessCodes = computed(() => {
  if (!searchProcessCode.value) return processCodes.value
  return processCodes.value.filter((p: any) =>
    p.code && p.code.toLowerCase().includes(String(searchProcessCode.value).toLowerCase())
  )
})
function fetchProcessCodes() {
  axios.get('/api/process-codes/', { params: { page_size: 1000 } }).then(res => {
    processCodes.value = res.data.results || res.data
  })
}
function fetchProcesses() {
  axios.get('/api/processes/', { params: { page_size: 1000 } }).then(res => {
    processes.value = res.data.results || res.data
  })
}
function fetchData() {
  loading.value = true
  const params: any = {
    page: currentPage.value,
    page_size: pageSize.value
  }
  // 修正筛选：用 search 参数实现后端模糊过滤
  if (searchProcessCode.value) {
    const selected = processCodes.value.find((p:any) => p.id === searchProcessCode.value)
    if (selected) {
      params.search = selected.code
    }
  }
  axios.get('/api/process-details/', { params }).then(res => {
    list.value = res.data.results || res.data
    total.value = res.data.count || res.data.length
  }).finally(() => loading.value = false)
}
function openAddDialog() {
  dialogTitle.value = '新增工艺流程明细'
  Object.assign(form, { id: null, process_code: '', step_no: 1, step: '', machine_time: 0, labor_time: 0, program_file: null })
  fileList.value = []
  dialogVisible.value = true
}
function openEditDialog(row: any) {
  dialogTitle.value = '编辑工艺流程明细'
  Object.assign(form, { ...row, process_code: row.process_code, step: row.step, program_file: null })
  fileList.value = []
  // 新增：显示已上传文件名
  if (row.program_file_url) {
    form.program_file_name = row.program_file_url.split('/').pop()
  } else {
    form.program_file_name = ''
  }
  dialogVisible.value = true
}
function closeDialog() {
  dialogVisible.value = false
  Object.assign(form, { id: null, process_code: '', step_no: 1, step: '', machine_time: 0, labor_time: 0, program_file: null })
  fileList.value = []
}
function handleFileChange(file: any) {
  fileList.value = [file]
  form.program_file = file.raw
}
function submit() {
  (formRef.value as any).validate(async (valid: boolean) => {
    if (!valid) return
    const fd = new FormData()
    fd.append('process_code', form.process_code)
    fd.append('step_no', String(form.step_no))
    fd.append('step', form.step)
    fd.append('machine_time', String(form.machine_time))
    fd.append('labor_time', String(form.labor_time))
    if (fileList.value.length && fileList.value[0].raw) {
      fd.append('program_file', fileList.value[0].raw)
    }
    try {
      if (form.id) {
        await axios.put(`/api/process-details/${form.id}/`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
        ElMessage.success('修改成功')
      } else {
        await axios.post('/api/process-details/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch (e) {
      ElMessage.error('保存失败')
    }
  })
}
function remove(row: any) {
  ElMessageBox.confirm('确定要删除该工艺流程明细吗？', '提示', { type: 'warning' })
    .then(async () => {
      await axios.delete(`/api/process-details/${row.id}/`)
      ElMessage.success('删除成功')
      fetchData()
    })
}
function handlePageChange(val: number) {
  currentPage.value = val
  fetchData()
}
function handleSizeChange(val: number) {
  pageSize.value = val
  currentPage.value = 1
  fetchData()
}
onMounted(() => {
  fetchProcessCodes()
  fetchProcesses()
  fetchData()
})
</script>
<style>
@import '/src/style.css';
</style>
<!-- 移除 scoped 样式，通用样式已抽取到 style.css，如有个性化样式可在此补充 -->
