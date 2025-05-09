<template>
  <div class="product-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">产品管理</h2>
          <div class="search-actions">
            <el-input
              v-model="search"
              placeholder="搜索产品名称"
              clearable
              prefix-icon="Search"
              @input="handleSearch"
            />
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon> 新增产品
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
        :data="filteredProducts"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="code" label="产品代码" min-width="120" />
        <el-table-column prop="name" label="产品名称" min-width="200" />
        <el-table-column prop="price" label="价格" min-width="100" />
        <el-table-column prop="category_name" label="产品类" min-width="120" />
        <el-table-column prop="unit_name" label="单位" min-width="120" />
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
    
    <!-- 新增产品对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增产品"
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
        <el-form-item label="产品类" prop="category">
          <el-select
            v-model="form.category"
            placeholder="请选择产品类"
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
        
        <el-form-item label="产品代码" prop="code">
          <el-input
            v-model="form.code"
            maxlength="100"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="产品名称" prop="name">
          <el-input
            v-model="form.name"
            maxlength="100"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="价格" prop="price">
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
          @click="saveProduct"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑产品对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑产品"
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
        <el-form-item label="产品类" prop="category">
          <el-select
            v-model="form.category"
            placeholder="请选择产品类"
            filterable
            class="form-select"
            @change="onCategoryChange"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.display_name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="产品代码" prop="code">
          <el-input
            v-model="form.code"
            maxlength="100"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="产品名称" prop="name">
          <el-input
            v-model="form.name"
            maxlength="40"
            show-word-limit
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="价格" prop="price">
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
          @click="updateProduct"
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
import { api } from '../../../api/index'
import apiService from '../../../api/index'
import PdfPreview from '../../../components/common/PdfPreview.vue'

// 类型定义
interface Product {
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

interface ProductForm {
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
    { required: true, message: '请输入产品名称', trigger: 'blur' },
    { max: 40, message: '最大长度不能超过100', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入产品代码', trigger: 'blur' },
    { max: 100, message: '最大长度不能超过100', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择产品类', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' }
  ]
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const products = ref<Product[]>([])
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
const form = reactive<ProductForm>({
  id: null,
  code: '',
  name: '',
  price: '',
  category: null,
  unit: null,
  paramValues: {}
})

// 计算属性
const filteredProducts = computed(() => products.value)

// 数据加载方法
const fetchProducts = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: search.value
    }
    
    const response = await api.get('/api/products/', { params })
    
    if (response.data && response.data.success === true) {
      // 处理API封装格式
      const responseData = response.data.data || {}
      
      if (responseData && Array.isArray(responseData.results)) {
        products.value = responseData.results.map(mapProductData)
        total.value = responseData.count || 0
      } else if (responseData && Array.isArray(responseData)) {
        products.value = responseData.map(mapProductData)
        total.value = responseData.length
      } else {
        products.value = []
        total.value = 0
        console.warn('未识别的产品数据格式:', responseData)
      }
    } else if (response.data) {
      // 直接处理返回数据
      if (Array.isArray(response.data.results)) {
        products.value = response.data.results.map(mapProductData)
        total.value = response.data.count || 0
      } else if (Array.isArray(response.data)) {
        products.value = response.data.map(mapProductData)
        total.value = response.data.length
      } else {
        products.value = []
        total.value = 0
        console.warn('未识别的产品数据格式:', response.data)
      }
    } else {
      products.value = []
      total.value = 0
    }
  } catch (error) {
    products.value = []
    total.value = 0
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
  } finally {
    loading.value = false
  }
}

// 映射产品数据并补充类别名称
const mapProductData = (product: Product): Product => {
  // 添加安全检查，确保categories.value是数组且有find方法
  const categoryName = Array.isArray(categories.value) && categories.value.length > 0
    ? categories.value.find(c => c.id === product.category)?.display_name || ''
    : '';
    
  return {
    ...product,
    category_name: categoryName
  }
}

const fetchCategories = async () => {
  try {
    // 使用预定义的API方法并添加日志记录
    console.log('正在获取产品类别...')
    const response = await apiService.basedata.getProductCategories({ page_size: 999 })
    
    console.log('产品类别原始响应:', response.data)
    
    // 确保categories.value始终是数组
    if (response.data && response.data.success === true) {
      const responseData = response.data.data || {}
      
      if (responseData && Array.isArray(responseData.results)) {
        categories.value = responseData.results
      } else if (responseData && Array.isArray(responseData)) {
        categories.value = responseData
      } else {
        categories.value = []
        console.warn('产品类别数据不是数组格式:', responseData)
      }
    } else if (response.data) {
      if (Array.isArray(response.data.results)) {
        categories.value = response.data.results
      } else if (Array.isArray(response.data)) {
        categories.value = response.data
      } else {
        categories.value = []
        console.warn('产品类别数据不是数组格式:', response.data)
      }
    } else {
      categories.value = []
    }
    
    // 确认最终结果是否为数组
    if (!Array.isArray(categories.value)) {
      console.error('categories.value不是数组，重置为空数组')
      categories.value = []
    }
    
    console.log('处理后的产品类别数据:', categories.value)
  } catch (error) {
    console.error('获取产品类别失败:', error)
    ElMessage.error('获取产品类别失败')
    categories.value = []
  }
}

// 加载单位数据
const fetchUnits = async () => {
  try {
    const response = await api.get('/api/units/', { 
      params: { page_size: 999 } // 获取所有单位
    });
    
    // 处理API响应
    if (response.data && response.data.success === true) {
      // API封装格式
      const responseData = response.data.data || {};
      
      if (responseData && Array.isArray(responseData.results)) {
        units.value = responseData.results;
      } else if (responseData && Array.isArray(responseData)) {
        units.value = responseData;
      } else {
        units.value = [];
        console.warn('未识别的单位数据格式:', responseData);
      }
    } else if (response.data) {
      // 直接处理返回数据
      if (Array.isArray(response.data.results)) {
        units.value = response.data.results;
      } else if (Array.isArray(response.data)) {
        units.value = response.data;
      } else {
        units.value = [];
        console.warn('未识别的单位数据格式:', response.data);
      }
    } else {
      units.value = [];
    }
  } catch (error) {
    units.value = [];
    console.error('获取单位列表失败:', error);
  }
}

// 处理事件
const handleSearch = () => {
  currentPage.value = 1
  fetchProducts()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchProducts()
}

const handleCurrentChange = () => {
  fetchProducts()
}

const confirmDelete = (row: Product) => {
  ElMessageBox.confirm(
    `<p>确定要删除产品 "${row.name}" 吗？此操作不可撤销。</p><p style="color: #E6A23C; margin-top: 10px;">注意：如果该产品已被生产订单或其他记录引用，则无法删除。</p>`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: true
    }
  ).then(() => {
    deleteProduct(row.id)
  }).catch(() => {
    // 用户取消操作
  })
}

// 显示开发者故障排除对话框
const showTroubleshootingDialog = () => {
  ElMessageBox.alert(
    `<h3>数据库迁移问题</h3>
    <p>系统检测到数据库缺少必要的表结构：<code>productionmgmt_productionorder</code></p>
    <p>这个问题通常是因为没有正确执行数据库迁移导致的。请联系技术人员执行以下操作：</p>
    <ol>
      <li>进入后端项目目录</li>
      <li>执行 <code>python manage.py makemigrations productionmgmt</code></li>
      <li>执行 <code>python manage.py migrate productionmgmt</code></li>
    </ol>
    <p>完成后，产品删除功能将正常工作。</p>`,
    '后端数据库配置问题',
    {
      confirmButtonText: '我了解了',
      dangerouslyUseHTMLString: true,
    }
  )
}

const deleteProduct = async (id: number) => {
  loading.value = true
  
  try {
    console.log(`正在删除产品 ID: ${id}`)
    await api.delete(`/api/products/${id}/`)
    ElMessage.success('删除产品成功')
    
    // 如果当前页删除后没有数据了，尝试跳到上一页
    if (products.value.length === 1 && currentPage.value > 1) {
      currentPage.value--
    }
    
    fetchProducts()
  } catch (error: any) {
    console.error('删除产品失败:', error)
    
    // 记录详细错误信息用于调试
    if (error.response) {
      console.error('错误响应状态:', error.response.status)
      console.error('错误响应数据:', error.response.data)
    }
    
    // 提取具体的错误信息，提供更友好的提示
    let errorMsg = '删除产品失败'
    let detailMsg = ''
    
    if (error.response?.data) {
      // 检查是否包含详细的错误信息
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (typeof error.response.data === 'object') {
        if (error.response.data.detail) {
          errorMsg = error.response.data.detail
        } else if (error.response.data.message) {
          errorMsg = error.response.data.message
        } else if (error.response.data.error) {
          errorMsg = error.response.data.error
        }
      }
    }
    
    // 检查是否为缺少表的错误
    if (error.message && error.message.includes('no such table: productionmgmt_productionorder')) {
      errorMsg = '数据库表结构不完整，无法检查产品依赖关系'
      detailMsg = '需要执行数据库迁移。请点击"查看解决方案"获取详情。'
      
      // 添加开发者故障排除说明
      console.warn('===== 开发者说明 =====')
      console.warn('问题：缺少 productionmgmt_productionorder 表')
      console.warn('原因：productionmgmt 应用的数据库迁移未创建或未应用')
      console.warn('解决方案:')
      console.warn('1. 进入项目后端目录')
      console.warn('2. 执行 python manage.py makemigrations productionmgmt')
      console.warn('3. 执行 python manage.py migrate productionmgmt')
      console.warn('=====================')
      
      // 显示错误消息并提供查看详情选项
      ElMessageBox.confirm(
        '数据库结构配置有误，无法完成删除操作。这是一个后端配置问题，需要技术人员修复。',
        '操作失败',
        {
          confirmButtonText: '查看解决方案',
          cancelButtonText: '关闭',
          type: 'error'
        }
      ).then(() => {
        showTroubleshootingDialog()
      }).catch(() => {})
      
      return
    } else if (error.message && error.message.includes('no such table')) {
      errorMsg = '数据库表结构不完整，无法完成删除操作'
      detailMsg = `后端错误: ${error.message}`
    }
    
    // 显示主要错误信息
    ElMessage.error(errorMsg)
    
    // 如果有详细信息，使用单独的通知显示
    if (detailMsg) {
      ElMessage({
        type: 'warning',
        message: detailMsg,
        duration: 8000, // 显示更长时间
        showClose: true
      })
    }
  } finally {
    loading.value = false
  }
}

// 对话框处理
const openAddDialog = () => {
  resetForm()
  showAddDialog.value = true
  drawingAddFileList.value = []
  
  nextTick(() => {
    if (addFormRef.value) {
      addFormRef.value.resetFields()
    }
  })
}

const openEditDialog = (row: Product) => {
  resetForm()
  
  form.id = row.id
  form.code = row.code
  form.name = row.name
  form.price = row.price
  form.category = row.category
  form.drawing_pdf_url = row.drawing_pdf_url
  drawingEditFileList.value = []
  
  // 加载该产品类别的参数项
  if (row.category) {
    onCategoryChange()
  }
  
  // 处理参数值
  if (row.param_values && Array.isArray(row.param_values)) {
    form.paramValues = {}
    row.param_values.forEach(pv => {
      form.paramValues[pv.param] = pv.value
    })
  }
  
  showEditDialog.value = true
  
  nextTick(() => {
    if (editFormRef.value) {
      editFormRef.value.resetFields()
    }
  })
}

const onEditDialogOpened = async () => {
  await nextTick()
  
  // 对话框打开后的初始化逻辑
  // 不需要手动渲染PDF，PdfPreview组件会自动处理
}

const closeAddDialog = () => {
  showAddDialog.value = false
  resetForm()
  drawingAddFileList.value = []
}

const closeEditDialog = () => {
  showEditDialog.value = false
  resetForm()
  drawingEditFileList.value = []
}

const resetForm = () => {
  form.id = null
  form.code = ''
  form.name = ''
  form.price = ''
  form.category = null
  form.paramValues = {}
  form.drawing_pdf_url = undefined
  params.value = []
}

// 自动填充产品代码
const autoFillProductCode = () => {
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
watch([() => form.category, () => form.paramValues], autoFillProductCode, { deep: true })

// 自动填充产品名称
const autoFillProductName  = () => {
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
watch([() => form.category, () => form.paramValues], autoFillProductName, { deep: true })


// 加载选定类别的参数项
const onCategoryChange = async () => {
  if (!form.category) return
  
  try {
    console.log('正在获取产品类别参数项:', form.category)
    const response = await api.get(`/api/product-categories/${form.category}/params/`)
    
    console.log('产品类别参数项原始响应:', response.data)
    
    // 确保params.value始终是数组
    if (response.data && response.data.success === true) {
      const responseData = response.data.data || {}
      
      if (responseData && Array.isArray(responseData.results)) {
        params.value = responseData.results
      } else if (responseData && Array.isArray(responseData)) {
        params.value = responseData
      } else {
        params.value = []
        console.warn('参数项数据不是数组:', responseData)
      }
    } else if (response.data) {
      if (Array.isArray(response.data.results)) {
        params.value = response.data.results
      } else if (Array.isArray(response.data)) {
        params.value = response.data
      } else {
        params.value = []
        console.warn('参数项数据不是数组:', response.data)
      }
    } else {
      params.value = []
    }
    
    // 确认结果是否为数组
    if (!Array.isArray(params.value)) {
      console.error('params.value不是数组，重置为空数组')
      params.value = []
    }
    
    console.log('处理后的参数项数据:', params.value)
    
    // 自动填充参数项
    const currentParams = { ...form.paramValues }
    form.paramValues = {}
    
    if (Array.isArray(params.value) && params.value.length > 0) {
      params.value.forEach(p => {
        // 保留已有的参数值
        form.paramValues[p.id] = currentParams[p.id] || ''
      })
    }
    
    autoFillProductCode()
  } catch (error) {
    console.error('获取参数项失败:', error)
    ElMessage.error('获取参数项失败')
    params.value = []
  }
}

// 表单提交
const saveProduct = async () => {
  if (!addFormRef.value) return
  
  await addFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    // 创建FormData对象来支持文件上传
    const formData = new FormData()
    formData.append('code', form.code)
    formData.append('name', form.name)
    formData.append('price', form.price.toString())
    formData.append('category', form.category!.toString())
    
    // 添加单位（如果选择了）
    if (form.unit) {
      formData.append('unit', form.unit.toString())
    }
    
    // 添加文件
    if (drawingAddFileList.value.length > 0 && drawingAddFileList.value[0].raw) {
      formData.append('drawing_pdf', drawingAddFileList.value[0].raw)
    }
    
    // 添加参数值
    const paramValues = []
    for (const paramId in form.paramValues) {
      if (form.paramValues[paramId]) {
        paramValues.push({
          param: parseInt(paramId),
          value: form.paramValues[paramId]
        })
      }
    }
    
    try {
      // 先创建产品
      const response = await api.post('/api/products/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      if (response.data) {
        // 保存成功，添加参数值
        const productId = response.data.id || response.data.data?.id
        
        if (productId && paramValues.length > 0) {
          for (const paramValue of paramValues) {
            await api.post('/api/product-param-values/', {
              product: productId,
              param: paramValue.param,
              value: paramValue.value
            })
          }
        }
        
        ElMessage.success('创建产品成功')
        showAddDialog.value = false
        fetchProducts()
      } else {
        ElMessage.error('创建产品失败')
      }
    } catch (error: any) {
      let errorMsg = '创建产品失败'
      
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
      console.error('创建产品失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const updateProduct = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    // 创建FormData对象来支持文件上传
    const formData = new FormData()
    formData.append('code', form.code)
    formData.append('name', form.name)
    formData.append('price', form.price.toString())
    formData.append('category', form.category!.toString())
    
    // 添加单位（如果选择了）
    if (form.unit) {
      formData.append('unit', form.unit.toString())
    }
    
    // 添加文件
    if (drawingEditFileList.value.length > 0 && drawingEditFileList.value[0].raw) {
      formData.append('drawing_pdf', drawingEditFileList.value[0].raw)
    }
    
    // 添加参数值
    const paramValues = []
    for (const paramId in form.paramValues) {
      if (form.paramValues[paramId]) {
        paramValues.push({
          param: parseInt(paramId),
          value: form.paramValues[paramId]
        })
      }
    }
    
    try {
      // 更新产品
      const response = await api.put(`/api/products/${form.id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      if (response.data) {
        // 保存成功，先清除原有参数值再添加新参数值
        const productId = form.id || response.data.id || response.data.data?.id
        
        if (productId) {
          // 获取现有参数值
          const paramValuesResponse = await api.get(`/api/product-param-values/`, {
            params: { product: productId }
          })
          
          // 删除现有参数值
          if (paramValuesResponse.data) {
            const existingParamValues = paramValuesResponse.data.results || paramValuesResponse.data
            if (Array.isArray(existingParamValues)) {
              for (const pv of existingParamValues) {
                await api.delete(`/api/product-param-values/${pv.id}/`)
              }
            }
          }
          
          // 添加新参数值
          if (paramValues.length > 0) {
            for (const paramValue of paramValues) {
              await api.post('/api/product-param-values/', {
                product: productId,
                param: paramValue.param,
                value: paramValue.value
              })
            }
          }
        }
        
        ElMessage.success('更新产品成功')
        showEditDialog.value = false
        fetchProducts()
      } else {
        ElMessage.error('更新产品失败')
      }
    } catch (error: any) {
      let errorMsg = '更新产品失败'
      
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
      console.error('更新产品失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

// 导入相关
function beforeImport(file: File) {
  const ext = file.name.split('.').pop()?.toLowerCase()
  
  if (!["xlsx", "xls", "csv"].includes(ext || '')) {
    ElMessage.error('仅支持Excel或CSV文件')
    return false
  }
  
  return true
}

async function handleImport(option: any) {
  submitting.value = true
  
  const formData = new FormData()
  formData.append('file', option.file)
  
  try {
    const response = await api.post('/api/products/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    ElMessage.success(response.data?.msg || '导入产品成功')
    fetchProducts()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.msg || '导入产品失败')
    console.error('导入产品失败:', error)
  } finally {
    submitting.value = false
  }
}

// 监听搜索值变化自动触发搜索
watch(search, () => {
  currentPage.value = 1
  fetchProducts()
})

// 生命周期钩子
onMounted(async () => {
  await fetchCategories()
  await fetchProducts()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

// 产品管理特有样式
.product-container {
  .no-file {
    color: var(--el-text-color-secondary);
  }
  
  .pdf-uploader {
    margin-bottom: 12px;
    
    .upload-tip {
      color: var(--el-text-color-secondary);
      font-size: 12px;
      margin-top: 8px;
    }
  }
  
  .current-file {
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .form-select {
    width: 400px;
  }
  
  .form-input {
    width: 400px;
  }
  
  .form-input-number {
    width: 180px;
  }

  .form-input-param {
    width: 200px;
  }
}
</style>
