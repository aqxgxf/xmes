<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">产品类管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-input v-model="search" placeholder="搜索产品类名称" style="width:220px;margin-right:8px;" clearable />
        <el-button type="primary" @click="openAddDialog">新增产品类</el-button>
      </div>
    </div>
    <el-table :data="filteredCategories" style="width: 100%; margin-top: 12px" v-loading="loading">
      <el-table-column prop="name" label="产品类名称" />
      <el-table-column prop="company_name" label="公司" />
      <el-table-column prop="drawing_pdf" label="图纸PDF">
        <template #default="scope">
          <a v-if="scope.row.drawing_pdf" :href="scope.row.drawing_pdf.replace(/\/$/, '')" target="_blank">查看/下载</a>
          <span v-else style="color:#aaa">无</span>
        </template>
      </el-table-column>
      <el-table-column prop="process_pdf" label="工艺PDF">
  <template #default="scope">
    <a v-if="scope.row.process_pdf" :href="scope.row.process_pdf" target="_blank">查看/下载</a>
    <span v-else style="color:#aaa">无</span>
  </template>
</el-table-column>
      <el-table-column label="操作" :min-width="140">
        <template #default="scope">
          <div style="display: flex; gap: 8px; flex-wrap: nowrap;">
            <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteCategory(scope.row.id)">删除</el-button>
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
    <el-dialog v-model="showAdd" title="新增产品类" @close="closeAddDialog" width="400px">
      <el-form :model="form" label-width="100px" label-position="left" enctype="multipart/form-data">
        <div style="display: flex; gap: 16px;">
          <el-form-item label="产品类名称" style="flex:1;">
            <el-input v-model="form.name" maxlength="10" show-word-limit />
          </el-form-item>
          <el-form-item label="公司" style="flex:1;">
            <el-select v-model="form.company" filterable>
              <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="图纸PDF">
          <input type="file" accept="application/pdf" @change="onFileChange($event, 'add')" />
          <div v-if="pdfPreviewUrlAdd" style="margin-top:8px">
            <iframe :src="pdfPreviewUrlAdd ? pdfPreviewUrlAdd + '#zoom=page-width' : ''" width="100%" height="300px" style="border:1px solid #eee"></iframe>
          </div>
        </el-form-item>
        <el-form-item label="工艺PDF">
          <input type="file" accept="application/pdf" @change="onProcessFileChange($event, 'add')" />
          <div v-if="processPdfPreviewUrlAdd" style="margin-top:8px">
            <iframe :src="processPdfPreviewUrlAdd ? processPdfPreviewUrlAdd + '#zoom=page-width' : ''" width="100%" height="300px" style="border:1px solid #eee"></iframe>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeAddDialog">取消</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog
  v-model="showEdit"
  title="编辑产品类"
  @close="closeEditDialog"
  width="90vw"
  top="2vh"
  fullscreen
  :modal="true"
  :lock-scroll="false"
  :close-on-click-modal="false"
  :show-close="true"
  class="edit-dialog-no-scroll"
>
      <div style="display:flex;flex-direction:column;height:100%;box-sizing:border-box;">
        <div style="flex:1 1 auto;overflow:auto;min-height:0;padding-bottom:0;box-sizing:border-box;">
          <el-form :model="form" label-width="100px" label-position="left" enctype="multipart/form-data">
            <div style="display: flex; gap: 16px;">
              <el-form-item label="产品类名称" style="flex:1;">
                <el-input v-model="form.name" maxlength="10" show-word-limit />
              </el-form-item>
              <el-form-item label="公司" style="flex:1;">
                <el-select v-model="form.company" filterable>
                  <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
                </el-select>
              </el-form-item>
            </div>
            <el-form-item label="图纸PDF">
              <input type="file" accept="application/pdf" @change="onFileChange($event, 'edit')" ref="drawingFileInputEdit" />
              <div v-if="form.drawing_pdf">
                <a :href="form.drawing_pdf" target="_blank">当前文件</a>
                <iframe v-if="form.drawing_pdf.endsWith('.pdf') && !pdfPreviewUrlEdit" :src="form.drawing_pdf.replace(/\/$/, '') + '#toolbar=0&view=fitH'" style="border:1px solid #eee;margin-top:8px;min-height:55vh;height:80vh;width:100vw;max-width:100%;"></iframe>
              </div>
              <div v-if="pdfPreviewUrlEdit" style="margin-top:8px">
                <iframe :src="pdfPreviewUrlEdit ? pdfPreviewUrlEdit + '#zoom=page-width' : ''" style="border:1px solid #eee;min-height:55vh;height:80vh;width:100vw;max-width:100%;"></iframe>
              </div>
            </el-form-item>
            <el-form-item label="工艺PDF">
              <input type="file" accept="application/pdf" @change="onProcessFileChange($event, 'edit')" ref="processFileInputEdit" />
              <div v-if="form.process_pdf">
                <a :href="form.process_pdf" target="_blank">当前文件</a>
                <iframe v-if="form.process_pdf.endsWith('.pdf') && !processPdfPreviewUrlEdit" :src="form.process_pdf.replace(/\/$/, '') + '#toolbar=0&view=fitH'" style="border:1px solid #eee;margin-top:8px;min-height:55vh;height:80vh;width:100vw;max-width:100%;"></iframe>
              </div>
              <div v-if="processPdfPreviewUrlEdit" style="margin-top:8px">
                <iframe :src="processPdfPreviewUrlEdit ? processPdfPreviewUrlEdit + '#zoom=page-width' : ''" style="border:1px solid #eee;min-height:55vh;height:80vh;width:100vw;max-width:100%;"></iframe>
              </div>
            </el-form-item>
          </el-form>
        </div>
        <div style="flex-shrink:0;display:flex;justify-content:flex-end;gap:12px;padding:12px 24px 12px 24px;background:#fff;box-sizing:border-box;height:56px;align-items:center;">
      <el-button @click="closeEditDialog">取消</el-button>
      <el-button type="primary" @click="updateCategory">保存</el-button>
    </div>
      </div>
    </el-dialog>
  </el-card>
</template>
<script setup>
import { nextTick, ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
const loading = ref(false)
const categories = ref([])
const search = ref('')
const filteredCategories = computed(() => {
  if (!search.value) return categories.value
  return categories.value.filter(c => c.name && c.name.toLowerCase().includes(search.value.toLowerCase()))
})
const showAdd = ref(false)
const showEdit = ref(false)
const form = reactive({ id: null, name: '', company: '', drawing_pdf: '', process_pdf: '' })
const fileAdd = ref(null)
const fileEdit = ref(null)
const fileProcessAdd = ref(null)
const fileProcessEdit = ref(null)
const pdfPreviewUrlAdd = ref('')
const pdfPreviewUrlEdit = ref('')
const processPdfPreviewUrlAdd = ref('')
const processPdfPreviewUrlEdit = ref('')

// 新增：用于重置文件input
const drawingFileInputEdit = ref(null)
const processFileInputEdit = ref(null)

const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const companies = ref([])
const fetchCompanies = async () => {
  const res = await axios.get('/api/companies/')
  companies.value = res.data
}

const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/product-categories/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    categories.value = res.data.results
    total.value = res.data.count
    // 如果当前页>1且无数据且总数>0，自动跳转第一页
    if (currentPage.value > 1 && categories.value.length === 0 && total.value > 0) {
      currentPage.value = 1
      await fetchCategories()
    }
    // 如果第一页且无数据，直接显示空表
  } finally {
    loading.value = false
  }
}
function handlePageChange(val) {
  currentPage.value = val
  fetchCategories()
}
function handleSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
  fetchCategories()
}

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
const onProcessFileChange = (e, type) => {
  const file = e.target.files[0]
  if (type === 'add') {
    fileProcessAdd.value = file
    processPdfPreviewUrlAdd.value = file ? URL.createObjectURL(file) : ''
  }
  if (type === 'edit') {
    fileProcessEdit.value = file
    processPdfPreviewUrlEdit.value = file ? URL.createObjectURL(file) : ''
  }
}
// 新增和编辑成功后跳转第一页并刷新
const saveCategory = async () => {
  try {
    loading.value = true
    const formData = new FormData()
    formData.append('name', form.name)
    formData.append('company', form.company)
    if (fileAdd.value) formData.append('drawing_pdf', fileAdd.value)
    if (fileProcessAdd.value) formData.append('process_pdf', fileProcessAdd.value)
    await axios.post('/api/product-categories/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('新增成功')
    closeAddDialog()
    currentPage.value = 1
    await fetchCategories()
    fileAdd.value = null
    fileProcessAdd.value = null
  } catch (e) {
    ElMessage.error('新增失败')
  } finally {
    loading.value = false
  }
}
const openAddDialog = () => {
  form.id = null
  form.name = ''
  form.company = ''
  form.drawing_pdf = ''
  form.process_pdf = ''
  showAdd.value = true
  fileAdd.value = null
  fileProcessAdd.value = null
}
const openEditDialog = (row) => {
  form.id = row.id
  form.name = row.name
  form.company = row.company
  form.drawing_pdf = row.drawing_pdf || ''
  form.process_pdf = row.process_pdf || ''
  showEdit.value = true
  fileEdit.value = null
  fileProcessEdit.value = null
}
const closeAddDialog = () => {
  showAdd.value = false
  form.id = null
  form.name = ''
  form.company = ''
  form.drawing_pdf = ''
  form.process_pdf = ''
  pdfPreviewUrlAdd.value = ''
  processPdfPreviewUrlAdd.value = ''
  fileAdd.value = null
  fileProcessAdd.value = null
}
const closeEditDialog = () => {
  showEdit.value = false
  form.id = null
  form.name = ''
  form.company = ''
  form.drawing_pdf = ''
  form.process_pdf = ''
  pdfPreviewUrlEdit.value = ''
  processPdfPreviewUrlEdit.value = ''
  fileEdit.value = null
  fileProcessEdit.value = null
  nextTick(() => {
    if (drawingFileInputEdit.value) drawingFileInputEdit.value.value = ''
    if (processFileInputEdit.value) processFileInputEdit.value.value = ''
  })
}
const updateCategory = async () => {
  try {
    loading.value = true
    const formData = new FormData()
    formData.append('name', form.name)
    formData.append('company', form.company)
    if (fileEdit.value) formData.append('drawing_pdf', fileEdit.value)
    if (fileProcessEdit.value) formData.append('process_pdf', fileProcessEdit.value)
    await axios.put(`/api/product-categories/${form.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('修改成功')
    closeEditDialog()
    currentPage.value = 1
    await fetchCategories()
    fileEdit.value = null
    fileProcessEdit.value = null
  } catch (e) {
    ElMessage.error('修改失败')
  } finally {
    loading.value = false
  }
}
const deleteCategory = async (id) => {
  try {
    loading.value = true
    await axios.delete(`/api/product-categories/${id}/`)
    ElMessage.success('删除成功')
    fetchCategories()
  } catch (e) {
    ElMessage.error('删除失败')
  } finally {
    loading.value = false
  }
}
onMounted(async () => {
  await fetchCompanies()
  await fetchCategories()
})
</script>
<style>
@import '/src/style.css';
</style>
