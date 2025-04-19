<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">菜单权限管理</span>
      <el-button type="primary" @click="showAdd=true" v-if="hasEditPermission">新增菜单</el-button>
    </div>
    <el-table :data="menusFlat" style="width:100%;margin-top:16px;">
      <el-table-column prop="name" label="菜单名" />
      <el-table-column prop="path" label="路径" />
      <el-table-column prop="groups" label="分配用户组" />
      <el-table-column prop="parent" label="父菜单ID" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="editMenu(scope.row)" v-if="hasEditPermission">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteMenu(scope.row)" v-if="hasEditPermission">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showAdd" title="新增菜单">
      <el-form :model="form">
        <el-form-item label="菜单名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="路径">
          <el-input v-model="form.path" />
        </el-form-item>
        <el-form-item label="分配用户组">
          <el-select v-model="form.groups" multiple filterable>
            <el-option v-for="g in groups" :key="g" :label="g" :value="g" />
          </el-select>
        </el-form-item>
        <el-form-item label="父菜单">
          <el-select v-model="form.parent" clearable filterable placeholder="无（一级菜单）">
            <el-option :value="null" label="无（一级菜单）" />
            <el-option v-for="m in menusFlat" :key="m.id" :value="m.id" :label="m.name" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd=false">取消</el-button>
        <el-button type="primary" @click="saveMenu">确定</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showEdit" title="编辑菜单">
      <el-form :model="editForm">
        <el-form-item label="菜单名">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="路径">
          <el-input v-model="editForm.path" />
        </el-form-item>
        <el-form-item label="分配用户组">
          <el-select v-model="editForm.groups" multiple filterable>
            <el-option v-for="g in groups" :key="g" :label="g" :value="g" />
          </el-select>
        </el-form-item>
        <el-form-item label="父菜单">
          <el-select v-model="editForm.parent" clearable filterable placeholder="无（一级菜单）">
            <el-option :value="null" label="无（一级菜单）" />
            <el-option v-for="m in menusFlat" :key="m.id" :value="m.id" :label="m.name" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit=false">取消</el-button>
        <el-button type="primary" @click="updateMenu">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

interface MenuItem {
  id: number;
  name: string;
  path: string;
  parent: number | null;
  groups: string[];
  children?: MenuItem[];
}

const menus = ref<MenuItem[]>([])
const groups = ref([])
const showAdd = ref(false)
const showEdit = ref(false)
const form = ref({ name: '', path: '', groups: [], parent: null })
const editForm = ref({ id: 0, name: '', path: '', groups: [], parent: null })
const hasEditPermission = ref(false)
const router = useRouter()
const fetchMenus = async () => {
  const res = await axios.get('/api/menus/', { withCredentials: true })
  menus.value = res.data.menus
}
const fetchGroups = async () => {
  const res = await axios.get('/api/groups/', { withCredentials: true })
  groups.value = res.data.groups
}
const checkPermission = async () => {
  // 通过 userinfo 判断是否超级管理员
  const res = await axios.get('/api/userinfo/', { withCredentials: true })
  hasEditPermission.value = (res.data.groups || []).includes('超级管理员')
}
const saveMenu = async () => {
  if (!hasEditPermission.value) {
    ElMessage.error('无权限')
    return
  }
  await axios.post('/api/menu/save/', form.value, { withCredentials: true })
  showAdd.value = false
  form.value = { name: '', path: '', groups: [], parent: null }
  fetchMenus()
}
const editMenu = (row: any) => {
  editForm.value = { id: row.id, name: row.name, path: row.path, groups: row.groups, parent: row.parent }
  showEdit.value = true
}
const updateMenu = async () => {
  if (!hasEditPermission.value) {
    ElMessage.error('无权限')
    return
  }
  await axios.post('/api/menu/save/', editForm.value, { withCredentials: true })
  showEdit.value = false
  fetchMenus()
}
const deleteMenu = async (row: any) => {
  if (!hasEditPermission.value) {
    ElMessage.error('无权限')
    return
  }
  await axios.post(`/api/menu/${row.id}/delete/`, {}, { withCredentials: true })
  fetchMenus()
}
const flatMenus = (tree: MenuItem[]): MenuItem[] => {
  const arr: MenuItem[] = []
  const walk = (nodes: MenuItem[], parent: number | null = null) => {
    for (const n of nodes) {
      arr.push({ ...n, parent })
      if (n.children && n.children.length) {
        walk(n.children, n.id)
      }
    }
  }
  walk(tree)
  return arr
}

const menusFlat = computed(() => flatMenus(menus.value))
onMounted(() => {
  fetchMenus()
  fetchGroups()
  checkPermission()
})
</script>
<style scoped>
.el-card {
  width: 100%;
  box-sizing: border-box;
}
</style>
