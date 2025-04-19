<template>
  <div class="page-container">
    <h2>参数项管理</h2>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
      <el-form inline style="margin:0;">
        <el-form-item label="产品类">
          <el-select v-model="selectedCategory" @change="fetchParams" style="width: 200px">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <el-button type="primary" @click="openAddDialog" :disabled="!selectedCategory">新增参数项</el-button>
    </div>
    <el-table :data="params" style="width: 100%; margin-top: 0" v-loading="loading">
      <el-table-column prop="name" label="参数项名称" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteParam(scope.row.id)">删除</el-button>
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
    <el-dialog v-model="showAdd" title="新增参数项" @close="closeAddDialog">
      <el-form :model="form">
        <el-form-item label="参数项名称">
          <el-input v-model="form.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeAddDialog">取消</el-button>
        <el-button type="primary" @click="saveParam">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showEdit" title="编辑参数项" @close="closeEditDialog">
      <el-form :model="form">
        <el-form-item label="参数项名称">
          <el-input v-model="form.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeEditDialog">取消</el-button>
        <el-button type="primary" @click="updateParam">保存</el-button>
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
const params = ref([])
const selectedCategory = ref(null)
const showAdd = ref(false)
const showEdit = ref(false)
const form = reactive({ id: null, name: '' })
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const fetchCategories = async () => {
  loading.value = true
  const res = await axios.get('/api/product-categories/')
  categories.value = res.data
  loading.value = false
  // 自动选中第一个产品类并加载参数项
  if (categories.value && categories.value.length > 0) {
    if (!selectedCategory.value) {
      selectedCategory.value = categories.value[0].id
      await fetchParams()
    }
  } else {
    params.value = []
    total.value = 0
  }
}
const fetchParams = async () => {
  if (!selectedCategory.value) { params.value = []; total.value = 0; return }
  loading.value = true
  try {
    const res = await axios.get(`/api/product-categories/${selectedCategory.value}/params/`, {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    params.value = res.data.results
    total.value = res.data.count
  } finally {
    loading.value = false
  }
}
const openAddDialog = () => {
  form.id = null
  form.name = ''
  showAdd.value = true
}
const openEditDialog = (row) => {
  form.id = row.id
  form.name = row.name
  showEdit.value = true
}
const closeAddDialog = () => {
  showAdd.value = false
  form.id = null
  form.name = ''
}
const closeEditDialog = () => {
  showEdit.value = false
  form.id = null
  form.name = ''
}
const saveParam = async () => {
  if (params.value.some(p => p.name === form.name)) {
    ElMessage.error('该产品类下参数项名称已存在！')
    return
  }
  try {
    loading.value = true
    await axios.post('/api/category-params/', { name: form.name, category: selectedCategory.value })
    ElMessage.success('新增成功')
    closeAddDialog()
    fetchParams()
  } catch (e) {
    ElMessage.error('新增失败')
  } finally {
    loading.value = false
  }
}
const updateParam = async () => {
  try {
    loading.value = true
    await axios.put(`/api/category-params/${form.id}/`, { name: form.name, category: selectedCategory.value })
    ElMessage.success('修改成功')
    closeEditDialog()
    fetchParams()
  } catch (e) {
    ElMessage.error('修改失败')
  } finally {
    loading.value = false
  }
}
const deleteParam = async (id) => {
  try {
    loading.value = true
    await axios.delete(`/api/category-params/${id}/`)
    ElMessage.success('删除成功')
    fetchParams()
  } catch (e) {
    ElMessage.error('删除失败')
  } finally {
    loading.value = false
  }
}
function handlePageChange(val) {
  currentPage.value = val
  fetchParams()
}
function handleSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
  fetchParams()
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
