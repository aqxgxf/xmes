<template>
  <div class="product-category-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">产品类管理</h2>
          <div class="search-actions">
            <el-input
              v-model="search"
              placeholder="搜索产品类名称"
              clearable
              prefix-icon="Search"
              @input="handleSearch"
            />
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon> 新增产品类
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 数据表格 -->
      <el-table
        :data="filteredCategories"
        v-loading="loading"
        border
        stripe
        row-key="id"
        style="width: 100%"
      >
        <el-table-column prop="name" label="产品类名称" min-width="150" />
        <el-table-column prop="company_name" label="公司" min-width="120" />
        <el-table-column label="图纸PDF" align="center" width="120">
          <template #default="{ row }">
            <el-link 
              v-if="row.drawing_pdf" 
              :href="row.drawing_pdf" 
              target="_blank"
              type="primary"
            >
              <el-icon><Document /></el-icon> 查看
            </el-link>
            <span v-else class="no-file">无</span>
          </template>
        </el-table-column>
        <el-table-column label="工艺PDF" align="center" width="120">
          <template #default="{ row }">
            <el-link 
              v-if="row.process_pdf" 
              :href="row.process_pdf" 
              target="_blank"
              type="primary"
            >
              <el-icon><Document /></el-icon> 查看
            </el-link>
            <span v-else class="no-file">无</span>
          </template>
        </el-table-column>
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
    
    <!-- 添加产品类对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增产品类"
      width="760px"
      destroy-on-close
    >
      <el-form
        ref="addFormRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="产品类名称" prop="name">
              <el-input v-model="form.name" maxlength="30" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属公司" prop="company">
              <el-select v-model="form.company" filterable placeholder="选择公司">
                <el-option
                  v-for="item in companies"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="图纸PDF">
          <el-upload
            class="pdf-uploader"
            :auto-upload="false"
            accept=".pdf"
            :limit="1"
            v-model:file-list="drawingFileList"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="upload-tip">仅支持PDF格式文件</div>
            </template>
          </el-upload>
          
          <pdf-preview
            v-if="drawingFileList.length > 0"
            :file="drawingFileList[0].raw"
            :url="drawingFileList[0].url"
          />
        </el-form-item>
        
        <el-form-item label="工艺PDF">
          <el-upload
            class="pdf-uploader"
            :auto-upload="false"
            accept=".pdf"
            :limit="1"
            v-model:file-list="processFileList"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="upload-tip">仅支持PDF格式文件</div>
            </template>
          </el-upload>
          
          <pdf-preview
            v-if="processFileList.length > 0"
            :file="processFileList[0].raw"
            :url="processFileList[0].url"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitAdd">
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑产品类对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑产品类"
      width="760px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="产品类名称" prop="name">
              <el-input v-model="form.name" maxlength="30" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属公司" prop="company">
              <el-select v-model="form.company" filterable placeholder="选择公司">
                <el-option
                  v-for="item in companies"
                  :key="item?.id || 'empty'"
                  :label="item?.name || ''"
                  :value="item?.id || null"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="图纸PDF">
          <div v-if="form.drawing_pdf && !drawingFileList.length" class="current-file">
            <span>当前文件：</span>
            <el-link :href="form.drawing_pdf" target="_blank" type="primary">
              <el-icon><Document /></el-icon> 查看PDF
            </el-link>
          </div>
          
          <el-upload
            class="pdf-uploader"
            :auto-upload="false"
            accept=".pdf"
            :limit="1"
            v-model:file-list="drawingFileList"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="upload-tip">上传新文件将替换当前文件</div>
            </template>
          </el-upload>
          
          <pdf-preview
            v-if="drawingFileList.length > 0"
            :file="drawingFileList[0].raw"
            :url="drawingFileList[0].url"
          />
        </el-form-item>
        
        <el-form-item label="工艺PDF">
          <div v-if="form.process_pdf && !processFileList.length" class="current-file">
            <span>当前文件：</span>
            <el-link :href="form.process_pdf" target="_blank" type="primary">
              <el-icon><Document /></el-icon> 查看PDF
            </el-link>
          </div>
          
          <el-upload
            class="pdf-uploader"
            :auto-upload="false"
            accept=".pdf"
            :limit="1"
            v-model:file-list="processFileList"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="upload-tip">上传新文件将替换当前文件</div>
            </template>
          </el-upload>
          
          <pdf-preview
            v-if="processFileList.length > 0"
            :file="processFileList[0].raw"
            :url="processFileList[0].url"
          />
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
import { Plus, Edit, Delete, Document, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type UploadUserFile } from 'element-plus'
import { api } from '../../../api/index'
import { fetchData, createData, updateData, deleteData } from '../../../api/apiUtils'
import PdfPreview from '../../../components/common/PdfPreview.vue'

// 类型定义
interface ProductCategory {
  id: number;
  name: string;
  company: number;
  company_name?: string;
  drawing_pdf?: string;
  process_pdf?: string;
}

interface ProductCategoryForm {
  id?: number;
  name: string;
  company: number | null;
  drawing_pdf?: string;
  process_pdf?: string;
}

interface Company {
  id: number;
  name: string;
  code: string;
  address?: string;
  contact?: string;
  phone?: string;
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const search = ref('')
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const categories = ref<ProductCategory[]>([])
const companies = ref<Company[]>([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const drawingFileList = ref<UploadUserFile[]>([])
const processFileList = ref<UploadUserFile[]>([])
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

// 表单相关
const form = reactive<ProductCategoryForm>({
  name: '',
  company: null,
  drawing_pdf: '',
  process_pdf: ''
})

const rules = {
  name: [
    { required: true, message: '请输入产品类名称', trigger: 'blur' },
    { min: 1, max: 30, message: '长度在1到30个字符', trigger: 'blur' }
  ],
  company: [
    { required: true, message: '请选择公司', trigger: 'change' }
  ]
}

// 计算属性
const filteredCategories = computed(() => {
  if (!search.value) return categories.value
  return categories.value.filter(c => 
    c.name && c.name.toLowerCase().includes(search.value.toLowerCase())
  )
})

// 数据加载方法
const fetchCategories = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await api.get('/api/product-categories/', { params })
    
    // 处理API拦截器添加的统一封装格式
    if (response.data && response.data.success) {
      const responseData = response.data.data // 获取内部的实际数据
      
      // 处理分页或数组格式
      if (responseData && Array.isArray(responseData.results)) {
        categories.value = responseData.results
        total.value = responseData.count || 0
      } else if (responseData && Array.isArray(responseData)) {
        categories.value = responseData
        total.value = responseData.length
      } else {
        categories.value = []
        total.value = 0
        console.warn('未能识别的数据格式:', responseData)
      }
      
      // 无数据并且不是第一页，则跳到第一页
      if (currentPage.value > 1 && categories.value.length === 0 && total.value > 0) {
        currentPage.value = 1
        await fetchCategories()
      }
    } else {
      categories.value = []
      total.value = 0
      if (response.data && !response.data.success) {
        ElMessage.error(response.data.message || '获取产品类列表失败')
      }
    }
  } catch (error) {
    categories.value = []
    total.value = 0
    ElMessage.error('获取产品类列表失败')
    console.error('获取产品类列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchCompanies = async () => {
  try {
    const response = await api.get('/api/basedata/companies/')
    
    // 处理API拦截器添加的统一封装格式
    if (response.data && response.data.success) {
      const responseData = response.data.data
      
      // 处理分页或数组格式
      if (responseData && Array.isArray(responseData.results)) {
        companies.value = responseData.results
      } else if (responseData && Array.isArray(responseData)) {
        companies.value = responseData
      } else {
        companies.value = []
        console.warn('未能识别的数据格式:', responseData)
      }
    } else {
      companies.value = []
      if (response.data && !response.data.success) {
        ElMessage.error(response.data.message || '获取公司列表失败')
      }
    }
  } catch (error) {
    companies.value = []
    ElMessage.error('获取公司列表失败')
    console.error('获取公司列表失败:', error)
  }
}

// 处理事件
const handleSearch = () => {
  currentPage.value = 1
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchCategories()
}

const handleCurrentChange = (val: number) => {
  fetchCategories()
}

const resetForm = () => {
  form.id = undefined
  form.name = ''
  form.company = null
  form.drawing_pdf = ''
  form.process_pdf = ''
  drawingFileList.value = []
  processFileList.value = []
}

const openAddDialog = () => {
  resetForm()
  showAddDialog.value = true
  nextTick(() => {
    addFormRef.value?.resetFields()
  })
}

const openEditDialog = (row: ProductCategory) => {
  resetForm()
  form.id = row?.id
  form.name = row?.name || ''
  form.company = row?.company || null
  form.drawing_pdf = row?.drawing_pdf || ''
  form.process_pdf = row?.process_pdf || ''
  showEditDialog.value = true
  nextTick(() => {
    editFormRef.value?.resetFields()
  })
}

const confirmDelete = (row: ProductCategory) => {
  ElMessageBox.confirm(
    `确定要删除产品类 "${row.name}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteCategory(row.id)
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
      const formData = new FormData()
      formData.append('name', form.name)
      formData.append('company', form.company!.toString())
      
      if (drawingFileList.value.length > 0 && drawingFileList.value[0].raw) {
        formData.append('drawing_pdf', drawingFileList.value[0].raw)
      }
      
      if (processFileList.value.length > 0 && processFileList.value[0].raw) {
        formData.append('process_pdf', processFileList.value[0].raw)
      }
      
      const response = await api.post('/api/product-categories/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      if (response.data && response.data.success) {
        ElMessage.success('新增产品类成功')
        showAddDialog.value = false
        currentPage.value = 1
        fetchCategories()
      } else if (response.data && !response.data.success) {
        ElMessage.error(response.data.message || '新增产品类失败')
      }
    } catch (error) {
      ElMessage.error('新增产品类失败')
      console.error('新增产品类失败:', error)
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
      const formData = new FormData()
      formData.append('name', form.name)
      formData.append('company', form.company!.toString())
      
      if (drawingFileList.value.length > 0 && drawingFileList.value[0].raw) {
        formData.append('drawing_pdf', drawingFileList.value[0].raw)
      }
      
      if (processFileList.value.length > 0 && processFileList.value[0].raw) {
        formData.append('process_pdf', processFileList.value[0].raw)
      }
      
      const response = await api.put(`/api/product-categories/${form.id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      if (response.data && response.data.success) {
        ElMessage.success('更新产品类成功')
        showEditDialog.value = false
        fetchCategories()
      } else if (response.data && !response.data.success) {
        ElMessage.error(response.data.message || '更新产品类失败')
      }
    } catch (error) {
      ElMessage.error('更新产品类失败')
      console.error('更新产品类失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteCategory = async (id: number) => {
  loading.value = true
  try {
    const response = await api.delete(`/api/product-categories/${id}/`)
    
    if (response.data && response.data.success) {
      ElMessage.success('删除产品类成功')
      
      // 如果当前页删除后没有数据了，尝试跳到上一页
      if (categories.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }
      
      fetchCategories()
    } else if (response.data && !response.data.success) {
      ElMessage.error(response.data.message || '删除产品类失败')
    }
  } catch (error) {
    ElMessage.error('删除产品类失败')
    console.error('删除产品类失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(async () => {
  await fetchCompanies()
  await fetchCategories()
})
</script>

<style lang="scss" scoped>
.product-category-container {
  padding: 16px;
  
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .page-title {
      font-size: 18px;
      margin: 0;
      color: var(--el-text-color-primary);
    }
    
    .search-actions {
      display: flex;
      gap: 12px;
      align-items: center;
      
      .el-input {
        width: 240px;
      }
    }
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
  }
  
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
  
  .no-file {
    color: var(--el-text-color-secondary);
  }
  
  .current-file {
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .pdf-uploader {
    margin-bottom: 12px;
    
    .upload-tip {
      color: var(--el-text-color-secondary);
      font-size: 12px;
      margin-top: 8px;
    }
  }
}
</style>
