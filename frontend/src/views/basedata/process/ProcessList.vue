<template>
  <div class="process-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工序管理</h2>
          <div class="search-actions">
            <el-input
              v-model="search"
              placeholder="搜索工序名称/代码"
              clearable
              prefix-icon="Search"
              @input="handleSearch"
            />
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon> 新增工序
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 数据表格 -->
      <el-table
        :data="filteredProcesses"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="code" label="工序代码" min-width="120" />
        <el-table-column prop="name" label="工序名称" min-width="180" />
        <el-table-column prop="description" label="工序描述" min-width="200" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column prop="updated_at" label="更新时间" min-width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" @click="openEditDialog(row)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button size="small" type="danger" @click="confirmDelete(row)">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页控件 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
        />
      </div>
    </el-card>
    
    <!-- 新增工序对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增工序"
      width="500px"
      destroy-on-close
      @close="closeAddDialog"
    >
      <el-form
        ref="addFormRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="left"
        class="form-container"
      >
        <el-form-item label="工序代码" prop="code">
          <el-input
            v-model="form.code"
            maxlength="20"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="工序名称" prop="name">
          <el-input
            v-model="form.name"
            maxlength="50"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="工序描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeAddDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="saveProcess"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑工序对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑工序"
      width="500px"
      destroy-on-close
      @close="closeEditDialog"
    >
      <el-form
        ref="editFormRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="left"
        class="form-container"
      >
        <el-form-item label="工序代码" prop="code">
          <el-input
            v-model="form.code"
            maxlength="20"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="工序名称" prop="name">
          <el-input
            v-model="form.name"
            maxlength="50"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="工序描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeEditDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="updateProcess"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'
import { api } from '../../../api/index'

// 类型定义
interface Process {
  id: number;
  code: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

interface ProcessForm {
  id: number | null;
  code: string;
  name: string;
  description: string;
}

// 表单验证规则
const rules = {
  code: [
    { required: true, message: '请输入工序代码', trigger: 'blur' },
    { max: 20, message: '最大长度不能超过20个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入工序名称', trigger: 'blur' },
    { max: 50, message: '最大长度不能超过50个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '最大长度不能超过200个字符', trigger: 'blur' }
  ]
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const processes = ref<Process[]>([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const search = ref('')

// 表单对象
const form = reactive<ProcessForm>({
  id: null,
  code: '',
  name: '',
  description: ''
})

// 计算属性
const filteredProcesses = computed(() => {
  if (!search.value) return processes.value
  
  return processes.value.filter(p => 
    (p.name && p.name.toLowerCase().includes(search.value.toLowerCase())) ||
    (p.code && p.code.toLowerCase().includes(search.value.toLowerCase()))
  )
})

// 数据加载方法
const fetchProcesses = async () => {
  loading.value = true
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await api.get('/api/processes/', { params })
    
    // 处理API返回数据
    if (response.data && response.data.success === true) {
      const responseData = response.data.data || {}
      
      if (responseData && Array.isArray(responseData.results)) {
        processes.value = responseData.results
        total.value = responseData.count || 0
      } else if (responseData && Array.isArray(responseData)) {
        processes.value = responseData
        total.value = responseData.length
      } else {
        processes.value = []
        total.value = 0
      }
    } else if (response.data) {
      if (Array.isArray(response.data.results)) {
        processes.value = response.data.results
        total.value = response.data.count || 0
      } else if (Array.isArray(response.data)) {
        processes.value = response.data
        total.value = response.data.length
      } else {
        processes.value = []
        total.value = 0
      }
    } else {
      processes.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取工序列表失败:', error)
    ElMessage.error('获取工序列表失败')
    processes.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 处理事件
const handleSearch = () => {
  // 本地筛选，不需要重新加载
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchProcesses()
}

const handleCurrentChange = () => {
  fetchProcesses()
}

const confirmDelete = (row: Process) => {
  ElMessageBox.confirm(
    `确定要删除工序 "${row.name}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteProcess(row.id)
  }).catch(() => {
    // 用户取消操作
  })
}

// 对话框处理
const openAddDialog = () => {
  resetForm()
  showAddDialog.value = true
}

const openEditDialog = (row: Process) => {
  resetForm()
  
  form.id = row.id
  form.code = row.code
  form.name = row.name
  form.description = row.description || ''
  
  showEditDialog.value = true
}

const closeAddDialog = () => {
  showAddDialog.value = false
  resetForm()
}

const closeEditDialog = () => {
  showEditDialog.value = false
  resetForm()
}

const resetForm = () => {
  form.id = null
  form.code = ''
  form.name = ''
  form.description = ''
}

// 表单提交
const saveProcess = async () => {
  if (!addFormRef.value) return
  
  addFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      await api.post('/api/processes/', {
        code: form.code,
        name: form.name,
        description: form.description
      })
      
      ElMessage.success('新增工序成功')
      closeAddDialog()
      fetchProcesses()
    } catch (error: any) {
      let errorMsg = '新增工序失败'
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMsg = error.response.data
        } else if (typeof error.response.data === 'object') {
          const firstError = Object.values(error.response.data)[0]
          if (Array.isArray(firstError) && firstError.length > 0) {
            errorMsg = firstError[0] as string
          } else if (typeof firstError === 'string') {
            errorMsg = firstError
          }
        }
      }
      
      ElMessage.error(errorMsg)
      console.error('新增工序失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const updateProcess = async () => {
  if (!editFormRef.value) return
  
  editFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      await api.put(`/api/processes/${form.id}/`, {
        code: form.code,
        name: form.name,
        description: form.description
      })
      
      ElMessage.success('更新工序成功')
      closeEditDialog()
      fetchProcesses()
    } catch (error: any) {
      let errorMsg = '更新工序失败'
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMsg = error.response.data
        } else if (typeof error.response.data === 'object') {
          const firstError = Object.values(error.response.data)[0]
          if (Array.isArray(firstError) && firstError.length > 0) {
            errorMsg = firstError[0] as string
          } else if (typeof firstError === 'string') {
            errorMsg = firstError
          }
        }
      }
      
      ElMessage.error(errorMsg)
      console.error('更新工序失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteProcess = async (id: number) => {
  loading.value = true
  
  try {
    await api.delete(`/api/processes/${id}/`)
    ElMessage.success('删除工序成功')
    
    // 如果当前页删除后没有数据了，尝试跳到上一页
    if (processes.value.length === 1 && currentPage.value > 1) {
      currentPage.value--
    }
    
    fetchProcesses()
  } catch (error: any) {
    let errorMsg = '删除工序失败'
    
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (typeof error.response.data === 'object') {
        const firstError = Object.values(error.response.data)[0]
        if (Array.isArray(firstError) && firstError.length > 0) {
          errorMsg = firstError[0] as string
        } else if (typeof firstError === 'string') {
          errorMsg = firstError
        }
      }
    }
    
    ElMessage.error(errorMsg)
    console.error('删除工序失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchProcesses()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

// 工序管理特有样式
.process-container {
  .form-input {
    width: 320px;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
  }
}
</style>
