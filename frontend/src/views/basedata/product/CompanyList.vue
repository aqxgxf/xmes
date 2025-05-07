<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">公司管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-button type="primary" @click="openAdd">新增公司</el-button>
      </div>
    </div>
    <el-table :data="companies" style="width:100%;margin-top:16px;">
      <el-table-column prop="name" label="公司名称" />
      <el-table-column prop="code" label="公司代码" />
      <el-table-column prop="address" label="地址" />
      <el-table-column prop="contact" label="联系人" />
      <el-table-column prop="phone" label="联系电话" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="editCompany(scope.row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showAdd" title="新增公司">
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item label="公司名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="公司代码"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="form.phone" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd=false">取消</el-button>
        <el-button type="primary" @click="saveCompany">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showEdit" title="编辑公司">
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item label="公司名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="公司代码"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="form.phone" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit=false">取消</el-button>
        <el-button type="primary" @click="updateCompany">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
const companies = ref([])
const showAdd = ref(false)
const showEdit = ref(false)
const form = ref({ id: null, name: '', code: '', address: '', contact: '', phone: '' })
const fetchCompanies = async () => {
  const res = await axios.get('/api/companies/')
  companies.value = res.data
}
const openAdd = () => {
  form.value = { id: null, name: '', code: '', address: '', contact: '', phone: '' }
  showAdd.value = true
}
const saveCompany = async () => {
  if (!form.value.name || !form.value.code) {
    ElMessage.error('公司名称和公司代码为必填项')
    return
  }
  try {
    await axios.post('/api/companies/', form.value)
    showAdd.value = false
    ElMessage.success('新增公司成功')
    fetchCompanies()
  } catch (e: any) {
    const detail = e?.response?.data
    if (typeof detail === 'object') {
      ElMessage.error(Object.values(detail).join('; '))
    } else {
      ElMessage.error(detail || '新增公司失败')
    }
  }
}
const editCompany = (row: any) => {
  form.value = { ...row }
  showEdit.value = true
}
const updateCompany = async () => {
  try {
    await axios.put(`/api/companies/${form.value.id}/`, form.value)
    showEdit.value = false
    ElMessage.success('编辑公司成功')
    fetchCompanies()
  } catch (e: any) {
    const detail = e?.response?.data
    if (typeof detail === 'object') {
      ElMessage.error(Object.values(detail).join('; '))
    } else {
      ElMessage.error(detail || '编辑公司失败')
    }
  }
}
onMounted(fetchCompanies)
</script>
<style>
@import '/src/style.css';
</style>
<!-- 移除 scoped 样式，通用样式已抽取到 style.css，如有个性化样式可在此补充 -->
