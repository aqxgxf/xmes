<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">用户组管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-input v-model="search" placeholder="搜索组名" style="width:200px" clearable @input="fetchGroups" />
        <el-button type="primary" @click="showAddGroup=true">新增用户组</el-button>
      </div>
    </div>
    <el-table :data="filteredGroups" style="width:100%;margin-top:16px;">
      <el-table-column prop="name" label="组名" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="editGroup(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteGroup(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showAddGroup" title="新增用户组">
      <el-form :model="groupForm">
        <el-form-item label="组名">
          <el-input v-model="groupForm.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddGroup=false">取消</el-button>
        <el-button type="primary" @click="addGroup">确定</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showEditGroup" title="编辑用户组">
      <el-form :model="editGroupForm">
        <el-form-item label="组名">
          <el-input v-model="editGroupForm.new_name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditGroup=false">取消</el-button>
        <el-button type="primary" @click="updateGroup">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
const groups = ref([])
const search = ref('')
const showAddGroup = ref(false)
const showEditGroup = ref(false)
const groupForm = ref({ name: '' })
const editGroupForm = ref({ name: '', new_name: '' })
const fetchGroups = async () => {
  const res = await axios.get('/api/groups/', { withCredentials: true })
  if (Array.isArray(res.data.groups)) {
    groups.value = res.data.groups.map((g: any) => ({ name: typeof g === 'string' ? g : g.name }))
  } else {
    groups.value = []
  }
}
const filteredGroups = computed(() => {
  if (!search.value) return groups.value
  return groups.value.filter((g: any) => g.name && g.name.toLowerCase().includes(search.value.toLowerCase()))
})
const addGroup = async () => {
  await axios.post('/api/group/add/', groupForm.value, { withCredentials: true })
  showAddGroup.value = false
  groupForm.value = { name: '' }
  fetchGroups()
}
const editGroup = (row: any) => {
  if (row && row.name) {
    editGroupForm.value = { name: row.name, new_name: row.name }
    showEditGroup.value = true
  }
}
const updateGroup = async () => {
  if (!editGroupForm.value.name) return
  await axios.post(`/api/group/${editGroupForm.value.name}/update/`, { new_name: editGroupForm.value.new_name }, { withCredentials: true })
  showEditGroup.value = false
  fetchGroups()
}
const deleteGroup = async (row: any) => {
  if (!row || !row.name) return
  await axios.post(`/api/group/${row.name}/delete/`, {}, { withCredentials: true })
  fetchGroups()
}
onMounted(fetchGroups)
</script>
<style>
@import '/src/style.css';
</style>
<!-- 移除 scoped 样式，通用样式已抽取到 style.css，如有个性化样式可在此补充 -->