<!-- filepath: f:\xmes\frontend\src\views\base_data\ProcessCodeList.vue -->
<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">工艺流程代码管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-input v-model="search" placeholder="搜索代码/说明/版本" style="width: 300px;" clearable @input="fetchData"/>
        <el-button type="primary" @click="openDialog()">新增工艺流程代码</el-button>
      </div>
    </div>
    <el-table :data="list" border style="width: 100%;margin-top:16px;">
      <el-table-column prop="code" label="工艺流程代码" width="180"/>
      <el-table-column prop="description" label="说明"/>
      <el-table-column prop="version" label="版本" width="120"/>
      <el-table-column prop="created_at" label="创建时间" width="180"/>
      <el-table-column prop="updated_at" label="更新时间" width="180"/>
      <el-table-column label="操作" width="160">
        <template #default="scope">
          <el-button size="small" @click="openDialog(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="page"
      :page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="fetchData"
      style="margin-top: 16px; text-align: right;"
    />
    <el-dialog :title="dialogTitle" v-model="dialogVisible">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="工艺流程代码" prop="code">
          <el-input v-model="form.code"/>
        </el-form-item>
        <el-form-item label="说明" prop="description">
          <el-input v-model="form.description"/>
        </el-form-item>
        <el-form-item label="版本" prop="version">
          <el-input v-model="form.version"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const search = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('新增工艺流程代码')
const form = reactive({
  id: null,
  code: '',
  description: '',
  version: ''
})
const rules = {
  code: [{ required: true, message: '请输入工艺流程代码', trigger: 'blur' }],
  version: [{ required: true, message: '请输入版本', trigger: 'blur' }]
}
const formRef = ref()

function fetchData() {
  axios.get('/api/process-codes/', {
    params: {
      page: page.value,
      search: search.value
    }
  }).then(res => {
    list.value = res.data.results || res.data
    total.value = res.data.count || res.data.length
  })
}
function openDialog(row?: any) {
  if (row) {
    dialogTitle.value = '编辑工艺流程代码'
    Object.assign(form, row)
  } else {
    dialogTitle.value = '新增工艺流程代码'
    Object.assign(form, { id: null, code: '', description: '', version: '' })
  }
  dialogVisible.value = true
}
function submit() {
  (formRef.value as any).validate(async (valid: boolean) => {
    if (!valid) return
    if (form.id) {
      await axios.put(`/api/process-codes/${form.id}/`, form)
      ElMessage.success('修改成功')
    } else {
      await axios.post('/api/process-codes/', form)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  })
}
function remove(row: any) {
  ElMessageBox.confirm('确定要删除该工艺流程代码吗？', '提示', { type: 'warning' })
    .then(async () => {
      await axios.delete(`/api/process-codes/${row.id}/`)
      ElMessage.success('删除成功')
      fetchData()
    })
}
onMounted(fetchData)
</script>
<style>
@import '/src/style.css';
</style>
<!-- 移除 scoped 样式，通用样式已抽取到 style.css，如有个性化样式可在此补充 -->