<!-- filepath: h:\xmes\frontend\src\views\basedata\process/ProductProcessCodeList.vue -->
<template>
  <div class="product-process-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">产品工艺关联</h2>
          <div class="actions">
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon> 新增关联
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选区域 -->
      <div class="filter-container">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="产品">
            <el-select 
              v-model="searchParams.product" 
              placeholder="请选择产品" 
              filterable 
              clearable 
              @change="handleSearch"
              class="filter-select"
            >
              <el-option 
                v-for="product in products" 
                :key="product.id" 
                :label="`${product.name} (${product.code || ''})`" 
                :value="product.id" 
              />
            </el-select>
          </el-form-item>
          <el-form-item label="工艺流程代码">
            <el-select 
              v-model="searchParams.processCode" 
              placeholder="请选择工艺流程代码" 
              filterable 
              clearable 
              @change="handleSearch"
              class="filter-select"
            >
              <el-option 
                v-for="code in processCodes" 
                :key="code.id" 
                :label="`${code.code} (${code.version})`" 
                :value="code.id" 
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon> 搜索
            </el-button>
            <el-button @click="resetSearch">
              <el-icon><RefreshRight /></el-icon> 重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 数据表格 -->
      <el-table 
        :data="tableData" 
        border 
        stripe 
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="product_name" label="产品名称" min-width="150" />
        <el-table-column prop="product_code" label="产品编码" min-width="120" />
        <el-table-column prop="process_code" label="工艺流程代码" min-width="150" />
        <el-table-column prop="process_code_version" label="版本" width="80" />
        <el-table-column label="默认工艺" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="row.is_default ? 'success' : 'info'" 
              effect="plain"
            >
              {{ row.is_default ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="200" />
        <el-table-column label="操作" fixed="right" min-width="240">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                size="small" 
                type="primary" 
                @click="openEditDialog(row)"
              >
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="confirmDelete(row)"
              >
                <el-icon><Delete /></el-icon> 删除
              </el-button>
              <el-button 
                v-if="!row.is_default" 
                size="small" 
                type="success" 
                @click="setAsDefault(row)"
              >
                <el-icon><Check /></el-icon> 设为默认
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

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="form.id ? '编辑产品工艺关联' : '新增产品工艺关联'"
      width="600px"
      destroy-on-close
    >
      <el-form
        :model="form"
        :rules="formRules"
        ref="formRef"
        label-width="120px"
        label-position="left"
      >
        <el-form-item label="产品" prop="product">
          <el-select 
            v-model="form.product" 
            filterable 
            placeholder="请选择产品"
            class="form-select"
          >
            <el-option 
              v-for="product in products" 
              :key="product.id" 
              :label="`${product.name} (${product.code || ''})`" 
              :value="product.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="工艺流程代码" prop="process_code">
          <el-select 
            v-model="form.process_code" 
            filterable 
            placeholder="请选择工艺流程代码"
            class="form-select"
          >
            <el-option 
              v-for="code in processCodes" 
              :key="code.id" 
              :label="`${code.code} (${code.version})`" 
              :value="code.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="是否默认" prop="is_default">
          <el-switch v-model="form.is_default" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="form.remark" 
            type="textarea" 
            rows="3" 
            placeholder="请输入备注"
            class="form-select"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="saveForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete, Check, Search, RefreshRight } from '@element-plus/icons-vue'
import axios from 'axios'

// 类型定义
interface Product {
  id: number;
  name: string;
  code?: string;
}

interface ProcessCode {
  id: number;
  code: string;
  version: string;
}

interface ProductProcessCode {
  id?: number;
  product: number;
  product_name?: string;
  product_code?: string;
  process_code: number;
  process_code_text?: string;
  process_code_version?: string;
  is_default: boolean;
  remark?: string;
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const products = ref<Product[]>([])
const processCodes = ref<ProcessCode[]>([])
const tableData = ref<ProductProcessCode[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const formRef = ref<FormInstance>()

// 搜索参数
const searchParams = reactive({
  product: '',
  processCode: ''
})

// 表单对象
const form = reactive<ProductProcessCode>({
  product: 0,
  process_code: 0,
  is_default: false,
  remark: ''
})

// 表单校验规则
const formRules = {
  product: [
    { required: true, message: '请选择产品', trigger: 'change' }
  ],
  process_code: [
    { required: true, message: '请选择工艺流程代码', trigger: 'change' }
  ]
}

// 数据加载方法
async function fetchProductProcessCodes() {
  loading.value = true
  
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchParams.product) {
      params.product = searchParams.product
    }
    
    if (searchParams.processCode) {
      params.process_code = searchParams.processCode
    }
    
    const response = await axios.get('/api/product-process-codes/', { params })
    
    if (response.data.results) {
      tableData.value = response.data.results
      total.value = response.data.count
    } else {
      tableData.value = response.data
      total.value = response.data.length
    }
  } catch (error) {
    console.error('获取产品工艺关联失败:', error)
    ElMessage.error('获取产品工艺关联失败')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function fetchProducts() {
  try {
    const response = await axios.get('/api/products/')
    products.value = response.data.results || response.data
  } catch (error) {
    console.error('获取产品列表失败:', error)
    ElMessage.error('获取产品列表失败')
    products.value = []
  }
}

async function fetchProcessCodes() {
  try {
    const response = await axios.get('/api/process-codes/')
    processCodes.value = response.data.results || response.data
  } catch (error) {
    console.error('获取工艺流程代码列表失败:', error)
    ElMessage.error('获取工艺流程代码列表失败')
    processCodes.value = []
  }
}

// 处理事件
function handleSearch() {
  currentPage.value = 1
  fetchProductProcessCodes()
}

function resetSearch() {
  searchParams.product = ''
  searchParams.processCode = ''
  handleSearch()
}

function handleSizeChange(val: number) {
  pageSize.value = val
  currentPage.value = 1
  fetchProductProcessCodes()
}

function handleCurrentChange() {
  fetchProductProcessCodes()
}

// 表单操作
function openAddDialog() {
  Object.assign(form, {
    id: undefined,
    product: '',
    process_code: '',
    is_default: false,
    remark: ''
  })
  
  dialogVisible.value = true
}

function openEditDialog(row: ProductProcessCode) {
  Object.assign(form, row)
  dialogVisible.value = true
}

async function saveForm() {
  if (!formRef.value) return
  
  formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      if (form.id) {
        // 编辑模式
        await axios.put(`/api/product-process-codes/${form.id}/`, form)
        ElMessage.success('更新产品工艺关联成功')
      } else {
        // 新增模式
        await axios.post('/api/product-process-codes/', form)
        ElMessage.success('添加产品工艺关联成功')
      }
      
      dialogVisible.value = false
      fetchProductProcessCodes()
    } catch (error: any) {
      let errorMsg = '保存失败'
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMsg = error.response.data
        } else if (typeof error.response.data === 'object') {
          if (error.response.data.detail) {
            errorMsg = error.response.data.detail
          } else {
            const firstError = Object.values(error.response.data)[0]
            if (Array.isArray(firstError) && firstError.length > 0) {
              errorMsg = firstError[0] as string
            }
          }
        }
      }
      
      ElMessage.error(`保存失败: ${errorMsg}`)
      console.error('保存产品工艺关联失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

function confirmDelete(row: ProductProcessCode) {
  if (!row.id) return
  
  ElMessageBox.confirm(
    `确定要删除该产品工艺关联吗？此操作不可恢复。`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  ).then(() => {
    deleteItem(row.id as number)
  }).catch(() => {
    // 用户取消操作
  })
}

async function deleteItem(id: number) {
  loading.value = true
  
  try {
    await axios.delete(`/api/product-process-codes/${id}/`)
    ElMessage.success('删除产品工艺关联成功')
    fetchProductProcessCodes()
  } catch (error: any) {
    let errorMsg = '删除失败'
    
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (typeof error.response.data === 'object') {
        if (error.response.data.detail) {
          errorMsg = error.response.data.detail
        }
      }
    }
    
    ElMessage.error(`删除失败: ${errorMsg}`)
    console.error('删除产品工艺关联失败:', error)
  } finally {
    loading.value = false
  }
}

async function setAsDefault(row: ProductProcessCode) {
  if (!row.id) return
  
  loading.value = true
  
  try {
    await axios.post(`/api/product-process-codes/${row.id}/set-default/`)
    ElMessage.success('设置默认工艺成功')
    fetchProductProcessCodes()
  } catch (error: any) {
    let errorMsg = '设置默认工艺失败'
    
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (typeof error.response.data === 'object') {
        if (error.response.data.detail) {
          errorMsg = error.response.data.detail
        }
      }
    }
    
    ElMessage.error(`设置默认工艺失败: ${errorMsg}`)
    console.error('设置默认工艺失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchProducts()
  fetchProcessCodes()
  fetchProductProcessCodes()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.product-process-container {
  .filter-container {
    margin-bottom: 20px;
    padding: 15px;
    background-color: var(--el-fill-color-light);
    border-radius: 4px;
  }
  
  .filter-select {
    width: 240px;
  }
  
  .form-select {
    width: 100%;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>