<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">用户管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-input v-model="search" placeholder="搜索用户名" style="width:200px" clearable @input="fetchUsers" />
        <el-button type="primary" @click="showAdd=true">新增用户</el-button>
      </div>
    </div>
    <el-table :data="filteredUsers" style="width:100%;margin-top:16px;">
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="groups" label="用户组" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showAdd" title="新增用户">
      <el-form :model="form">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item label="用户组">
          <el-select v-model="form.groups" multiple filterable>
            <el-option v-for="g in groups" :key="g.name" :label="g.name" :value="g.name" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd=false">取消</el-button>
        <el-button type="primary" @click="addUser">确定</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showEdit" title="编辑用户">
      <el-form :model="editForm">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="editForm.password" type="password" placeholder="不修改请留空" />
        </el-form-item>
        <el-form-item label="用户组">
          <el-select v-model="editForm.groups" multiple filterable>
            <el-option v-for="g in groups" :key="g.name" :label="g.name" :value="g.name" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit=false">取消</el-button>
        <el-button type="primary" @click="updateUser">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
const users = ref([])
const groups = ref<{ name: string }[]>([])
const search = ref('')
const showAdd = ref(false)
const showEdit = ref(false)
// const showAddGroup = ref(false)
// const showEditGroup = ref(false)
const form = ref({ username: '', password: '', groups: [] })
const editForm = ref({ id: 0, username: '', password: '', groups: [] })
const fetchUsers = async () => {
  try {
    const res = await axios.get('/api/users/', { withCredentials: true })
    users.value = res.data.users
  } catch (e: unknown) {
    if (typeof e === 'object' && e && 'response' in e && (e as any).response.status === 401) {
      // 未登录时不再请求
      users.value = []
    }
  }
}

const fetchGroups = async () => {
  const res = await axios.get('/api/groups/', { withCredentials: true })
  // 兼容字符串数组和对象数组，强制转为 {name: string}[]
  if (Array.isArray(res.data.groups)) {
    groups.value = res.data.groups.map((g: any) => typeof g === 'string' ? { name: g } : { name: g.name })
  } else {
    groups.value = []
  }
}

const filteredUsers = computed(() => {
  if (!search.value) return users.value
  return users.value.filter((u: any) => u.username && u.username.toLowerCase().includes(search.value.toLowerCase()))
})

const addUser = async () => {
  await axios.post('/api/register/', form.value, { withCredentials: true })
  showAdd.value = false
  form.value = { username: '', password: '', groups: [] }
  ElMessage.success('新增用户成功')
  fetchUsers()
}
const editUser = (row: any) => {
  // row.groups 需为字符串数组
  editForm.value = {
    id: row.id,
    username: row.username,
    password: '',
    groups: Array.isArray(row.groups) ? row.groups.map((g: any) => typeof g === 'string' ? g : g.name) : []
  }
  showEdit.value = true
}
const updateUser = async () => {
  try {
    // 确保 groups 为字符串数组
    const groups = Array.isArray(editForm.value.groups)
      ? editForm.value.groups.map((g: any) => typeof g === 'string' ? g : g.name)
      : []
    await axios.post(`/api/user/${editForm.value.id}/update/`, {
      username: editForm.value.username,
      password: editForm.value.password,
      groups
    }, { withCredentials: true })
    showEdit.value = false
    ElMessage.success('编辑用户成功')
    await fetchUsers()
  } catch (e: unknown) {
    ElMessage.error('编辑用户失败')
  }
}

onMounted(() => {
  fetchUsers()
  fetchGroups()
})
</script>
<style>
@import '/src/style.css';
</style>
<!-- 移除 scoped 样式，通用样式已抽取到 style.css，如有个性化样式可在此补充 -->
