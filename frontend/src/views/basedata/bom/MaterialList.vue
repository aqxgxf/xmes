<template>
  <div class="material-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">物料管理</h2>
          <div class="search-actions">
            <el-input
              v-model="search"
              placeholder="搜索物料名称/代码"
              clearable
              prefix-icon="Search"
              @input="handleSearch"
            />
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon> 新增物料
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
        :data="filteredMaterials"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="code" label="物料代码" min-width="120" />
        <el-table-column prop="name" label="物料名称" min-width="200" />
        <el-table-column prop="price" label="单价" min-width="100" />
        <el-table-column prop="category_name" label="物料类别" min-width="120" />
        <el-table-column prop="unit_name" label="单位" min-width="80" />
        <el-table-column prop="drawing_pdf_url" label="图纸PDF" min-width="120" align="center">
          <template #default="{ row }">
            <el-link 
              v-if="row.drawing_pdf_url" 
              :href="row.drawing_pdf_url.replace(/\/$/, '')" 
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
    
    <!-- 新增物料对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增物料"
      width="70%"
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
        <el-form-item label="物料类别" prop="category">
          <el-select
            v-model="form.category"
            placeholder="请选择物料类别"
            filterable
            class="form-select"
            @change="onCategoryChange"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.display_name + ' (' + cat.code + ')'"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="物料代码" prop="code">
          <el-input
            v-model="form.code"
            maxlength="100"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="物料名称" prop="name">
          <el-input
            v-model="form.name"
            maxlength="100"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="单价" prop="price">
          <el-input-number
            v-model="form.price"
            :precision="2"
            :min="0"
            class="form-input-number"
          />
        </el-form-item>
        
        <el-form-item label="单位" prop="unit">
          <el-select
            v-model="form.unit"
            placeholder="请选择单位"
            filterable
            clearable
            class="form-select"
          >
            <el-option
              v-for="unit in units"
              :key="unit.id"
              :label="`${unit.name} (${unit.code})`"
              :value="unit.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item
          v-for="param in params"
          :key="param.id"
          :label="param.name"
          :prop="`paramValues.${param.id}`"
        >
          <el-input
            v-model="form.paramValues[param.id]"
            class="form-input-param"
          />
        </el-form-item>
        
        <el-form-item label="图纸PDF" prop="drawing_pdf">
          <el-upload
            class="pdf-uploader"
            :auto-upload="false"
            accept=".pdf"
            :limit="1"
            v-model:file-list="drawingAddFileList"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="upload-tip">仅支持PDF格式文件</div>
            </template>
          </el-upload>
          
          <pdf-preview
            v-if="drawingAddFileList.length > 0"
            :file="drawingAddFileList[0].raw"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeAddDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="saveMaterial"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑物料对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑物料"
      width="70%"
      destroy-on-close
      @close="closeEditDialog"
      @opened="onEditDialogOpened"
    >
      <el-form
        ref="editFormRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="left"
        class="form-container"
      >
        <el-form-item label="物料类别" prop="category">
          <el-select
            v-model="form.category"
            placeholder="请选择物料类别"
            filterable
            class="form-select"
            @change="onCategoryChange"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.display_name + ' (' + cat.code + ')'"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="物料代码" prop="code">
          <el-input
            v-model="form.code"
            maxlength="100"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="物料名称" prop="name">
          <el-input
            v-model="form.name"
            maxlength="100"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="单价" prop="price">
          <el-input-number
            v-model="form.price"
            :precision="2"
            :min="0"
            class="form-input-number"
          />
        </el-form-item>
        
        <el-form-item label="单位" prop="unit">
          <el-select
            v-model="form.unit"
            placeholder="请选择单位"
            filterable
            clearable
            class="form-select"
          >
            <el-option
              v-for="unit in units"
              :key="unit.id"
              :label="`${unit.name} (${unit.code})`"
              :value="unit.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item
          v-for="param in params"
          :key="param.id"
          :label="param.name"
          :prop="`paramValues.${param.id}`"
        >
          <el-input
            v-model="form.paramValues[param.id]"
            class="form-input-param"
          />
        </el-form-item>
        
        <el-form-item label="图纸PDF" prop="drawing_pdf">
          <div v-if="form.drawing_pdf_url && !drawingEditFileList.length" class="current-file">
            <span>当前文件：</span>
            <el-link :href="form.drawing_pdf_url" target="_blank" type="primary">
              <el-icon><Document /></el-icon> 查看PDF
            </el-link>
          </div>
          
          <el-upload
            class="pdf-uploader"
            :auto-upload="false"
            accept=".pdf"
            :limit="1"
            v-model:file-list="drawingEditFileList"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="upload-tip">上传新文件将替换当前文件</div>
            </template>
          </el-upload>
          
          <pdf-preview
            v-if="drawingEditFileList.length > 0"
            :file="drawingEditFileList[0].raw"
            :url="drawingEditFileList.length === 0 && form.drawing_pdf_url ? form.drawing_pdf_url : undefined"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeEditDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="updateMaterial"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type UploadUserFile } from 'element-plus'
import { Plus, Edit, Delete, Upload, Search, Document } from '@element-plus/icons-vue'
import axios from 'axios'
import PdfPreview from '../../../components/common/PdfPreview.vue'

// 类型定义
interface Material {
  id: number;
  code: string;
  name: string;
  price: number | string;
  category: number;
  category_name?: string;
  unit?: number | null;
  unit_name?: string;
  drawing_pdf_url?: string;
  param_values?: ParamValue[];
}

interface Category {
  id: number;
  code: string;
  display_name: string;
  company: number;
  company_name?: string;
  drawing_pdf?: string;
  process_pdf?: string;
}

interface Param {
  id: number;
  name: string;
  category: number;
}

interface ParamValue {
  param: number;
  value: string;
}

interface Unit {
  id: number;
  code: string;
  name: string;
  description?: string;
}

interface MaterialForm {
  id: number | null;
  code: string;
  name: string;
  price: number | string;
  category: number | null;
  unit: number | null;
  paramValues: Record<number, string>;
  drawing_pdf_url?: string;
}

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入物料名称', trigger: 'blur' },
    { max: 100, message: '最大长度不能超过100', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入物料代码', trigger: 'blur' },
    { max: 100, message: '最大长度不能超过100', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择物料类别', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入单价', trigger: 'blur' }
  ]
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const materials = ref<Material[]>([])
const categories = ref<Category[]>([])
const units = ref<Unit[]>([])
const params = ref<Param[]>([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const search = ref('')
const drawingAddFileList = ref<UploadUserFile[]>([])
const drawingEditFileList = ref<UploadUserFile[]>([])

// 表单对象
const form = reactive<MaterialForm>({
  id: null,
  code: '',
  name: '',
  price: '',
  category: null,
  unit: null,
  paramValues: {}
})

// 搜索过滤
const filteredMaterials = computed(() => {
  if (!search.value) return materials.value
  
  const searchTerm = search.value.toLowerCase()
  return materials.value.filter(material => {
    return (
      material.name.toLowerCase().includes(searchTerm) ||
      material.code.toLowerCase().includes(searchTerm)
    )
  })
})

// 数据加载
const fetchMaterials = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/materials/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    
    if (response.data && response.data.results) {
      materials.value = response.data.results
      total.value = response.data.count
    } else if (Array.isArray(response.data)) {
      materials.value = response.data
      total.value = response.data.length
    } else {
      materials.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取物料列表失败:', error)
    ElMessage.error('获取物料列表失败')
    materials.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/product-categories/')
    if (response.data && response.data.results) {
      categories.value = response.data.results
    } else if (Array.isArray(response.data)) {
      categories.value = response.data
    } else {
      categories.value = []
    }
  } catch (error) {
    console.error('获取物料类别失败:', error)
    ElMessage.error('获取物料类别失败')
    categories.value = []
  }
}

const fetchCategoryParams = async (categoryId: number) => {
  try {
    // 使用正确的API端点获取产品类别的参数项
    const response = await axios.get(`/api/product-categories/${categoryId}/params/`)
    
    console.log('物料类别参数原始响应:', response.data)
    
    if (response.data && response.data.results) {
      params.value = response.data.results
    } else if (Array.isArray(response.data)) {
      params.value = response.data
    } else {
      params.value = []
    }
    
    console.log('处理后的参数项数据:', params.value)
  } catch (error) {
    console.error('获取类别参数失败:', error)
    ElMessage.error('获取类别参数失败')
    params.value = []
  }
}

const fetchUnits = async () => {
  try {
    const response = await axios.get('/api/units/', { 
      params: { page_size: 999 } // 获取所有单位
    });
    
    if (response.data && response.data.results) {
      units.value = response.data.results;
    } else if (Array.isArray(response.data)) {
      units.value = response.data;
    } else {
      units.value = [];
    }
  } catch (error) {
    console.error('获取单位列表失败:', error);
    units.value = [];
  }
}

// 处理页面事件
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchMaterials()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchMaterials()
}

const handleSearch = () => {
  currentPage.value = 1
  if (search.value === '') {
    fetchMaterials()
  }
}

// 选择类别变更时获取参数
const onCategoryChange = async (categoryId: number) => {
  // 清空参数值和参数列表
  form.paramValues = {}
  params.value = []
  
  if (categoryId) {
    console.log('类别变更，获取参数项:', categoryId)
    await fetchCategoryParams(categoryId)
  }
}

// 对话框操作
const openAddDialog = () => {
  form.id = null
  form.code = ''
  form.name = ''
  form.price = ''
  form.category = null
  form.unit = null
  form.paramValues = {}
  form.drawing_pdf_url = undefined
  
  drawingAddFileList.value = []
  params.value = []
  showAddDialog.value = true
}

const closeAddDialog = () => {
  showAddDialog.value = false
}

const openEditDialog = async (material: Material) => {
  form.id = material.id
  form.code = material.code
  form.name = material.name
  form.price = material.price
  form.category = material.category
  form.unit = material.unit ?? null
  form.drawing_pdf_url = material.drawing_pdf_url
  form.paramValues = {}
  
  // 清空现有参数
  params.value = []
  
  // 如果有category，先获取参数
  if (material.category) {
    await fetchCategoryParams(material.category)
    
    // 获取参数后，再填充参数值
    if (material.param_values && material.param_values.length > 0) {
      material.param_values.forEach(pv => {
        form.paramValues[pv.param] = pv.value
      })
    }
  }
  
  drawingEditFileList.value = []
  showEditDialog.value = true
}

const onEditDialogOpened = () => {
  // 对话框打开后额外操作（如需要）
}

const closeEditDialog = () => {
  showEditDialog.value = false
}

// 自动填充物料代码
const autoFillMaterialCode = () => {
  const cat = categories.value.find(c => c.id === form.category)
  let code = cat ? cat.code : ''
  
  // 添加数组检查
  if (Array.isArray(params.value) && params.value.length > 0) {
    params.value.forEach(p => {
      const val = form.paramValues[p.id]
      if (val) code += '-' + p.name + '-' + val
    })
  }
  
  form.code = code
}

// 监听参数变化自动填充代码
watch([() => form.category, () => form.paramValues], autoFillMaterialCode, { deep: true })

// 自动填充物料名称
const autoFillMaterialName  = () => {
  const cat = categories.value.find(c => c.id === form.category)
  let name = cat ? cat.display_name : ''
  
  // 添加数组检查
  if (Array.isArray(params.value) && params.value.length > 0) {
    params.value.forEach(p => {
      const val = form.paramValues[p.id]
      if (val) name += '-' + p.name + '-' + val
    })
  }
  
  form.name = name
}

// 监听参数变化自动填充代码
watch([() => form.category, () => form.paramValues], autoFillMaterialName, { deep: true })


// 保存物料
const saveMaterial = async () => {
  if (!addFormRef.value) return
  
  await addFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      const formData = new FormData()
      formData.append('code', form.code)
      formData.append('name', form.name)
      formData.append('price', String(form.price))
      formData.append('category', String(form.category || ''))
      
      // Add unit if selected
      if (form.unit !== null) {
        formData.append('unit', String(form.unit))
      }
      
      // Add drawing file if selected
      if (drawingAddFileList.value.length > 0 && drawingAddFileList.value[0].raw) {
        formData.append('drawing_pdf', drawingAddFileList.value[0].raw)
      }
      
      // Add param values
      if (form.paramValues && Object.keys(form.paramValues).length > 0) {
        const paramValues = Object.entries(form.paramValues)
          .filter(([paramId, value]) => value.trim() !== '') // 过滤掉空值
          .map(([paramId, value]) => ({
            param: parseInt(paramId),
            value: value.trim()
          }))
        
        if (paramValues.length > 0) {
          console.log('添加参数值:', paramValues)
          formData.append('param_values', JSON.stringify(paramValues))
        }
      }
      
      // Add is_material marker
      formData.append('is_material', 'true')
      
      // Send request
      console.log('提交物料数据:', Object.fromEntries(formData.entries()))
      const response = await axios.post('/api/materials/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      ElMessage.success('添加物料成功')
      closeAddDialog()
      await fetchMaterials()
    } catch (error: any) {
      console.error('保存物料失败:', error)
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      submitting.value = false
    }
  })
}

const updateMaterial = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      const formData = new FormData()
      formData.append('code', form.code)
      formData.append('name', form.name)
      formData.append('price', String(form.price))
      formData.append('category', String(form.category || ''))
      
      // Add unit if selected
      if (form.unit !== null) {
        formData.append('unit', String(form.unit))
      }
      
      // Add drawing file if selected
      if (drawingEditFileList.value.length > 0 && drawingEditFileList.value[0].raw) {
        formData.append('drawing_pdf', drawingEditFileList.value[0].raw)
      }
      
      // Add param values
      if (form.paramValues && Object.keys(form.paramValues).length > 0) {
        const paramValues = Object.entries(form.paramValues)
          .filter(([paramId, value]) => value.trim() !== '') // 过滤掉空值
          .map(([paramId, value]) => ({
            param: parseInt(paramId),
            value: value.trim()
          }))
        
        if (paramValues.length > 0) {
          console.log('更新参数值:', paramValues)
          formData.append('param_values', JSON.stringify(paramValues))
        }
      }
      
      // Add is_material marker
      formData.append('is_material', 'true')
      
      console.log('更新物料数据:', Object.fromEntries(formData.entries()))
      const response = await axios.put(`/api/materials/${form.id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      ElMessage.success('更新物料成功')
      closeEditDialog()
      await fetchMaterials()
    } catch (error: any) {
      console.error('更新物料失败:', error)
      ElMessage.error(error.response?.data?.detail || '更新失败')
    } finally {
      submitting.value = false
    }
  })
}

// 删除物料
const confirmDelete = (material: Material) => {
  ElMessageBox.confirm(
    `确定要删除物料 "${material.name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteMaterial(material.id)
  }).catch(() => {
    // 用户取消删除
  })
}

const deleteMaterial = async (id: number) => {
  loading.value = true
  
  try {
    await axios.delete(`/api/materials/${id}/`)
    ElMessage.success('删除物料成功')
    await fetchMaterials()
  } catch (error: any) {
    console.error('删除物料失败:', error)
    ElMessage.error(error.response?.data?.detail || '删除失败')
  } finally {
    loading.value = false
  }
}

// 导入物料
const beforeImport = (file: File) => {
  const validExtensions = ['.xlsx', '.xls', '.csv']
  const fileName = file.name
  const extension = fileName.slice(fileName.lastIndexOf('.'))
  
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
    
    // 使用专用的物料导入接口
    const response = await axios.post('/api/materials/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    ElMessage.success(response.data?.msg || '导入物料成功')
    await fetchMaterials()
  } catch (error: any) {
    console.error('导入物料失败:', error)
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '导入失败')
  } finally {
    loading.value = false
  }
}

// 页面初始化
onMounted(async () => {
  await fetchCategories()
  await fetchUnits()
  await fetchMaterials()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.material-container {
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
    max-height: 60vh;
    width: 500px;
    overflow-y: auto;
    padding-right: 16px;
  }
  
  .form-input, .form-select {
    width: 400px;
  }

  .form-input-number {
    width: 140px;
  }
 
  .form-input-param {
    width: 200px;
  }

  .current-file {
    margin-bottom: 12px;
  }
  
  .pdf-uploader {
    margin-bottom: 16px;
  }
  
  .no-file {
    color: #909399;
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