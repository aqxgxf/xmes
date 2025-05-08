<template>
  <div class="menu-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">菜单权限管理</h2>
          <div class="search-actions">
            <el-button
              v-if="hasEditPermission"
              type="primary"
              @click="openAddDialog"
            >
              <el-icon><Plus /></el-icon> 新增菜单
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 数据表格 -->
      <el-table
        :data="menus"
        v-loading="loading"
        border
        stripe
        row-key="id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        style="width: 100%"
        height="calc(80vh - 120px)"
      >
        <el-table-column prop="name" label="菜单名" min-width="180" />
        <el-table-column prop="path" label="路径" min-width="200" />
        <el-table-column label="分配用户组" min-width="200">
          <template #default="{ row }">
            <div class="group-tags">
              <el-tag
                v-for="group in row.groups"
                :key="group"
                size="small"
                class="group-tag"
              >
                {{ group }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="parent" label="父菜单ID" min-width="100" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons" v-if="hasEditPermission">
              <el-button size="small" type="primary" @click="editMenu(row)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button size="small" type="danger" @click="confirmDeleteMenu(row)">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 新增菜单对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增菜单"
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
        <el-form-item label="菜单名" prop="name">
          <el-input
            v-model="form.name"
            maxlength="30"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="路径" prop="path">
          <el-input
            v-model="form.path"
            maxlength="100"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="分配用户组" prop="groups">
          <el-select
            v-model="form.groups"
            multiple
            filterable
            placeholder="请选择用户组"
            class="form-input"
          >
            <el-option
              v-for="group in groups"
              :key="group"
              :label="group"
              :value="group"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="父菜单" prop="parent">
          <el-select
            v-model="form.parent"
            filterable
            clearable
            placeholder="无（一级菜单）"
            class="form-input"
          >
            <el-option :value="null" label="无（一级菜单）" />
            <el-option
              v-for="menu in flatMenus(menus)"
              :key="menu.id"
              :label="menu.name"
              :value="menu.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeAddDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="saveMenu"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑菜单对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑菜单"
      width="500px"
      destroy-on-close
      @close="closeEditDialog"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="rules"
        label-width="100px"
        label-position="left"
        class="form-container"
      >
        <el-form-item label="菜单名" prop="name">
          <el-input
            v-model="editForm.name"
            maxlength="30"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="路径" prop="path">
          <el-input
            v-model="editForm.path"
            maxlength="100"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="分配用户组" prop="groups">
          <el-select
            v-model="editForm.groups"
            multiple
            filterable
            placeholder="请选择用户组"
            class="form-input"
          >
            <el-option
              v-for="group in groups"
              :key="group"
              :label="group"
              :value="group"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="父菜单" prop="parent">
          <el-select
            v-model="editForm.parent"
            filterable
            clearable
            placeholder="无（一级菜单）"
            class="form-input"
          >
            <el-option :value="null" label="无（一级菜单）" />
            <el-option
              v-for="menu in flatMenus(menus)"
              :key="menu.id"
              :label="menu.name"
              :value="menu.id"
              :disabled="menu.id === editForm.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeEditDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="updateMenu"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

// 类型定义
interface MenuItem {
  id: number;
  name: string;
  path: string;
  parent: number | null;
  groups: string[];
  children?: MenuItem[];
}

interface MenuForm {
  id?: number;
  name: string;
  path: string;
  groups: string[];
  parent: number | null;
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const menus = ref<MenuItem[]>([])
const groups = ref<string[]>([])
const hasEditPermission = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

// 表单对象
const form = reactive<MenuForm>({
  name: '',
  path: '',
  groups: [],
  parent: null
})

const editForm = reactive<MenuForm>({
  id: 0,
  name: '',
  path: '',
  groups: [],
  parent: null
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入菜单名', trigger: 'blur' },
    { min: 2, max: 30, message: '长度在 2 到 30 个字符', trigger: 'blur' }
  ],
  path: [
    { required: true, message: '请输入路径', trigger: 'blur' },
    { max: 100, message: '最大长度不能超过100个字符', trigger: 'blur' }
  ]
}

// 数据加载方法
const fetchMenus = async () => {
  loading.value = true
  
  try {
    const response = await axios.get('/api/menus/', { withCredentials: true })
    
    if (response.data && response.data.menus) {
      menus.value = response.data.menus || []
    } else {
      menus.value = []
    }
  } catch (error) {
    console.error('获取菜单列表失败:', error)
    ElMessage.error('获取菜单列表失败')
    menus.value = []
  } finally {
    loading.value = false
  }
}

const fetchGroups = async () => {
  try {
    const response = await axios.get('/api/groups/', { withCredentials: true })
    
    if (response.data && Array.isArray(response.data.groups)) {
      // 兼容字符串数组和对象数组
      groups.value = response.data.groups.map((g: any) => 
        typeof g === 'string' ? g : g.name
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

const checkPermission = async () => {
  try {
    const response = await axios.get('/api/userinfo/', { withCredentials: true })
    
    if (response.data && Array.isArray(response.data.groups)) {
      hasEditPermission.value = response.data.groups.includes('超级管理员')
    } else {
      hasEditPermission.value = false
    }
  } catch (error) {
    console.error('检查权限失败:', error)
    hasEditPermission.value = false
  }
}

// 辅助函数
function flatMenus(tree: MenuItem[]): MenuItem[] {
  const result: MenuItem[] = []
  
  function walk(list: MenuItem[]) {
    for (const item of list) {
      result.push(item)
      if (item.children && item.children.length) {
        walk(item.children)
      }
    }
  }
  
  walk(tree)
  return result
}

// 对话框处理
const openAddDialog = async () => {
  if (!hasEditPermission.value) {
    ElMessage.error('无权限')
    return
  }
  
  resetForm()
  
  if (groups.value.length === 0) {
    await fetchGroups()
  }
  
  showAddDialog.value = true
}

const editMenu = async (menu: MenuItem) => {
  if (!hasEditPermission.value) {
    ElMessage.error('无权限')
    return
  }
  
  resetEditForm()
  
  if (groups.value.length === 0) {
    await fetchGroups()
  }
  
  editForm.id = menu.id
  editForm.name = menu.name
  editForm.path = menu.path
  editForm.groups = menu.groups || []
  editForm.parent = menu.parent
  
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
  form.name = ''
  form.path = ''
  form.groups = []
  form.parent = null
}

const resetEditForm = () => {
  editForm.id = 0
  editForm.name = ''
  editForm.path = ''
  editForm.groups = []
  editForm.parent = null
}

const confirmDeleteMenu = (menu: MenuItem) => {
  if (!hasEditPermission.value) {
    ElMessage.error('无权限')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除菜单 "${menu.name}" 吗？此操作不可撤销。${menu.children && menu.children.length ? '子菜单也将被删除！' : ''}`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteMenu(menu)
  }).catch(() => {
    // 用户取消操作
  })
}

// 表单提交
const saveMenu = async () => {
  if (!hasEditPermission.value) {
    ElMessage.error('无权限')
    return
  }
  
  if (!addFormRef.value) return
  
  addFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      await axios.post('/api/menu/save/', form, { withCredentials: true })
      
      ElMessage.success('新增菜单成功')
      closeAddDialog()
      fetchMenus()
    } catch (error: any) {
      let errorMsg = '新增菜单失败'
      
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
      console.error('新增菜单失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const updateMenu = async () => {
  if (!hasEditPermission.value) {
    ElMessage.error('无权限')
    return
  }
  
  if (!editFormRef.value) return
  
  // 检查是否将自己设为自己的父级
  if (editForm.id === editForm.parent) {
    ElMessage.error('不能将菜单设为自己的父级')
    return
  }
  
  editFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      await axios.post('/api/menu/save/', editForm, { withCredentials: true })
      
      ElMessage.success('更新菜单成功')
      closeEditDialog()
      fetchMenus()
    } catch (error: any) {
      let errorMsg = '更新菜单失败'
      
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
      console.error('更新菜单失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteMenu = async (menu: MenuItem) => {
  if (!hasEditPermission.value) {
    ElMessage.error('无权限')
    return
  }
  
  loading.value = true
  
  try {
    await axios.post(`/api/menu/${menu.id}/delete/`, {}, { withCredentials: true })
    ElMessage.success('删除菜单成功')
    fetchMenus()
  } catch (error: any) {
    let errorMsg = '删除菜单失败'
    
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
    console.error('删除菜单失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchMenus()
  fetchGroups()
  checkPermission()
})
</script>

<style lang="scss" scoped>
@use '../../assets/styles/common.scss' as *;

.menu-container {
  .form-input {
    width: 320px;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
  }
  
  .group-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
  
  .group-tag {
    margin-bottom: 4px;
  }
}
</style>
