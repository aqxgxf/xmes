<template>
  <div class="user-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">用户管理</h2>
          <div class="search-actions">
            <el-input
              v-model="search"
              placeholder="搜索用户名"
              clearable
              prefix-icon="Search"
              @input="handleSearch"
            />
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon> 新增用户
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="filteredUsers"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column label="用户组" min-width="200">
          <template #default="{ row }">
            <el-tag
              v-for="group in getGroupArray(row.groups)"
              :key="group"
              class="group-tag"
              size="small"
            >
              {{ group }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" @click="editUser(row)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button 
                v-if="canDeleteUser(row)" 
                size="small" 
                type="danger" 
                @click="confirmDeleteUser(row)"
              >
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
    
    <!-- 新增用户对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增用户"
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
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            maxlength="30"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="用户组" prop="groups">
          <el-select
            v-model="form.groups"
            multiple
            filterable
            placeholder="请选择用户组"
            class="form-input"
          >
            <el-option
              v-for="group in groups"
              :key="group.name"
              :label="group.name"
              :value="group.name"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeAddDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="addUser"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑用户"
      width="500px"
      destroy-on-close
      @close="closeEditDialog"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
        label-position="left"
        class="form-container"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="editForm.username"
            maxlength="30"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="editForm.password"
            type="password"
            show-password
            placeholder="不修改请留空"
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="用户组" prop="groups">
          <el-select
            v-model="editForm.groups"
            multiple
            filterable
            placeholder="请选择用户组"
            class="form-input"
          >
            <el-option
              v-for="group in groups"
              :key="group.name"
              :label="group.name"
              :value="group.name"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeEditDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="updateUser"
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
interface User {
  id: number;
  username: string;
  groups: string[] | { name: string }[];
}

interface Group {
  name: string;
}

interface UserForm {
  username: string;
  password: string;
  groups: string[];
}

interface UserEditForm extends UserForm {
  id: number | null;
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const users = ref<User[]>([])
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
const form = reactive<UserForm>({
  username: '',
  password: '',
  groups: []
})

const editForm = reactive<UserEditForm>({
  id: null,
  username: '',
  password: '',
  groups: []
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 30, message: '长度在 3 到 30 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ],
  groups: [
    { required: true, message: '请选择至少一个用户组', trigger: 'change' },
    { type: 'array', min: 1, message: '请至少选择一个用户组', trigger: 'change' }
  ]
}

// 编辑表单验证规则 (密码可选)
const editRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 30, message: '长度在 3 到 30 个字符', trigger: 'blur' }
  ],
  password: [
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ],
  groups: [
    { required: true, message: '请选择至少一个用户组', trigger: 'change' },
    { type: 'array', min: 1, message: '请至少选择一个用户组', trigger: 'change' }
  ]
}

// 计算属性
const filteredUsers = computed(() => {
  if (!search.value.trim()) return users.value
  
  const keyword = search.value.toLowerCase()
  return users.value.filter(user => 
    user.username.toLowerCase().includes(keyword)
  )
})

// 用户组处理函数
const getGroupArray = (groups: string[] | { name: string }[] | undefined): string[] => {
  if (!groups) return []
  
  return Array.isArray(groups) 
    ? groups.map(g => typeof g === 'string' ? g : g.name)
    : []
}

// 权限检查
const canDeleteUser = (user: User): boolean => {
  // 防止删除当前登录用户或特定重要账户
  // 这里可以根据实际需求添加逻辑
  return true
}

// 数据加载方法
const fetchUsers = async () => {
  loading.value = true
  
  try {
    const response = await axios.get('/api/users/', { withCredentials: true })
    
    if (response.data && response.data.users) {
      users.value = response.data.users
      total.value = response.data.users.length
    } else {
      users.value = []
      total.value = 0
    }
  } catch (error: any) {
    if (error?.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      window.location.href = '/login'
    } else {
      console.error('获取用户列表失败:', error)
      ElMessage.error('获取用户列表失败')
    }
    
    users.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const fetchGroups = async () => {
  try {
    const response = await axios.get('/api/groups/', { withCredentials: true })
    
    if (response.data && Array.isArray(response.data.groups)) {
      groups.value = response.data.groups.map((g: any) => 
        typeof g === 'string' ? { name: g } : { name: g.name }
      )
    } else {
      groups.value = []
    }
  } catch (error) {
    console.error('获取用户组列表失败:', error)
    ElMessage.error('获取用户组列表失败')
    groups.value = []
  }
}

// 处理事件
const handleSearch = () => {
  // 本地过滤，不需要重新请求
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchUsers()
}

const handleCurrentChange = () => {
  fetchUsers()
}

const confirmDeleteUser = (user: User) => {
  ElMessageBox.confirm(
    `确定要删除用户 "${user.username}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteUser(user.id)
  }).catch(() => {
    // 用户取消操作
  })
}

// 对话框处理
const openAddDialog = async () => {
  if (groups.value.length === 0) {
    await fetchGroups()
  }
  
  resetForm()
  showAddDialog.value = true
}

const editUser = async (user: User) => {
  if (groups.value.length === 0) {
    await fetchGroups()
  }
  
  resetEditForm()
  
  editForm.id = user.id
  editForm.username = user.username
  editForm.password = ''
  editForm.groups = getGroupArray(user.groups)
  
  showEditDialog.value = true
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
  form.username = ''
  form.password = ''
  form.groups = []
}

const resetEditForm = () => {
  editForm.id = null
  editForm.username = ''
  editForm.password = ''
  editForm.groups = []
}

// 表单提交
const addUser = async () => {
  if (!addFormRef.value) return
  
  addFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      await axios.post('/api/register/', form, { withCredentials: true })
      
      ElMessage.success('新增用户成功')
      closeAddDialog()
      fetchUsers()
    } catch (error: any) {
      let errorMsg = '新增用户失败'
      
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
      console.error('新增用户失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const updateUser = async () => {
  if (!editFormRef.value) return
  
  editFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      // 确保 groups 为字符串数组
      const groups = Array.isArray(editForm.groups)
        ? editForm.groups.map((g: any) => typeof g === 'string' ? g : g.name)
        : []
      
      await axios.post(`/api/user/${editForm.id}/update/`, {
        username: editForm.username,
        password: editForm.password,
        groups
      }, { withCredentials: true })
      
      ElMessage.success('编辑用户成功')
      closeEditDialog()
      fetchUsers()
    } catch (error: any) {
      let errorMsg = '编辑用户失败'
      
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
      console.error('编辑用户失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteUser = async (id: number) => {
  loading.value = true
  
  try {
    await axios.post(`/api/user/${id}/delete/`, {}, { withCredentials: true })
    ElMessage.success('删除用户成功')
    fetchUsers()
  } catch (error: any) {
    let errorMsg = '删除用户失败'
    
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
    console.error('删除用户失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchUsers()
  fetchGroups()
})
</script>

<style lang="scss" scoped>
@use '../../assets/styles/common.scss' as *;

.user-container {
  .form-input {
    width: 320px;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
  }
  
  .group-tag {
    margin-right: 5px;
    margin-bottom: 5px;
  }
}
</style>
