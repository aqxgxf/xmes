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
      
      <div class="menu-management-container">
        <div class="menu-tree-container">
          <h3>菜单层级结构</h3>
          <el-tree
            ref="menuTreeRef"
            :data="menuTreeData"
            node-key="id"
            :props="{ label: 'name', children: 'children' }"
            highlight-current
            @node-click="handleNodeClick"
            default-expand-all
          >
            <template #default="{ node, data }">
              <div class="custom-tree-node">
                <span :class="data.path ? 'has-path' : 'no-path'">{{ node.label }}</span>
                <span v-if="data.path" class="menu-path">{{ data.path }}</span>
              </div>
            </template>
          </el-tree>
        </div>
        
        <div class="menu-table-container">
          <h3>菜单详情</h3>
          <!-- 数据表格 -->
          <el-table
            :data="menus"
            v-loading="loading"
            border
            stripe
            row-key="id"
            :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
            style="width: 100%"
            height="calc(80vh - 180px)"
          >
            <el-table-column prop="name" label="菜单名" min-width="120">
              <template #default="{ row }">
                <div class="menu-name-cell">
                  <el-tag 
                    v-if="row.parent === null"
                    type="primary" 
                    effect="plain"
                    class="menu-level-tag"
                  >
                    一级
                  </el-tag>
                  <el-tag 
                    v-else
                    type="success" 
                    effect="plain"
                    class="menu-level-tag"
                  >
                    子级
                  </el-tag>
                  {{ row.name }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="path" label="路径" min-width="120">
              <template #default="{ row }">
                <span v-if="row.path">{{ row.path }}</span>
                <span v-else class="no-path-text">无路径（菜单分组）</span>
              </template>
            </el-table-column>
            <el-table-column label="分配用户组" min-width="120">
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
            <el-table-column label="父菜单" min-width="100">
              <template #default="{ row }">
                <span v-if="row.parent">
                  {{ getParentName(row.parent) }}
                </span>
                <span v-else class="root-menu">
                  根菜单
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
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
        </div>
      </div>
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
        
        <el-form-item label="菜单类型" prop="menuType">
          <el-radio-group v-model="form.menuType" @change="handleMenuTypeChange">
            <el-radio label="page">页面菜单</el-radio>
            <el-radio label="group">菜单分组</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="路径" prop="path" v-if="form.menuType === 'page'">
          <el-input
            v-model="form.path"
            maxlength="100"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="父菜单" prop="parent">
          <el-cascader
            v-model="form.parent"
            :options="menuOptions"
            :props="{ 
              checkStrictly: true,
              value: 'id',
              label: 'name',
              emitPath: false
            }"
            clearable
            placeholder="无（一级菜单）"
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
        
        <el-form-item label="菜单类型" prop="menuType">
          <el-radio-group v-model="editForm.menuType" @change="handleEditMenuTypeChange">
            <el-radio label="page">页面菜单</el-radio>
            <el-radio label="group">菜单分组</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="路径" prop="path" v-if="editForm.menuType === 'page'">
          <el-input
            v-model="editForm.path"
            maxlength="100"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="父菜单" prop="parent">
          <el-cascader
            v-model="editForm.parent"
            :options="menuOptions"
            :props="{ 
              checkStrictly: true,
              value: 'id',
              label: 'name',
              emitPath: false
            }"
            clearable
            placeholder="无（一级菜单）"
            class="form-input"
            :disabled="isParentMenuSelectDisabled"
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
import { ref, reactive, onMounted, computed } from 'vue'
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
  menuType: 'page' | 'group';
  groups: string[];
  parent: number | null;
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const menus = ref<MenuItem[]>([])
const groups = ref<string[]>([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const hasEditPermission = ref(false)
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const menuTreeRef = ref<InstanceType<typeof import('element-plus')['ElTree']>>()
const selectedNode = ref<MenuItem>()
const isParentMenuSelectDisabled = ref(false)

// 表单对象
const form = reactive<MenuForm>({
  name: '',
  path: '',
  menuType: 'page',
  groups: [],
  parent: null
})

// 编辑表单对象
const editForm = reactive<MenuForm>({
  id: undefined,
  name: '',
  path: '',
  menuType: 'page',
  groups: [],
  parent: null
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入菜单名', trigger: 'blur' },
    { max: 30, message: '最大长度不能超过30', trigger: 'blur' }
  ],
  path: [
    { required: (form: any) => form.menuType === 'page', message: '页面菜单必须输入路径', trigger: 'blur' },
    { max: 100, message: '最大长度不能超过100', trigger: 'blur' }
  ]
}

// 计算菜单树形数据
const menuTreeData = computed(() => {
  return [...menus.value]
})

// 计算菜单选项
const menuOptions = computed(() => {
  const result = [...menus.value]
  
  // 如果是编辑模式且有选中的菜单
  if (showEditDialog.value && editForm.id) {
    // 从选项中排除当前菜单及其所有子孙菜单，避免循环引用
    const excludeIds = getMenuAndChildrenIds(editForm.id, result)
    return result.filter(item => !excludeIds.includes(item.id))
  }
  
  return result
})

// 获取菜单及其所有子孙菜单的ID
function getMenuAndChildrenIds(menuId: number, menuList: MenuItem[]): number[] {
  const ids: number[] = [menuId]
  
  function traverse(items: MenuItem[]) {
    for (const item of items) {
      if (item.id === menuId && item.children) {
        collectChildrenIds(item.children, ids)
      } else if (item.children) {
        traverse(item.children)
      }
    }
  }
  
  function collectChildrenIds(children: MenuItem[], collectIds: number[]) {
    for (const child of children) {
      collectIds.push(child.id)
      if (child.children) {
        collectChildrenIds(child.children, collectIds)
      }
    }
  }
  
  traverse(menuList)
  return ids
}

// 获取父菜单名称
function getParentName(parentId: number | null): string {
  if (!parentId) return '无'
  
  const findParent = (menuList: MenuItem[]): string => {
    for (const menu of menuList) {
      if (menu.id === parentId) {
        return menu.name
      }
      if (menu.children && menu.children.length > 0) {
        const name = findParent(menu.children)
        if (name !== '未找到') {
          return name
        }
      }
    }
    return '未找到'
  }
  
  return findParent(menus.value)
}

// 处理菜单类型变更
function handleMenuTypeChange(type: 'page' | 'group') {
  if (type === 'group') {
    form.path = ''
  }
}

// 处理编辑菜单类型变更
function handleEditMenuTypeChange(type: 'page' | 'group') {
  if (type === 'group') {
    editForm.path = ''
  }
}

// 数据加载
const fetchMenus = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/menus/')
    
    if (response.data && response.data.menus) {
      menus.value = response.data.menus
    } else {
      menus.value = []
    }
  } catch (error) {
    menus.value = []
    console.error('获取菜单列表失败:', error)
    ElMessage.error('获取菜单列表失败')
  } finally {
    loading.value = false
  }
}

// 加载用户组列表
const fetchGroups = async () => {
  try {
    const response = await axios.get('/api/groups/')
    if (response.data && response.data.groups) {
      groups.value = response.data.groups
    } else {
      groups.value = []
    }
  } catch (error) {
    groups.value = []
    console.error('获取用户组列表失败:', error)
    ElMessage.error('获取用户组列表失败')
  }
}

// 检查权限
const checkPermission = async () => {
  try {
    const response = await axios.get('/api/userinfo/')
    if (response.data && response.data.groups) {
      hasEditPermission.value = response.data.groups.includes('超级管理员')
    } else {
      hasEditPermission.value = false
    }
  } catch (error) {
    hasEditPermission.value = false
  }
}

// 打开新增菜单对话框
const openAddDialog = () => {
  form.name = ''
  form.path = ''
  form.menuType = 'page'
  form.groups = []
  form.parent = null
  showAddDialog.value = true
}

// 关闭新增菜单对话框
const closeAddDialog = () => {
  showAddDialog.value = false
}

// 打开编辑菜单对话框
const editMenu = (menu: MenuItem) => {
  editForm.id = menu.id
  editForm.name = menu.name
  editForm.path = menu.path || ''
  editForm.menuType = menu.path ? 'page' : 'group'
  editForm.groups = [...menu.groups]
  editForm.parent = menu.parent
  
  // 检测是否有子菜单，有则禁用父菜单选择
  const hasChildren = hasChildMenus(menu.id, menus.value)
  isParentMenuSelectDisabled.value = hasChildren
  
  showEditDialog.value = true
}

// 检查菜单是否有子菜单
function hasChildMenus(menuId: number, menuList: MenuItem[]): boolean {
  for (const menu of menuList) {
    if (menu.parent === menuId) {
      return true
    }
    if (menu.children && menu.children.length > 0) {
      if (hasChildMenus(menuId, menu.children)) {
        return true
      }
    }
  }
  return false
}

// 关闭编辑菜单对话框
const closeEditDialog = () => {
  showEditDialog.value = false
}

// 保存菜单
const saveMenu = async () => {
  if (!addFormRef.value) return
  
  await addFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    // 如果是菜单分组，路径为空
    if (form.menuType === 'group') {
      form.path = ''
    }
    
    try {
      await axios.post('/api/menu/save/', {
        name: form.name,
        path: form.path,
        parent: form.parent,
        groups: form.groups
      })
      
      ElMessage.success('菜单保存成功')
      closeAddDialog()
      fetchMenus()
    } catch (error: any) {
      console.error('保存菜单失败:', error)
      ElMessage.error(error.response?.data?.detail || error.response?.data?.error || '保存失败')
    } finally {
      submitting.value = false
    }
  })
}

// 更新菜单
const updateMenu = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    // 如果是菜单分组，路径为空
    if (editForm.menuType === 'group') {
      editForm.path = ''
    }
    
    try {
      await axios.post('/api/menu/save/', {
        id: editForm.id,
        name: editForm.name,
        path: editForm.path,
        parent: editForm.parent,
        groups: editForm.groups
      })
      
      ElMessage.success('菜单更新成功')
      closeEditDialog()
      fetchMenus()
    } catch (error: any) {
      console.error('更新菜单失败:', error)
      ElMessage.error(error.response?.data?.detail || error.response?.data?.error || '更新失败')
    } finally {
      submitting.value = false
    }
  })
}

// 确认删除菜单
const confirmDeleteMenu = (menu: MenuItem) => {
  // 检查是否有子菜单
  const hasChildren = hasChildMenus(menu.id, menus.value)
  if (hasChildren) {
    ElMessageBox.alert(
      '该菜单下有子菜单，无法直接删除。请先删除其下的所有子菜单。',
      '无法删除',
      { type: 'warning' }
    )
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除菜单 "${menu.name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteMenu(menu.id)
  }).catch(() => {
    // 用户取消操作
  })
}

// 删除菜单
const deleteMenu = async (menuId: number) => {
  loading.value = true
  
  try {
    await axios.post(`/api/menu/${menuId}/delete/`)
    ElMessage.success('删除菜单成功')
    await fetchMenus()
  } catch (error: any) {
    console.error('删除菜单失败:', error)
    ElMessage.error(error.response?.data?.detail || error.response?.data?.error || '删除失败')
  } finally {
    loading.value = false
  }
}

// 处理菜单树节点点击
const handleNodeClick = (data: MenuItem) => {
  selectedNode.value = data
}

// 生命周期钩子
onMounted(async () => {
  await checkPermission()
  await fetchGroups()
  await fetchMenus()
})
</script>

<style lang="scss" scoped>
@use '../../assets/styles/common.scss' as *;

.menu-container {
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .page-title {
    margin: 0;
    font-size: 18px;
  }
  
  .menu-management-container {
    display: grid;
    grid-template-columns: 250px 1fr;
    gap: 15px;
    
    @media (max-width: 1200px) {
      grid-template-columns: 1fr;
    }
  }
  
  .menu-tree-container {
    background-color: #f9f9f9;
    padding: 12px;
    border-radius: 4px;
    max-height: calc(80vh - 180px);
    overflow: auto;
    
    h3 {
      margin-top: 0;
      margin-bottom: 12px;
      font-size: 16px;
      color: #606266;
    }
  }
  
  .menu-table-container {
    h3 {
      margin-top: 0;
      margin-bottom: 12px;
      font-size: 16px;
      color: #606266;
    }
  }
  
  .custom-tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.9em;
    padding-right: 8px;
    
    .has-path {
      font-weight: bold;
    }
    
    .no-path {
      color: #909399;
    }
    
    .menu-path {
      font-size: 12px;
      color: #909399;
      margin-left: 8px;
      max-width: 100px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
  
  .menu-name-cell {
    display: flex;
    align-items: center;
    
    .menu-level-tag {
      margin-right: 8px;
      transform: scale(0.85);
    }
  }
  
  .no-path-text {
    color: #909399;
    font-style: italic;
    font-size: 0.9em;
  }
  
  .root-menu {
    color: #409EFF;
    font-weight: bold;
  }
  
  .action-buttons {
    display: flex;
    gap: 4px;
    
    .el-button {
      padding: 5px 10px;
    }
  }
  
  .group-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    
    .group-tag {
      margin-bottom: 2px;
      font-size: 0.85em;
    }
  }
  
  .form-container {
    max-height: 60vh;
    overflow-y: auto;
  }
  
  .form-input {
    width: 100%;
  }

  // Make the table more responsive
  :deep(.el-table) {
    font-size: 0.9em;
    
    .el-table__header th {
      padding: 8px 0;
    }
    
    .el-table__row td {
      padding: 6px 0;
    }
  }
}
</style>
