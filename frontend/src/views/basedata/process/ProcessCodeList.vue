<template>
  <div class="process-code-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工艺流程代码管理</h2>
          <div class="search-actions">
            <el-input
              v-model="search"
              placeholder="搜索代码/说明/版本"
              clearable
              prefix-icon="Search"
              @input="handleSearch"
            />
            <el-button type="primary" @click="openDialog(null)">
              <el-icon><Plus /></el-icon> 新增工艺流程代码
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 数据表格 -->
      <el-table
        :data="list"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="code" label="工艺流程代码" min-width="180" />
        <el-table-column prop="description" label="说明" min-width="200" />
        <el-table-column prop="version" label="版本" min-width="80" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column prop="updated_at" label="更新时间" min-width="160" />
        <el-table-column label="工艺PDF" width="120" align="center">
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
              <el-button size="small" type="primary" @click="openDialog(row)">
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
    
    <!-- 编辑/新增对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      destroy-on-close
      @close="closeDialog"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="left"
        class="form-container"
      >
        <el-form-item label="产品" prop="product">
          <el-select
            v-model="form.product"
            placeholder="请选择产品"
            filterable
            class="form-select"
          >
            <el-option
              v-for="item in productList"
              :key="item.id"
              :label="item.name + '（' + item.code + '）'"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="说明" prop="description">
          <el-input
            v-model="form.description"
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="版本" prop="version">
          <el-select
            v-model="form.version"
            placeholder="请选择版本"
            class="form-select"
          >
            <el-option
              v-for="v in ['A','B','C','D','E','F','G']"
              :key="v"
              :label="v"
              :value="v"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="工艺流程代码" prop="code">
          <el-input
            v-model="form.code"
            class="form-input"
          />
        </el-form-item>
        
        <el-form-item label="工艺PDF">
          <div v-if="form.process_pdf && !pdfFileList.length" class="current-file">
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
            v-model:file-list="pdfFileList"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="upload-tip">仅支持PDF格式文件</div>
            </template>
          </el-upload>
          
          <pdf-preview
            v-if="pdfFileList.length > 0"
            :file="pdfFileList[0].raw"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="submit"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type UploadUserFile } from 'element-plus'
import { Plus, Edit, Delete, Search, Document } from '@element-plus/icons-vue'
import { api } from '../../../api/index'
import PdfPreview from '../../../components/common/PdfPreview.vue'

// 类型定义
interface ProcessCode {
  id: number;
  code: string;
  description: string;
  version: string;
  process_pdf?: string;
  product?: number | null;
  created_at?: string;
  updated_at?: string;
}

interface Product {
  id: number;
  code: string;
  name: string;
}

interface ProcessCodeForm {
  id: number | null;
  code: string;
  description: string;
  version: string;
  process_pdf?: string;
  product: number | null;
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const list = ref<ProcessCode[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const search = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('新增工艺流程代码')
const formRef = ref<FormInstance>()
const pdfFileList = ref<UploadUserFile[]>([])
const productList = ref<Product[]>([])

// 表单对象
const form = reactive<ProcessCodeForm>({
  id: null,
  code: '',
  description: '',
  version: '',
  process_pdf: '',
  product: null
})

// 表单验证规则
const rules = {
  code: [
    { required: true, message: '请输入工艺流程代码', trigger: 'blur' },
    { max: 50, message: '最大长度不能超过50个字符', trigger: 'blur' }
  ],
  version: [
    { required: true, message: '请选择版本', trigger: 'change' }
  ],
  product: [
    { required: true, message: '请选择产品', trigger: 'change' }
  ]
}

// 监听产品和版本变化，自动生成code
watch(() => [form.product, form.version], updateCodeByProductAndVersion)

// 数据加载方法
const fetchData = async () => {
  loading.value = true
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: search.value
    }
    
    const response = await api.get('/api/process-codes/', { params })
    
    // 处理API返回数据
    if (response.data && response.data.success === true) {
      const responseData = response.data.data || {}
      
      if (responseData && Array.isArray(responseData.results)) {
        list.value = responseData.results
        total.value = responseData.count || 0
      } else if (responseData && Array.isArray(responseData)) {
        list.value = responseData
        total.value = responseData.length
      } else {
        list.value = []
        total.value = 0
      }
    } else if (response.data) {
      if (Array.isArray(response.data.results)) {
        list.value = response.data.results
        total.value = response.data.count || 0
      } else if (Array.isArray(response.data)) {
        list.value = response.data
        total.value = response.data.length
      } else {
        list.value = []
        total.value = 0
      }
    } else {
      list.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取工艺流程代码列表失败:', error)
    ElMessage.error('获取工艺流程代码列表失败')
    list.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const fetchProductList = async () => {
  try {
    const params = {
      page_size: 999
    }
    
    const response = await api.get('/api/products/', { params })
    
    // 处理API返回数据
    if (response.data && response.data.success === true) {
      const responseData = response.data.data || {}
      
      if (responseData && Array.isArray(responseData.results)) {
        productList.value = responseData.results
      } else if (responseData && Array.isArray(responseData)) {
        productList.value = responseData
      } else {
        productList.value = []
      }
    } else if (response.data) {
      if (Array.isArray(response.data.results)) {
        productList.value = response.data.results
      } else if (Array.isArray(response.data)) {
        productList.value = response.data
      } else {
        productList.value = []
      }
    } else {
      productList.value = []
    }
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
    productList.value = []
  }
}

function updateCodeByProductAndVersion() {
  const product = productList.value.find(p => p.id === form.product)
  if (product && form.version) {
    form.code = product.code + '-' + form.version
  } else {
    form.code = ''
  }
  if (form.description === '' && form.code !== '') {
    form.description = product?.code + '-' + product?.name + '-' + form.version
  }
}

// 处理事件
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchData()
}

const handleCurrentChange = () => {
  fetchData()
}

const confirmDelete = (row: ProcessCode) => {
  ElMessageBox.confirm(
    `确定要删除工艺流程代码 "${row.code}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteProcessCode(row.id)
  }).catch(() => {
    // 用户取消操作
  })
}

// 对话框处理
const openDialog = async (row: ProcessCode | null) => {
  resetForm()
  
  if (productList.value.length === 0) {
    await fetchProductList()
  }
  
  if (row) {
    // 编辑模式
    dialogTitle.value = '编辑工艺流程代码'
    
    // 兼容字符串和数字
    let foundRow = row
    
    // 处理el-table可能丢失字段的情况
    if (row.id && (row.product === undefined || row.product === null)) {
      const found = list.value.find(item => item.id === row.id)
      if (found) {
        foundRow = found
      }
    }
    
    form.id = foundRow.id
    form.code = foundRow.code
    form.description = foundRow.description
    form.version = foundRow.version
    form.process_pdf = foundRow.process_pdf
    
    if (foundRow.product) {
      form.product = typeof foundRow.product === 'string' ? Number(foundRow.product) : foundRow.product
    } else {
      form.product = null
    }
  } else {
    // 新增模式
    dialogTitle.value = '新增工艺流程代码'
  }
  
  pdfFileList.value = []
  
  // 可能需要手动触发一次更新，确保code正确生成
  updateCodeByProductAndVersion()
  
  dialogVisible.value = true
}

const closeDialog = () => {
  dialogVisible.value = false
  resetForm()
  pdfFileList.value = []
}

const resetForm = () => {
  form.id = null
  form.code = ''
  form.description = ''
  form.version = ''
  form.process_pdf = ''
  form.product = null
}

// 表单提交
const submit = async () => {
  if (!formRef.value) return
  
  formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      const formData = new FormData()
      formData.append('code', form.code)
      formData.append('description', form.description)
      formData.append('version', form.version)
      
      if (pdfFileList.value.length > 0 && pdfFileList.value[0].raw) {
        formData.append('process_pdf', pdfFileList.value[0].raw)
      }
      
      let processCodeId = form.id
      
      if (form.id) {
        // 编辑模式
        await api.patch(`/api/process-codes/${form.id}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        ElMessage.success('更新工艺流程代码成功')
      } else {
        // 新增模式
        const response = await api.post('/api/process-codes/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        // 获取新创建的记录ID
        if (response.data && response.data.id) {
          processCodeId = response.data.id
        } else if (response.data && response.data.data && response.data.data.id) {
          processCodeId = response.data.data.id
        }
        
        ElMessage.success('新增工艺流程代码成功')
      }
      
      // 保存产品-工艺流程代码关系
      if (form.product && processCodeId) {
        try {
          await api.post('/api/product-process-codes/', {
            product: form.product,
            process_code: processCodeId,
            is_default: true
          })
        } catch (error) {
          console.error('保存产品-工艺流程代码关系失败:', error)
        }
      }
      
      dialogVisible.value = false
      fetchData()
    } catch (error: any) {
      let errorMsg = '保存工艺流程代码失败'
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMsg = error.response.data
        } else if (typeof error.response.data === 'object') {
          // 尝试获取详细错误信息
          if (error.response.data.detail) {
            errorMsg = error.response.data.detail
          } else {
            // 尝试序列化所有错误信息
            try {
              errorMsg = JSON.stringify(error.response.data)
            } catch (e) {
              errorMsg = '请检查表单数据是否有误'
            }
          }
        }
      }
      
      ElMessage.error(errorMsg)
      console.error('保存工艺流程代码失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteProcessCode = async (id: number) => {
  loading.value = true
  
  try {
    await api.delete(`/api/process-codes/${id}/`)
    ElMessage.success('删除工艺流程代码成功')
    
    // 如果当前页删除后没有数据了，尝试跳到上一页
    if (list.value.length === 1 && currentPage.value > 1) {
      currentPage.value--
    }
    
    fetchData()
  } catch (error: any) {
    let errorMsg = '删除工艺流程代码失败'
    
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
    console.error('删除工艺流程代码失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchData()
  fetchProductList()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

// 工艺流程代码管理特有样式
.process-code-container {
  .form-select {
    width: 320px;
  }
  
  .form-input {
    width: 320px;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
  }
  
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
}
</style>

