<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">BOM管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-input v-model="search" placeholder="搜索BOM名称/产品/版本" style="width: 300px;" clearable @input="fetchData" />
        <el-button type="primary" @click="openDialog({})">新增BOM</el-button>
      </div>
    </div>
    <el-table :data="list" border style="width: 100%;margin-top:16px;">
      <el-table-column prop="name" label="BOM名称" width="200" />
      <el-table-column prop="product_name" label="产品" width="200" />
      <el-table-column prop="version" label="版本" width="120" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column prop="updated_at" label="更新时间" width="180" />
      <el-table-column label="操作" width="160">
        <template #default="scope">
          <el-button size="small" @click="openDialog(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination :current-page.sync="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next"
      @current-change="fetchData" style="margin-top: 16px; text-align: right;" />
    <el-dialog :title="dialogTitle" v-model="dialogVisible">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="产品" prop="product">
          <el-select v-model="form.product" placeholder="请选择产品" filterable style="width:100%">
            <el-option v-for="item in productList" :key="item.id" :label="item.name + '（' + item.code + '）'"
              :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本" prop="version">
          <el-select v-model="form.version" placeholder="请选择版本" style="width:100%">
            <el-option v-for="v in ['A', 'B', 'C', 'D', 'E', 'F', 'G']" :key="v" :label="v" :value="v" />
          </el-select>
        </el-form-item>
        <el-form-item label="BOM名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" />
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

const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const search = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('新增BOM')
const form = reactive({
  id: null,
  product: null,
  name: '',
  version: '',
  description: ''
})
const rules = {
  product: [{ required: true, message: '请选择产品', trigger: 'change' }],
  name: [{ required: true, message: '请输入BOM名称', trigger: 'blur' }],
  version: [{ required: true, message: '请输入版本', trigger: 'blur' }]
}
const formRef = ref()
const productList = ref<any[]>([])

async function fetchProductList() {
  const res = await axios.get('/api/products/', { params: { page_size: 999 } })
  productList.value = res.data.results || res.data
}
function updatNameByProductAndVersion() {
  const product = productList.value.find(p => p.id === form.product)
  if (product && form.version) {
    form.name = product.code + '-' + form.version
  } else {
    form.name = ''
  }
  if (form.description == '' && form.name !== '') {
    form.description = product.code + '-' + product.name + '-' + form.version
  }
}

// 监听产品和版本变化，自动生成code
import { watch } from 'vue'
watch(() => [form.product, form.version], updatNameByProductAndVersion)

function fetchData() {
  axios.get('/api/boms/', {
    params: {
      page: page.value,
      search: search.value
    }
  }).then(res => {
    list.value = res.data.results || res.data
    total.value = res.data.count || res.data.length
  })
}
async function openDialog(row?: any) {
  if (productList.value.length === 0) {
    await fetchProductList();
  }
  if (row && row.id) {
    dialogTitle.value = '编辑BOM';
    Object.assign(form, { id: null, product: null, name: '', version: '', description: '' });
    Object.assign(form, row);
    if (row.product) {
      form.product = typeof row.product === 'string' ? Number(row.product) : row.product;
    } else {
      form.product = null;
    }
  } else {
    dialogTitle.value = '新增BOM';
    Object.assign(form, { id: null, product: null, name: '', version: '', description: '' });
  }
  dialogVisible.value = true;
}
function submit() {
  (formRef.value as any).validate(async (valid: boolean) => {
    if (!valid) return
    const isEdit = !!form.id
    const data = {
      product: form.product,
      name: form.name,
      version: form.version,
      description: form.description
    }
    try {
      if (isEdit) {
        await axios.patch(`/api/boms/${form.id}/`, data)
        ElMessage.success('修改成功')
      } else {
        await axios.post('/api/boms/', data)
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
  ElMessageBox.confirm('确定要删除该BOM吗？', '提示', { type: 'warning' })
    .then(async () => {
      await axios.delete(`/api/boms/${row.id}/`)
      ElMessage.success('删除成功')
      fetchData()
    })
}
onMounted(() => {
  fetchData()
  fetchProductList()
})
</script>
<style>
@import '/src/style.css';
</style>
