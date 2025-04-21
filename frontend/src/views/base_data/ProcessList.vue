<template>
  <el-card style="width:100%">
    <div style="display:flex;flex-direction:column;gap:8px;">
      <h2 style="margin-bottom:0;text-align:left;font-size:18px;font-weight:500;">工序管理</h2>
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <el-input v-model="search" placeholder="搜索工序名称/代码" style="width:220px;margin-right:8px;" clearable />
        <el-button type="primary" @click="openAddDialog">新增工序</el-button>
      </div>
    </div>
    <el-table :data="filteredProcesses" style="width: 100%; margin-top: 12px" :loading="loading">
      <el-table-column prop="code" label="工序代码" min-width="120" />
      <el-table-column prop="name" label="工序名称" min-width="180" />
      <el-table-column prop="description" label="工序描述" min-width="200" />
      <el-table-column prop="created_at" label="创建时间" min-width="160" />
      <el-table-column prop="updated_at" label="更新时间" min-width="160" />
      <el-table-column label="操作" :min-width="140">
        <template #default="scope">
          <div style="display: flex; gap: 8px; flex-wrap: nowrap;">
            <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteProcess(scope.row.id)">删除</el-button>
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
    <el-dialog v-model="showAdd" title="新增工序" width="400px" @close="closeAddDialog">
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item label="工序代码">
          <el-input v-model="form.code" maxlength="20" show-word-limit style="width: 260px" />
        </el-form-item>
        <el-form-item label="工序名称">
          <el-input v-model="form.name" maxlength="50" show-word-limit style="width: 260px" />
        </el-form-item>
        <el-form-item label="工序描述">
          <el-input v-model="form.description" type="textarea" :rows="3" maxlength="200" show-word-limit style="width: 260px" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeAddDialog">取消</el-button>
        <el-button type="primary" @click="saveProcess">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showEdit" title="编辑工序" width="400px" @close="closeEditDialog">
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item label="工序代码">
          <el-input v-model="form.code" maxlength="20" show-word-limit style="width: 260px" />
        </el-form-item>
        <el-form-item label="工序名称">
          <el-input v-model="form.name" maxlength="50" show-word-limit style="width: 260px" />
        </el-form-item>
        <el-form-item label="工序描述">
          <el-input v-model="form.description" type="textarea" :rows="3" maxlength="200" show-word-limit style="width: 260px" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeEditDialog">取消</el-button>
        <el-button type="primary" @click="updateProcess">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
const loading = ref(false)
const processes = ref([])
const showAdd = ref(false)
const showEdit = ref(false)
const form = reactive({ id: null, code: '', name: '', description: '' })
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const search = ref('')
const filteredProcesses = computed(() => {
  if (!search.value) return processes.value
  return processes.value.filter(p =>
    (p.name && p.name.includes(search.value)) ||
    (p.code && p.code.includes(search.value))
  )
})
const fetchProcesses = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/processes/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    processes.value = res.data.results
    total.value = res.data.count
  } finally {
    loading.value = false
  }
}
const openAddDialog = () => {
  form.id = null
  form.code = ''
  form.name = ''
  form.description = ''
  showAdd.value = true
}
const openEditDialog = (row) => {
  form.id = row.id
  form.code = row.code
  form.name = row.name
  form.description = row.description
  showEdit.value = true
}
const closeAddDialog = () => {
  showAdd.value = false
  form.id = null
  form.code = ''
  form.name = ''
  form.description = ''
}
const closeEditDialog = () => {
  showEdit.value = false
  form.id = null
  form.code = ''
  form.name = ''
  form.description = ''
}
const saveProcess = async () => {
  if (!form.code || !form.name) {
    ElMessage.error('工序代码和名称不能为空')
    return
  }
  try {
    loading.value = true
    await axios.post('/api/processes/', {
      code: form.code,
      name: form.name,
      description: form.description
    })
    ElMessage.success('新增成功')
    closeAddDialog()
    fetchProcesses()
  } catch (e) {
    ElMessage.error('新增失败')
  } finally {
    loading.value = false
  }
}
const updateProcess = async () => {
  if (!form.code || !form.name) {
    ElMessage.error('工序代码和名称不能为空')
    return
  }
  try {
    loading.value = true
    await axios.put(`/api/processes/${form.id}/`, {
      code: form.code,
      name: form.name,
      description: form.description
    })
    ElMessage.success('修改成功')
    closeEditDialog()
    fetchProcesses()
  } catch (e) {
    ElMessage.error('修改失败')
  } finally {
    loading.value = false
  }
}
const deleteProcess = async (id) => {
  try {
    loading.value = true
    await axios.delete(`/api/processes/${id}/`)
    ElMessage.success('删除成功')
    fetchProcesses()
  } catch (e) {
    ElMessage.error('删除失败')
  } finally {
    loading.value = false
  }
}
function handlePageChange(val) {
  currentPage.value = val
  fetchProcesses()
}
function handleSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
  fetchProcesses()
}
onMounted(fetchProcesses)
</script>
<style scoped>
.el-card {
  width: 100%;
  box-sizing: border-box;
  padding: 0 8px;
  background: #fff;
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
h2 {
  margin-bottom: 0;
  text-align: left;
  font-size: 18px;
  font-weight: 500;
}
</style>
