<template>
  <div class="group-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">用户组管理</h2>
          <div class="search-actions">
            <el-input
              v-model="search"
              placeholder="搜索组名"
              clearable
              prefix-icon="Search"
              @input="handleSearch"
            />
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon> 新增用户组
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 数据表格 -->
      <el-table
        :data="filteredGroups"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="组名" min-width="200" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" @click="editGroup(row)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button size="small" type="danger" @click="confirmDeleteGroup(row)">
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
    
    <!-- 新增用户组对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增用户组"
      width="500px"
      destroy-on-close
      @close="closeAddDialog"
    >
      <el-form
        ref="addFormRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        label-position="left"
        class="form-container"
      >
        <el-form-item label="组名" prop="name">
          <el-input
            v-model="form.name"
            maxlength="30"
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
          @click="addGroup"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑用户组对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑用户组"
      width="500px"
      destroy-on-close
      @close="closeEditDialog"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="rules"
        label-width="80px"
        label-position="left"
        class="form-container"
      >
        <el-form-item label="组名" prop="new_name">
          <el-input
            v-model="editForm.new_name"
            maxlength="30"
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
          @click="updateGroup"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'
import axios from 'axios'

// 类型定义
interface Group {
  name: string;
}

interface GroupForm {
  name: string;
}

interface GroupEditForm {
  name: string;
  new_name: string;
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const groups = ref<Group[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const search = ref('')
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

// 表单对象
const form = reactive<GroupForm>({
  name: ''
})

const editForm = reactive<GroupEditForm>({
  name: '',
  new_name: ''
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入组名', trigger: 'blur' },
    { min: 2, max: 30, message: '长度在 2 到 30 个字符', trigger: 'blur' }
  ],
  new_name: [
    { required: true, message: '请输入组名', trigger: 'blur' },
    { min: 2, max: 30, message: '长度在 2 到 30 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const filteredGroups = computed(() => {
  if (!search.value.trim()) return groups.value
  
  const keyword = search.value.toLowerCase()
  return groups.value.filter(group => 
    group.name && group.name.toLowerCase().includes(keyword)
  )
})

// 数据加载方法
const fetchGroups = async () => {
  loading.value = true
  
  try {
    const response = await axios.get('/api/groups/', { withCredentials: true })
    
    if (response.data && Array.isArray(response.data.groups)) {
      groups.value = response.data.groups.map((g: any) => ({
        name: typeof g === 'string' ? g : g.name
      }))
      total.value = groups.value.length
    } else {
      groups.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取用户组列表失败:', error)
    ElMessage.error('获取用户组列表失败')
    groups.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 处理事件
const handleSearch = () => {
  // 本地过滤，不需要重新请求
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  // 本组件中分页仅作用于前端过滤结果，不需要重新请求
}

const handleCurrentChange = () => {
  // 本组件中分页仅作用于前端过滤结果，不需要重新请求
}

const confirmDeleteGroup = (group: Group) => {
  ElMessageBox.confirm(
    `确定要删除用户组 "${group.name}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteGroup(group.name)
  }).catch(() => {
    // 用户取消操作
  })
}

// 对话框处理
const openAddDialog = () => {
  resetForm()
  showAddDialog.value = true
}

const editGroup = (group: Group) => {
  resetEditForm()
  
  if (group && group.name) {
    editForm.name = group.name
    editForm.new_name = group.name
    showEditDialog.value = true
  }
}

const closeAddDialog = () => {
  showAddDialog.value = false
  resetForm()
}

const closeEditDialog = () => {
  showEditDialog.value = false
  resetEditForm()
}

const resetForm = () => {
  form.name = ''
}

const resetEditForm = () => {
  editForm.name = ''
  editForm.new_name = ''
}

// 表单提交
const addGroup = async () => {
  if (!addFormRef.value) return
  
  addFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      await axios.post('/api/group/add/', form, { withCredentials: true })
      
      ElMessage.success('新增用户组成功')
      closeAddDialog()
      fetchGroups()
    } catch (error: any) {
      let errorMsg = '新增用户组失败'
      
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
      console.error('新增用户组失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const updateGroup = async () => {
  if (!editFormRef.value) return
  
  editFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      if (!editForm.name) {
        throw new Error('原用户组名为空')
      }
      
      await axios.post(
        `/api/group/${editForm.name}/update/`, 
        { new_name: editForm.new_name }, 
        { withCredentials: true }
      )
      
      ElMessage.success('更新用户组成功')
      closeEditDialog()
      fetchGroups()
    } catch (error: any) {
      let errorMsg = '更新用户组失败'
      
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
      console.error('更新用户组失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteGroup = async (groupName: string) => {
  if (!groupName) return
  
  loading.value = true
  
  try {
    await axios.post(`/api/group/${groupName}/delete/`, {}, { withCredentials: true })
    ElMessage.success('删除用户组成功')
    fetchGroups()
  } catch (error: any) {
    let errorMsg = '删除用户组失败'
    
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
    console.error('删除用户组失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchGroups()
})
</script>

<style lang="scss" scoped>
@use '../../assets/styles/common.scss' as *;

.group-container {
  .form-input {
    width: 320px;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
  }
}
</style>