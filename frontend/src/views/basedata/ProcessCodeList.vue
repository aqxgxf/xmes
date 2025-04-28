<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">工艺流程代码管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-input v-model="search" placeholder="搜索代码/说明/版本" style="width: 300px;" clearable @input="fetchData"/>
        <el-button type="primary" @click="openDialog({})">新增工艺流程代码</el-button>
      </div>
    </div>
    <el-table :data="list" border style="width: 100%;margin-top:16px;">
      <el-table-column prop="code" label="工艺流程代码" width="280"/>
      <el-table-column prop="description" label="说明"/>
      <el-table-column prop="version" label="版本" width="120"/>
      <el-table-column prop="created_at" label="创建时间" width="180"/>
      <el-table-column prop="updated_at" label="更新时间" width="180"/>
      <el-table-column label="工艺PDF" width="120">
        <template #default="scope">
          <el-link v-if="scope.row.process_pdf" :href="scope.row.process_pdf" target="_blank">查看</el-link>
          <span v-else>无</span>
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
      :current-page.sync="page"
      :page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="fetchData"
      style="margin-top: 16px; text-align: right;"
    />
    <el-dialog :title="dialogTitle" v-model="dialogVisible">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" enctype="multipart/form-data">
        <el-form-item label="产品" prop="product">
          <el-select v-model="form.product" placeholder="请选择产品" filterable style="width:100%">
            <el-option v-for="item in productList" :key="item.id" :label="item.name + '（' + item.code + '）'" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="说明" prop="description">
          <el-input v-model="form.description"/>
        </el-form-item>
        <el-form-item label="版本" prop="version">
          <el-select v-model="form.version" placeholder="请选择版本" style="width:100%">
            <el-option v-for="v in ['A','B','C','D','E','F','G']" :key="v" :label="v" :value="v" />
          </el-select>
        </el-form-item>
        <el-form-item label="工艺流程代码" prop="code">
          <el-input v-model="form.code"/>
        </el-form-item>
        <el-form-item label="工艺PDF">
          <el-upload
            :file-list="pdfFileList"
            :auto-upload="false"
            :limit="1"
            accept=".pdf"
            :on-change="onPdfChange"
            :on-remove="onPdfRemove"
            :show-file-list="true"
          >
            <el-button size="small" type="primary">选择PDF</el-button>
          </el-upload>
          <template v-if="form.process_pdf">
            <el-link :href="form.process_pdf" target="_blank" type="primary" style="margin-left: 8px;">已上传PDF</el-link>
          </template>
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

const list = ref<{ id: number; [key: string]: any }[]>([])
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
  version: '',
  process_pdf: '',
  product: null
})
const rules = {
  code: [{ required: true, message: '请输入工艺流程代码', trigger: 'blur' }],
  version: [{ required: true, message: '请输入版本', trigger: 'blur' }]
}
const formRef = ref()
const pdfFileList = ref<any[]>([])
const productList = ref<any[]>([])

async function fetchProductList() {
  const res = await axios.get('/api/products/', { params: { page_size: 999 } })
  productList.value = res.data.results || res.data
}

function updateCodeByProductAndVersion() {
  const product = productList.value.find(p => p.id === form.product)
  if (product && form.version) {
    form.code = product.code + '-' + form.version
  } else {
    form.code = ''
  }
  if (form.description== '' && form.code !== '') {
    form.description = product.code + '-' + product.name + '-' + form.version
  }
}

// 监听产品和版本变化，自动生成code
import { watch } from 'vue'
watch(() => [form.product, form.version], updateCodeByProductAndVersion)

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
async function openDialog(row?: any) {
  if (productList.value.length === 0) {
    await fetchProductList();
  }
  // 兼容el-table row丢失字段的情况，优先用id查找原始数据
  let realRow = row;
  if (row && row.id && (row.product === undefined || row.product === null)) {
    const found = list.value.find(item => item.id === row.id);
    if (found) realRow = found;
  }
  setFormProduct(realRow);
}

function setFormProduct(row?: any) {
console.log('row.product', row.product)
  if (row) {
    dialogTitle.value = '编辑工艺流程代码';
    // 先清空form，防止响应式污染
    Object.assign(form, { id: null, code: '', description: '', version: '', process_pdf: '', product: null });
    // 赋值，确保类型一致
    Object.assign(form, row);
    if (row.product) {
      // 兼容字符串和数字
      form.product = typeof row.product === 'string' ? Number(row.product) : row.product;
    } else {
      form.product = null;
    }
    // 赋值后手动触发一次工艺流程代码生成，确保code和下拉框都能正确显示
    updateCodeByProductAndVersion();
    pdfFileList.value = [];
  } else {
    dialogTitle.value = '新增工艺流程代码';
    Object.assign(form, { id: null, code: '', description: '', version: '', process_pdf: '', product: null });
    pdfFileList.value = [];
  }
  dialogVisible.value = true;
}

function onPdfChange(file: any) {
  pdfFileList.value = [file]
}
function onPdfRemove() {
  pdfFileList.value = []
  form.process_pdf = ''
}
function submit() {
  (formRef.value as any).validate(async (valid: boolean) => {
    if (!valid) return
    const isEdit = !!form.id
    const formData = new FormData()
    formData.append('code', form.code)
    formData.append('description', form.description)
    formData.append('version', form.version)
    if (pdfFileList.value.length > 0) {
      formData.append('process_pdf', pdfFileList.value[0].raw)
    }
    let processCodeId = form.id
    try {
      if (isEdit) {
        // PATCH 支持部分更新
        await axios.patch(`/api/process-codes/${form.id}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        processCodeId = form.id
        ElMessage.success('修改成功')
      } else {
        const res = await axios.post('/api/process-codes/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        processCodeId = res.data.id
        ElMessage.success('新增成功')
      }
      // 保存产品-工艺流程代码关系
      if (form.product && processCodeId) {
        await axios.post('/api/product-process-codes/', {
          product: form.product,
          process_code: processCodeId,
          is_default: true
        })
      }
      dialogVisible.value = false
      fetchData()
    } catch (e) {
      // 输出后端详细错误
      console.error((e as any)?.response?.data || e)
      ElMessage.error('保存失败: ' + ((e as any)?.response?.data?.detail || JSON.stringify((e as any)?.response?.data) || (e as any).message || '未知错误'))
    }
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
onMounted(() => {
  fetchData()
  fetchProductList()
})
</script>
<style>
@import '/src/style.css';
</style>
