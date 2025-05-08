<template>
  <div class="company-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">公司管理</h2>
          <div class="search-actions">
            <el-input
              v-model="search"
              placeholder="搜索公司名称"
              clearable
              prefix-icon="Search"
              @input="handleSearch"
              class="search-input"
            />
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon> 新增公司
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 数据表格 -->
      <el-table
        :data="filteredCompanies"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="公司名称" min-width="150" />
        <el-table-column prop="code" label="公司代码" min-width="120" />
        <el-table-column prop="address" label="地址" min-width="180" />
        <el-table-column prop="contact" label="联系人" min-width="120" />
        <el-table-column prop="phone" label="联系电话" min-width="120" />
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
      <div class="pagination-container" v-if="total > pageSize">
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
    
    <!-- 添加公司对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增公司"
      width="580px"
      destroy-on-close
    >
      <el-form
        ref="addFormRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="left"
      >
        <el-form-item label="公司名称" prop="name">
          <el-input v-model="form.name" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="公司代码" prop="code">
          <el-input v-model="form.code" maxlength="20" show-word-limit />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" maxlength="200" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact">
          <el-input v-model="form.contact" maxlength="50" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" maxlength="20" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitAdd">
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑公司对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑公司"
      width="580px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="left"
      >
        <el-form-item label="公司名称" prop="name">
          <el-input v-model="form.name" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="公司代码" prop="code">
          <el-input v-model="form.code" maxlength="20" show-word-limit />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" maxlength="200" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact">
          <el-input v-model="form.contact" maxlength="50" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" maxlength="20" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitEdit">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { api } from '../../../api/index'
import { fetchData, createData, updateData, deleteData } from '../../../api/apiUtils'

// 类型定义
interface Company {
  id: number;
  name: string;
  code: string;
  address?: string;
  contact?: string;
  phone?: string;
}

interface CompanyForm {
  id?: number | null;
  name: string;
  code: string;
  address: string;
  contact: string;
  phone: string;
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const search = ref('')
const companies = ref<Company[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

// 表单相关
const form = reactive<CompanyForm>({
  id: null,
  name: '',
  code: '',
  address: '',
  contact: '',
  phone: ''
})

const rules = {
  name: [
    { required: true, message: '请输入公司名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在1到50个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入公司代码', trigger: 'blur' },
    { min: 1, max: 20, message: '长度在1到20个字符', trigger: 'blur' }
  ]
}

// 计算属性
const filteredCompanies = computed(() => {
  if (!search.value) return companies.value
  return companies.value.filter(c => 
    c.name && c.name.toLowerCase().includes(search.value.toLowerCase())
  )
})

// 数据加载方法
const fetchCompanies = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await api.get('/api/basedata/companies/', { params })
    
    // 处理API拦截器添加的统一封装格式
    if (response.data && response.data.success) {
      const responseData = response.data.data // 获取内部的实际数据
      
      // 处理分页或数组格式
      if (responseData && Array.isArray(responseData.results)) {
        companies.value = responseData.results
        total.value = responseData.count || 0
      } else if (responseData && Array.isArray(responseData)) {
        companies.value = responseData
        total.value = responseData.length
      } else {
        companies.value = []
        total.value = 0
        console.warn('未能识别的数据格式:', responseData)
      }
    } else {
      companies.value = []
      total.value = 0
      if (response.data && !response.data.success) {
        ElMessage.error(response.data.message || '获取公司列表失败')
      }
    }
  } catch (error) {
    companies.value = []
    total.value = 0
    ElMessage.error('获取公司列表失败')
    console.error('获取公司列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理事件
const handleSearch = () => {
  currentPage.value = 1
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchCompanies()
}

const handleCurrentChange = (val: number) => {
  fetchCompanies()
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.code = ''
  form.address = ''
  form.contact = ''
  form.phone = ''
}

const openAddDialog = () => {
  resetForm()
  showAddDialog.value = true
  nextTick(() => {
    addFormRef.value?.resetFields()
  })
}

const openEditDialog = (row: Company) => {
  resetForm()
  form.id = row?.id || null
  form.name = row?.name || ''
  form.code = row?.code || ''
  form.address = row?.address || ''
  form.contact = row?.contact || ''
  form.phone = row?.phone || ''
  showEditDialog.value = true
  nextTick(() => {
    editFormRef.value?.resetFields()
  })
}

const confirmDelete = (row: Company) => {
  ElMessageBox.confirm(
    `确定要删除公司 "${row.name}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteCompany(row.id)
  }).catch(() => {
    // 用户取消操作
  })
}

// 表单提交
const submitAdd = async () => {
  if (!addFormRef.value) return
  
  await addFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const response = await api.post('/api/basedata/companies/', form)
      
      if (response.data && response.data.success) {
        ElMessage.success('新增公司成功')
        showAddDialog.value = false
        fetchCompanies()
      } else if (response.data && !response.data.success) {
        ElMessage.error(response.data.message || '新增公司失败')
      }
    } catch (error: any) {
      const detail = error?.response?.data
      if (typeof detail === 'object') {
        ElMessage.error(Object.values(detail).join('; '))
      } else {
        ElMessage.error(detail || '新增公司失败')
      }
      console.error('新增公司失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const submitEdit = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const response = await api.put(`/api/basedata/companies/${form.id}/`, form)
      
      if (response.data && response.data.success) {
        ElMessage.success('更新公司成功')
        showEditDialog.value = false
        fetchCompanies()
      } else if (response.data && !response.data.success) {
        ElMessage.error(response.data.message || '更新公司失败')
      }
    } catch (error: any) {
      const detail = error?.response?.data
      if (typeof detail === 'object') {
        ElMessage.error(Object.values(detail).join('; '))
      } else {
        ElMessage.error(detail || '更新公司失败')
      }
      console.error('更新公司失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteCompany = async (id: number) => {
  loading.value = true
  try {
    const response = await api.delete(`/api/basedata/companies/${id}/`)
    
    if (response.data && response.data.success) {
      ElMessage.success('删除公司成功')
      fetchCompanies()
    } else if (response.data && !response.data.success) {
      ElMessage.error(response.data.message || '删除公司失败')
    }
  } catch (error) {
    ElMessage.error('删除公司失败')
    console.error('删除公司失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchCompanies()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

// Additional component specific styles
.company-container {
  .search-input {
    width: 240px;
  }
}
</style>
