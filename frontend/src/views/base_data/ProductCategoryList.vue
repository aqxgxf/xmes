<template>
  <div class="page-container">
    <h2>产品类管理</h2>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
      <div></div>
      <el-button type="primary" @click="openAddDialog">新增产品类</el-button>
    </div>
    <el-table :data="categories" style="width: 100%; margin-top: 0" v-loading="loading">
      <el-table-column prop="name" label="产品类名称" />
      <el-table-column prop="company" label="公司" />
      <el-table-column prop="drawing_pdf" label="图纸PDF">
        <template #default="scope">
          <a v-if="scope.row.drawing_pdf" :href="scope.row.drawing_pdf" target="_blank">查看/下载</a>
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
        <el-form-item label="产品类名称">
          <el-input v-model="form.name" maxlength="10" show-word-limit />
        </el-form-item>
        <el-form-item label="公司">
          <el-input v-model="form.company" maxlength="20" show-word-limit />
        </el-form-item>
        <el-form-item label="图纸PDF">
          <input type="file" accept="application/pdf" @change="onFileChange($event, 'add')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeAddDialog">取消</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showEdit" title="编辑产品类" @close="closeEditDialog" width="400px">
      <el-form :model="form" label-width="100px" label-position="left" enctype="multipart/form-data">
        <el-form-item label="产品类名称">
          <el-input v-model="form.name" maxlength="10" show-word-limit />
        </el-form-item>
        <el-form-item label="公司">
          <el-input v-model="form.company" maxlength="20" show-word-limit />
        </el-form-item>
        <el-form-item label="图纸PDF">
          <input type="file" accept="application/pdf" @change="onFileChange($event, 'edit')" />
          <div v-if="form.drawing_pdf">
            <a :href="form.drawing_pdf" target="_blank">当前文件</a>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeEditDialog">取消</el-button>
        <el-button type="primary" @click="updateCategory">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
const loading = ref(false)
const categories = ref([])
const showAdd = ref(false)
const showEdit = ref(false)
const form = reactive({ id: null, name: '', company: '', drawing_pdf: '' })
const fileAdd = ref(null)
const fileEdit = ref(null)

const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

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
  if (type === 'add') fileAdd.value = file
  if (type === 'edit') fileEdit.value = file
}
// 新增和编辑成功后跳转第一页并刷新
const saveCategory = async () => {
  try {
    loading.value = true
    const formData = new FormData()
    formData.append('name', form.name)
    formData.append('company', form.company)
    if (fileAdd.value) formData.append('drawing_pdf', fileAdd.value)
    await axios.post('/api/product-categories/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('新增成功')
    closeAddDialog()
    currentPage.value = 1
    await fetchCategories()
    fileAdd.value = null
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
  showAdd.value = true
  fileAdd.value = null
}
const openEditDialog = (row) => {
  form.id = row.id
  form.name = row.name
  form.company = row.company
  form.drawing_pdf = row.drawing_pdf
  showEdit.value = true
  fileEdit.value = null
}
const closeAddDialog = () => {
  showAdd.value = false
  form.id = null
  form.name = ''
  form.company = ''
  form.drawing_pdf = ''
}
const closeEditDialog = () => {
  showEdit.value = false
  form.id = null
  form.name = ''
  form.company = ''
  form.drawing_pdf = ''
}
const updateCategory = async () => {
  try {
    loading.value = true
    const formData = new FormData()
    formData.append('name', form.name)
    formData.append('company', form.company)
    if (fileEdit.value) formData.append('drawing_pdf', fileEdit.value)
    await axios.put(`/api/product-categories/${form.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('修改成功')
    closeEditDialog()
    currentPage.value = 1
    await fetchCategories()
    fileEdit.value = null
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
onMounted(fetchCategories)
</script>
<style scoped>
.page-container {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  min-height: 0;
  height: calc(100vh - 32px);
  margin: 0;
  background: #fff;
  padding: 0 8px;
  border-radius: 0;
  box-shadow: none;
  display: flex;
  flex-direction: column;
}
.table-pagination {
  display: flex;
  justify-content: center;
  margin: 16px 0 0 0;
}
.el-table {
  flex: 1 1 0%;
  min-height: 0;
  width: 100%;
  overflow: auto;
}
h2 { margin-bottom: 18px; text-align: center; }
</style>
