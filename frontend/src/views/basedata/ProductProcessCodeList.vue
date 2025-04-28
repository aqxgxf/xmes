<!-- filepath: h:\xmes\frontend\src\views\basedata\ProductProcessCodeList.vue -->
<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">产品/工艺流程关系管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-input v-model="search" placeholder="搜索产品/工艺流程代码" style="width: 300px;" clearable @input="fetchData"/>
        <el-button type="primary" @click="openDialog()">新增关系</el-button>
      </div>
    </div>
    <el-table :data="list" border style="width:100%;margin-top:16px;"
      :header-cell-style="{textAlign:'center'}"
      :cell-style="{textAlign:'center'}"
      :table-layout="'auto'">
      <el-table-column prop="product_name" label="产品" width="180"/>
      <el-table-column prop="process_code_detail.code" label="工艺流程代码" width="180"/>
      <el-table-column prop="process_code_detail.version" label="版本" width="120"/>
      <el-table-column prop="is_default" label="默认" width="80">
        <template #default="scope">
          <el-tag v-if="scope.row.is_default" type="success">是</el-tag>
          <el-tag v-else>否</el-tag>
        </template>
      </el-table-column>
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
        <el-form-item label="产品" prop="product">
          <el-select v-model="form.product" filterable>
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="工艺流程代码" prop="process_code">
          <el-select v-model="form.process_code" filterable>
            <el-option v-for="pc in processCodes" :key="pc.id" :label="`${pc.code} (v${pc.version})`" :value="pc.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="默认" prop="is_default">
          <el-switch v-model="form.is_default"/>
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

interface Product {
  id: number
  name: string
}

interface ProcessCode {
  id: number
  code: string
  version: string
}

const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const search = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('新增关系')
const form = reactive({
  id: null as number | null,
  product: '' as number | '',
  process_code: '' as number | '',
  is_default: false
})
const rules = {
  product: [{ required: true, message: '请选择产品', trigger: 'change' }],
  process_code: [{ required: true, message: '请选择工艺流程代码', trigger: 'change' }]
}
const formRef = ref()
const products = ref<Product[]>([])
const processCodes = ref<ProcessCode[]>([])

function fetchData() {
  axios.get('/api/product-process-codes/', {
    params: {
      page: page.value,
      search: search.value
    }
  }).then(res => {
    list.value = res.data.results || res.data
    total.value = res.data.count || res.data.length
  })
}
function fetchProducts() {
  axios.get('/api/products/').then(res => {
    products.value = res.data.results || res.data
  })
}
function fetchProcessCodes() {
  axios.get('/api/process-codes/').then(res => {
    console.log('产品接口返回：', res.data)
    processCodes.value = res.data.results || res.data
  })
}
function openDialog(row?: any) {
  if (row) {
    dialogTitle.value = '编辑关系'
    Object.assign(form, {
      id: row.id,
      product: row.product,
      process_code: row.process_code,
      is_default: row.is_default
    })
  } else {
    dialogTitle.value = '新增关系'
    Object.assign(form, { id: null, product: '', process_code: '', is_default: false })
  }
  dialogVisible.value = true
  fetchProducts()
  fetchProcessCodes()
}
function submit() {
  (formRef.value as any).validate(async (valid: boolean) => {
    if (!valid) return
    if (form.id) {
      await axios.put(`/api/product-process-codes/${form.id}/`, form)
      ElMessage.success('修改成功')
    } else {
      await axios.post('/api/product-process-codes/', form)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  })
}
function remove(row: any) {
  ElMessageBox.confirm('确定要删除该关系吗？', '提示', { type: 'warning' })
    .then(async () => {
      await axios.delete(`/api/product-process-codes/${row.id}/`)
      ElMessage.success('删除成功')
      fetchData()
    })
}
onMounted(() => {
  fetchData()
  fetchProducts()
  fetchProcessCodes()
})
</script>
<style>
@import '/src/style.css';
</style>
<!-- 移除 scoped 样式，通用样式已抽取到 style.css，如有个性化样式可在此补充 -->