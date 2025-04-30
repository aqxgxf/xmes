<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">产品管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-input v-model="search" placeholder="搜索产品名称" style="width:220px;margin-right:8px;" clearable />
        <el-button type="primary" @click="openAddDialog">新增产品</el-button>
        <el-upload
          :show-file-list="false"
          :before-upload="beforeImport"
          :http-request="handleImport"
          accept=".xlsx,.xls,.csv"
        >
          <el-button type="success">导入</el-button>
        </el-upload>
      </div>
    </div>
    <el-table :data="filteredProducts" style="width: 100%; margin-top: 12px" :loading="loading">
      <el-table-column prop="code" label="产品代码" min-width="120" />
      <el-table-column prop="name" label="产品名称" min-width="200" />
      <el-table-column prop="price" label="价格" min-width="100" />
      <el-table-column prop="category_name" label="产品类" min-width="120" />
      <el-table-column prop="drawing_pdf_url" label="图纸PDF">
        <template #default="scope">
          <a v-if="scope.row.drawing_pdf_url" :href="scope.row.drawing_pdf_url.replace(/\/$/, '')" target="_blank">查看/下载</a>
          <span v-else style="color:#aaa">无</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" :min-width="140">
        <template #default="scope">
          <div style="display: flex; gap: 8px; flex-wrap: nowrap;">
            <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteProduct(scope.row.id)">删除</el-button>
          </div>
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
    <el-dialog v-model="showAdd" title="新增产品" width="80vw" @close="closeAddDialog">
      <el-form :model="form" label-width="100px" label-position="left" enctype="multipart/form-data">
        <el-form-item label="产品类">
          <el-select v-model="form.category" @change="onCategoryChange" style="width: 280px">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品代码">
          <el-input v-model="form.code" maxlength="100" show-word-limit style="width: 280px" />
        </el-form-item>
        <el-form-item label="产品名称">
          <el-input v-model="form.name" maxlength="40" show-word-limit style="width: 280px" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input v-model="form.price" type="number" style="width: 180px" />
        </el-form-item>
        <el-form-item v-for="param in params" :key="param.id" :label="param.name" :required="true">
          <el-input v-model="form.paramValues[param.id]" style="width: 280px" />
        </el-form-item>
        <el-form-item label="图纸PDF">
          <input type="file" accept="application/pdf" @change="onFileChange($event, 'add')" ref="drawingFileInputAdd" />
          <div v-if="pdfPreviewUrlAdd" style="margin-top:8px">
            <iframe :src="pdfPreviewUrlAdd ? pdfPreviewUrlAdd + '#zoom=page-width' : ''" style="border:1px solid #eee;margin-top:8px;min-height:55vh;height:80vh;width:100vw;max-width:100%;"></iframe>
          </div>

        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeAddDialog">取消</el-button>
        <el-button type="primary" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showEdit" title="编辑产品" width="500px" @close="closeEditDialog" @opened="onEditDialogOpened">
      <el-form :model="form" label-width="100px" label-position="left" enctype="multipart/form-data">
        <el-form-item label="产品类">
          <el-select v-model="form.category" @change="onCategoryChange" style="width: 280px">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品代码">
          <el-input v-model="form.code" maxlength="100" show-word-limit style="width: 280px" />
        </el-form-item>
        <el-form-item label="产品名称">
          <el-input v-model="form.name" maxlength="40" show-word-limit style="width: 280px" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input v-model="form.price" type="number" style="width: 180px" />
        </el-form-item>
        <el-form-item v-for="param in params" :key="param.id" :label="param.name" :required="true">
          <el-input v-model="form.paramValues[param.id]" style="width: 280px" />
        </el-form-item>
        <el-form-item label="图纸PDF">
          <input type="file" accept="application/pdf" @change="onFileChange($event, 'edit')" ref="fileEditInput" v-if="showEdit" />
          <div v-if="form.drawing_pdf_url">
            <a :href="form.drawing_pdf_url.replace(/\/$/, '')" target="_blank">当前文件</a>
          </div>
          <div v-if="fileEdit.value">
            <iframe :src="fileEdit.value ? URL.createObjectURL(fileEdit.value) + '#zoom=page-width' : ''" style="border:1px solid #eee;margin-top:8px;min-height:55vh;height:60vh;width:100vw;max-width:100%;"></iframe>
          </div>
          <div v-else-if="form.drawing_pdf_url">
            <iframe :src="form.drawing_pdf_url.replace(/\/$/, '') + '#zoom=page-width'" style="border:1px solid #eee;margin-top:8px;min-height:55vh;height:60vh;width:100vw;max-width:100%;"></iframe>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeEditDialog">取消</el-button>
        <el-button type="primary" @click="updateProduct">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 统一风格变量
const loading = ref(false)
const products = ref([])
const categories = ref([])
const params = ref([])
const showAdd = ref(false)
const showEdit = ref(false)
const form = reactive({
  id: null,
  code: '',
  name: '',
  price: '',
  category: '',
  paramValues: {},
  drawing_pdf_url: ''
})

const fileAdd = ref(null)
const fileEdit = ref(null)
const fileAddInput = ref(null)
const fileEditInput = ref(null)
const pdfPreviewUrlEdit = ref('')
const pdfPreviewUrlAdd = ref('')
const drawingFileInputAdd = ref(null)
const onFileChange = (e, type) => {
  const file = e.target.files[0]
  if (type === 'add') {
    fileAdd.value = file
    pdfPreviewUrlAdd.value = file ? URL.createObjectURL(file) : ''
  }
  if (type === 'edit') {
    fileEdit.value = file
    pdfPreviewUrlEdit.value = file ? URL.createObjectURL(file) : ''
  }
}

const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const search = ref('')

const filteredProducts = computed(() => products.value) // 后端分页，直接用products

const fetchProducts = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/products/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: search.value // 搜索参数传递给后端
      }
    })
    products.value = res.data.results.map(p => ({
      ...p,
      category_name: categories.value.find(c => c.id === p.category)?.name || '',
      drawing_pdf_url: p.drawing_pdf_url
    }))
    total.value = res.data.count
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  const res = await axios.get('/api/product-categories/')
  categories.value = res.data
}
const openAddDialog = () => {
  form.id = null
  form.code = ''
  form.name = ''
  form.price = ''
  form.category = ''
  form.paramValues = {}
  form.drawing_pdf_url = ''
  params.value = []
  showAdd.value = true
  fileAdd.value = null
  pdfPreviewUrlAdd.value = ''
  nextTick(() => {
    if (drawingFileInputAdd.value) drawingFileInputAdd.value = ''
  })
}
const onEditDialogOpened = () => {
  console.log('onEditDialogOpened method entered')
  fileEdit.value = null
  nextTick(() => {
    fileEditInput.value = document.querySelector('input[type="file"][ref="fileEditInput"]')
    if (fileEditInput.value) {
      fileEditInput.value.value = ''
    } else {
      console.error('fileEditInput.value is null or undefined')
    }
  })
}
const openEditDialog = (row) => {
  console.log('openEditDialog called with row:', row)
  form.id = row.id
  form.code = row.code
  form.name = row.name
  form.price = row.price
  form.category = row.category
  form.drawing_pdf_url = row.drawing_pdf_url
  console.log('before onCategoryChange, form:', JSON.parse(JSON.stringify(form)))
  onCategoryChange().then(() => {
    console.log('onCategoryChange completed, params:', params.value)
    form.paramValues = {}
    if (row.param_values) {
      row.param_values.forEach(pv => {
        form.paramValues[String(pv.param)] = pv.value
      })
    }
    console.log('before show dialog, form:', JSON.parse(JSON.stringify(form)))
    showEdit.value = true
    fileEdit.value = null
  })
}
const closeAddDialog = () => {
  showAdd.value = false
  form.id = null
  form.code = ''
  form.name = ''
  form.price = ''
  form.category = ''
  form.paramValues = {}
  params.value = []
  fileAdd.value = null
  pdfPreviewUrlAdd.value = ''
  nextTick(() => {
    if (drawingFileInputAdd.value) drawingFileInputAdd.value = ''
  })
}
const closeEditDialog = () => {
  showEdit.value = false
  form.id = null
  form.code = ''
  form.name = ''
  form.price = ''
  form.category = ''
  form.paramValues = {}
  params.value = []
  fileEdit.value = null
}
const autoFillProductCode = () => {
  const cat = categories.value.find(c => c.id === form.category)
  let code = cat ? cat.name : ''
  params.value.forEach(p => {
    const val = form.paramValues[p.id]
    if (val) code += '-' + p.name + '-' + val
  })
  form.code = code
}

watch([() => form.category, () => form.paramValues], autoFillProductCode, { deep: true })

const onCategoryChange = async () => {
  if (!form.category) return
  const res = await axios.get(`/api/product-categories/${form.category}/params/`)
  params.value = res.data
  // 自动填充参数项
  form.paramValues = {}
  params.value.forEach(p => { form.paramValues[p.id] = '' })
  autoFillProductCode()
}
const saveProduct = async () => {
  for (const p of params.value) {
    if (!form.paramValues[p.id]) {
      ElMessage.error(`请填写参数项：${p.name}`)
      return
    }
  }
  const param_values = Object.entries(form.paramValues).map(([param, value]) => ({ param, value }))
  try {
    loading.value = true
    const formData = new FormData()
    formData.append('code', form.code)
    formData.append('name', form.name)
    formData.append('price', form.price)
    formData.append('category', form.category)
    if (fileAdd.value && fileAdd.value.size > 0) formData.append('drawing_pdf', fileAdd.value)
    formData.append('param_values', JSON.stringify(param_values))
    await axios.post('/api/products/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('新增成功')
    closeAddDialog()
    fetchProducts()
    fileAdd.value = null
  } catch (e) {
    ElMessage.error('新增失败')
  } finally {
    loading.value = false
  }
}
const updateProduct = async () => {
  for (const p of params.value) {
    if (!form.paramValues[p.id]) {
      ElMessage.error(`请填写参数项：${p.name}`)
      return
    }
  }
  const param_values = Object.entries(form.paramValues).map(([param, value]) => ({ param, value }))
  try {
    loading.value = true
    const formData = new FormData()
    formData.append('code', form.code)
    formData.append('name', form.name)
    formData.append('price', form.price)
    formData.append('category', form.category)
    if (fileEdit.value && fileEdit.value.size > 0) formData.append('drawing_pdf', fileEdit.value)
    formData.append('param_values', JSON.stringify(param_values))
    await axios.put(`/api/products/${form.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('修改成功')
    closeEditDialog()
    fetchProducts()
    fileEdit.value = null
  } catch (e) {
    ElMessage.error('修改失败')
  } finally {
    loading.value = false
  }
}
const deleteProduct = async (id) => {
  try {
    loading.value = true
    await axios.delete(`/api/products/${id}/`)
    ElMessage.success('删除成功')
    fetchProducts()
  } catch (e) {
    ElMessage.error('删除失败')
  } finally {
    loading.value = false
  }
}
function handlePageChange(val) {
  currentPage.value = val
  fetchProducts()
}
function handleSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
  fetchProducts()
}

watch(search, () => {
  currentPage.value = 1
  fetchProducts()
})

onMounted(async () => {
  await fetchCategories()
  await fetchProducts()
})

function beforeImport(file) {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!["xlsx", "xls", "csv"].includes(ext)) {
    ElMessage.error('仅支持Excel或CSV文件')
    return false
  }
  return true
}
async function handleImport(option) {
  const formData = new FormData()
  formData.append('file', option.file)
  try {
    const res = await axios.post('/api/products/import/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success(res.data?.msg || '导入成功')
    fetchProducts()
  } catch (e) {
    ElMessage.error(e?.response?.data?.msg || '导入失败')
  }
}
</script>

<!-- 引入全局样式 -->
<style>
@import '/src/style.css';
</style>

<!-- 移除 scoped 样式，通用样式已抽取到 style.css，如有个性化样式可在此补充 -->
