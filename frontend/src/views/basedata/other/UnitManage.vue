<template>
  <div class="unit-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">单位管理</h2>
          <div class="search-actions">
            <el-input
              v-model="search"
              placeholder="搜索单位名称/代码"
              clearable
              prefix-icon="Search"
              @input="handleSearch"
            />
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon> 新增单位
            </el-button>
            <el-button type="success" @click="downloadTemplate">
              <el-icon><Download /></el-icon> 下载模板
            </el-button>
            <el-upload
              :show-file-list="false"
              :before-upload="beforeImport"
              :http-request="handleImport"
              accept=".xlsx,.xls,.csv"
            >
              <el-button type="success">
                <el-icon><Upload /></el-icon> 导入
              </el-button>
            </el-upload>
          </div>
        </div>
      </template>
      
      <!-- 数据表格 -->
      <el-table
        :data="filteredUnits"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="code" label="单位代码" min-width="120" />
        <el-table-column prop="name" label="单位名称" min-width="120" />
        <el-table-column prop="description" label="描述" min-width="200" />
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
          :current-page="currentPage"
          @update:current-page="currentPage = $event"
          :page-size="pageSize"
          @update:page-size="pageSize = $event"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
        />
      </div>
    </el-card>
    
    <!-- 新增单位对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增单位"
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
        <el-form-item label="单位代码" prop="code">
          <el-input
            v-model="form.code"
            maxlength="20"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="单位名称" prop="name">
          <el-input
            v-model="form.name"
            maxlength="50"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
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
          @click="saveUnit"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑单位对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑单位"
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
        <el-form-item label="单位代码" prop="code">
          <el-input
            v-model="form.code"
            maxlength="20"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="单位名称" prop="name">
          <el-input
            v-model="form.name"
            maxlength="50"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
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
          @click="updateUnit"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete, Search, Download, Upload } from '@element-plus/icons-vue'
import axios from 'axios'
import * as XLSX from 'xlsx'

// 类型定义
interface Unit {
  id: number;
  code: string;
  name: string;
  description?: string;
}

interface UnitForm {
  id: number | null;
  code: string;
  name: string;
  description: string;
}

// 表单验证规则
const rules = {
  code: [
    { required: true, message: '请输入单位代码', trigger: 'blur' },
    { max: 20, message: '最大长度不能超过20', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入单位名称', trigger: 'blur' },
    { max: 50, message: '最大长度不能超过50', trigger: 'blur' }
  ]
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const units = ref<Unit[]>([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const search = ref('')

// 表单对象
const form = reactive<UnitForm>({
  id: null,
  code: '',
  name: '',
  description: ''
})

// 搜索过滤
const filteredUnits = computed(() => {
  if (!search.value) return units.value
  
  const searchTerm = search.value.toLowerCase()
  return units.value.filter(unit => {
    return (
      unit.name.toLowerCase().includes(searchTerm) ||
      unit.code.toLowerCase().includes(searchTerm) ||
      (unit.description && unit.description.toLowerCase().includes(searchTerm))
    )
  })
})

// 数据加载
const fetchUnits = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/units/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    
    if (response.data && response.data.results) {
      units.value = response.data.results
      total.value = response.data.count
    } else if (Array.isArray(response.data)) {
      units.value = response.data
      total.value = response.data.length
    } else {
      units.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取单位列表失败:', error)
    ElMessage.error('获取单位列表失败')
    units.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 处理页面事件
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchUnits()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchUnits()
}

const handleSearch = () => {
  currentPage.value = 1
  if (search.value === '') {
    fetchUnits()
  }
}

// 对话框操作
const openAddDialog = () => {
  form.id = null
  form.code = ''
  form.name = ''
  form.description = ''
  
  showAddDialog.value = true
}

const closeAddDialog = () => {
  showAddDialog.value = false
}

const openEditDialog = (unit: Unit) => {
  form.id = unit.id
  form.code = unit.code
  form.name = unit.name
  form.description = unit.description || ''
  
  showEditDialog.value = true
}

const closeEditDialog = () => {
  showEditDialog.value = false
}

// 保存单位
const saveUnit = async () => {
  if (!addFormRef.value) return
  
  await addFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      const response = await axios.post('/api/units/', {
        code: form.code,
        name: form.name,
        description: form.description
      })
      
      ElMessage.success('添加单位成功')
      closeAddDialog()
      await fetchUnits()
    } catch (error: any) {
      console.error('保存单位失败:', error)
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      submitting.value = false
    }
  })
}

const updateUnit = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      const response = await axios.put(`/api/units/${form.id}/`, {
        code: form.code,
        name: form.name,
        description: form.description
      })
      
      ElMessage.success('更新单位成功')
      closeEditDialog()
      await fetchUnits()
    } catch (error: any) {
      console.error('更新单位失败:', error)
      ElMessage.error(error.response?.data?.detail || '更新失败')
    } finally {
      submitting.value = false
    }
  })
}

// 删除单位
const confirmDelete = (unit: Unit) => {
  ElMessageBox.confirm(
    `确定要删除单位 "${unit.name} (${unit.code})" 吗？此操作将影响所有使用此单位的产品和物料。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteUnit(unit.id)
  }).catch(() => {
    // 用户取消删除
  })
}

const deleteUnit = async (id: number) => {
  loading.value = true
  
  try {
    await axios.delete(`/api/units/${id}/`)
    ElMessage.success('删除单位成功')
    await fetchUnits()
  } catch (error: any) {
    console.error('删除单位失败:', error)
    
    // 检查是否因为存在关联数据而无法删除
    if (error.response?.status === 400 || error.response?.status === 500) {
      ElMessage.error('无法删除该单位，因为已有产品或物料关联了此单位')
    } else {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  } finally {
    loading.value = false
  }
}

// 下载模板
const downloadTemplate = () => {
  // 创建工作簿和工作表
  const wb = XLSX.utils.book_new()
  
  // 添加表头
  const headers = ['code', 'name', 'description']
  const exampleData = [
    ['个', '个', '基本单位'],
    ['套', '套', '一套完整产品'],
    ['kg', '千克', '重量单位'],
    ['m', '米', '长度单位']
  ]
  
  // 合并表头和示例数据
  const worksheet = XLSX.utils.aoa_to_sheet([headers, ...exampleData])
  
  // 将工作表添加到工作簿
  XLSX.utils.book_append_sheet(wb, worksheet, '单位导入模板')
  
  // 保存文件
  XLSX.writeFile(wb, '单位导入模板.xlsx')
}

// 导入相关
const beforeImport = (file: File) => {
  const validExtensions = ['.xlsx', '.xls', '.csv']
  const fileName = file.name
  const extension = fileName.slice(fileName.lastIndexOf('.')).toLowerCase()
  
  if (!validExtensions.includes(extension)) {
    ElMessage.error('仅支持Excel或CSV文件导入')
    return false
  }
  
  return true
}

const handleImport = async (options: any) => {
  loading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    
    // 使用专用的单位导入接口
    const response = await axios.post('/api/units/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    ElMessage.success(response.data?.msg || '导入单位成功')
    await fetchUnits()
  } catch (error: any) {
    console.error('导入单位失败:', error)
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '导入失败')
  } finally {
    loading.value = false
  }
}

// 页面初始化
onMounted(async () => {
  await fetchUnits()
})
</script>

<style lang="scss" scoped>
@use '../../assets/styles/common.scss' as *;

.unit-container {
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 12px;
  }
  
  .page-title {
    margin: 0;
    font-size: 18px;
  }
  
  .search-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }
  
  .form-container {
    width: 100%;
  }
  
  .form-input {
    width: 100%;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
  }
  
  .pagination-container {
    margin-top: 24px;
    display: flex;
    justify-content: flex-end;
  }
}
</style> 