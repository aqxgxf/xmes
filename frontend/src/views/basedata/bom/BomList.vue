<template>
  <div class="bom-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">BOM管理</h2>
          <div class="search-actions">
            <el-input
              v-model="search"
              placeholder="搜索BOM名称/产品/版本"
              clearable
              prefix-icon="Search"
              @input="handleSearch"
            />
            <el-button type="primary" @click="openDialog({})">
              <el-icon><Plus /></el-icon> 新增BOM
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
        <el-table-column prop="name" label="BOM名称" min-width="180" />
        <el-table-column prop="product_name" label="产品" min-width="160" />
        <el-table-column prop="version" label="版本" width="100" align="center" />
        <el-table-column prop="description" label="描述" min-width="180" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" @click="openDialog(row)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button size="small" type="danger" @click="remove(row)">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页控件 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="page"
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
    
    <!-- BOM编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="800px"
      destroy-on-close
    >
      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="100px"
        label-position="left"
        class="form-container"
      >
        <el-form-item label="产品" prop="product">
          <div class="product-select-container">
            <el-select
              v-model="form.product"
              placeholder="请选择产品"
              filterable
              class="product-select"
            >
              <el-option
                v-for="item in productList"
                :key="item.id"
                :label="`${item.name} (${item.code})`"
                :value="item.id"
              />
            </el-select>
            <el-button v-if="productList.length === 0" type="primary" size="small" @click="reloadProducts" :loading="loading">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="版本" prop="version">
          <el-select
            v-model="form.version"
            placeholder="请选择版本"
            class="version-select"
          >
            <el-option
              v-for="v in versionOptions"
              :key="v"
              :label="v"
              :value="v"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="BOM名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Refresh } from '@element-plus/icons-vue'
import { api } from '../../../api/index'
import type { FormInstance } from 'element-plus'

// 类型定义
interface BomItem {
  id: number
  name: string
  product: number
  product_name?: string
  version: string
  description?: string
  created_at?: string
  updated_at?: string
}

interface Product {
  id: number
  name: string
  code: string
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const list = ref<BomItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const search = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('新增BOM')
const versionOptions = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

// 表单相关
const form = reactive({
  id: null as number | null,
  product: null as number | null,
  name: '',
  version: '',
  description: ''
})

const rules = {
  product: [{ required: true, message: '请选择产品', trigger: 'change' }],
  name: [{ required: true, message: '请输入BOM名称', trigger: 'blur' }],
  version: [{ required: true, message: '请选择版本', trigger: 'change' }]
}

const formRef = ref<FormInstance>()
const productList = ref<Product[]>([])

// 数据加载方法
async function fetchProductList() {
  try {
    loading.value = true;
    const response = await api.get('/api/products/', { 
      params: { 
        page_size: 999 
      }
    });
    
    console.log('API Response:', response.data);
    
    // Pattern 1: Django REST direct (results + count format)
    if (response.data && response.data.results) {
      productList.value = response.data.results;
      console.log('Using Django REST format, found', productList.value.length, 'products');
    }
    // Pattern 2: API wrapper with success flag
    else if (response.data && response.data.success === true && response.data.data) {
      const apiData = response.data.data;
      if (Array.isArray(apiData.results)) {
        productList.value = apiData.results;
      } else if (Array.isArray(apiData)) {
        productList.value = apiData;
      }
      console.log('Using API success wrapper format, found', productList.value.length, 'products');
    }
    // Pattern 3: Direct array
    else if (Array.isArray(response.data)) {
      productList.value = response.data;
      console.log('Using direct array format, found', productList.value.length, 'products');
    }
    // Fallback
    else {
      console.warn('Unexpected API response format:', response.data);
      productList.value = [];
    }
    
    // 确保productList是数组
    if (!Array.isArray(productList.value)) {
      console.warn('设置为空数组因为产品列表不是数组:', productList.value);
      productList.value = [];
    }
  } catch (error) {
    console.error('获取产品列表失败:', error);
    ElMessage.error('获取产品列表失败');
    productList.value = [];
  } finally {
    loading.value = false;
  }
}

function fetchData() {
  loading.value = true
  api.get('/api/boms/', {
    params: {
      page: page.value,
      page_size: pageSize.value,
      search: search.value
    }
  }).then(response => {
    if (response.data && response.data.success === true) {
      // 处理API返回的封装格式
      const responseData = response.data.data || {}
      
      // 确保list始终是数组
      if (responseData && Array.isArray(responseData.results)) {
        list.value = responseData.results
        total.value = responseData.count || 0
      } else if (responseData && Array.isArray(responseData)) {
        list.value = responseData
        total.value = responseData.length
      } else {
        // 如果数据格式异常，设置为空数组
        list.value = []
        total.value = 0
        console.warn('未识别的数据格式:', responseData)
      }
    } else if (response.data) {
      // 直接处理返回数据
      if (Array.isArray(response.data.results)) {
        list.value = response.data.results
        total.value = response.data.count || 0
      } else if (Array.isArray(response.data)) {
        list.value = response.data
        total.value = response.data.length
      } else {
        // 如果数据格式异常，设置为空数组
        list.value = []
        total.value = 0
        console.warn('未识别的数据格式:', response.data)
      }
    } else {
      list.value = []
      total.value = 0
    }
  }).catch(error => {
    list.value = [] // 确保在错误时也设置为空数组
    total.value = 0
    console.error('获取BOM列表失败:', error)
    ElMessage.error('获取BOM列表失败')
  }).finally(() => {
    loading.value = false
  })
}

// 自动生成BOM名称和描述
function updateNameByProductAndVersion() {
  if (!Array.isArray(productList.value)) {
    console.warn('productList is not an array', productList.value);
    return;
  }
  
  const product = productList.value.find(p => p.id === form.product)
  if (product && form.version) {
    form.name = `${product.code}-${form.version}`
    
    // 只有当描述为空时才自动生成
    if (!form.description || form.description === '') {
      form.description = `${product.code}-${product.name}-${form.version}`
    }
  }
}

// 监听产品和版本变化，自动生成名称和描述
watch(() => [form.product, form.version], updateNameByProductAndVersion)

// 处理事件
function handleSearch() {
  page.value = 1
  fetchData()
}

function handleSizeChange(val: number) {
  pageSize.value = val
  page.value = 1
  fetchData()
}

function handleCurrentChange() {
  fetchData()
}

async function openDialog(row?: Partial<BomItem>) {
  // 确保产品列表已加载
  if (productList.value.length === 0) {
    loading.value = true;
    await fetchProductList();
    loading.value = false;
  }
  
  console.log('Opening dialog with products:', productList.value.length, 'items');
  
  // 如果仍然没有产品数据，显示提示并中止
  if (productList.value.length === 0) {
    ElMessage.warning('无法加载产品列表，请刷新页面重试');
    return;
  }
  
  // 重置表单
  Object.assign(form, {
    id: null,
    product: null,
    name: '',
    version: '',
    description: ''
  })
  
  // 编辑模式
  if (row && row.id) {
    dialogTitle.value = '编辑BOM'
    
    // 处理产品ID可能是字符串的情况
    let productId = row.product
    if (typeof productId === 'string') {
      productId = Number(productId)
    }
    
    Object.assign(form, {
      ...row,
      id: row.id,
      product: productId
    })
  } else {
    dialogTitle.value = '新增BOM'
  }
  
  dialogVisible.value = true
  // 等待DOM更新后重置表单验证状态
  setTimeout(() => {
    formRef.value?.clearValidate()
  }, 100)
}

function submit() {
  if (!formRef.value) return
  
  formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    const isEdit = !!form.id
    const data = {
      product: form.product,
      name: form.name,
      version: form.version,
      description: form.description
    }
    
    submitting.value = true
    
    try {
      if (isEdit) {
        await api.patch(`/api/boms/${form.id}/`, data)
        ElMessage.success('修改成功')
      } else {
        await api.post('/api/boms/', data)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch (error: any) {
      let errorMsg = '保存失败'
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMsg = error.response.data
        } else if (typeof error.response.data === 'object') {
          const firstError = Object.values(error.response.data)[0]
          if (Array.isArray(firstError) && firstError.length > 0) {
            errorMsg = firstError[0]
          } else if (typeof firstError === 'string') {
            errorMsg = firstError
          }
        }
      }
      ElMessage.error(errorMsg)
    } finally {
      submitting.value = false
    }
  })
}

function remove(row: BomItem) {
  ElMessageBox.confirm(
    `确定要删除BOM "${row.name}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    loading.value = true
    try {
      await api.delete(`/api/boms/${row.id}/`)
      ElMessage.success('删除成功')
      
      // 如果当前页删除后没有数据了，尝试跳到上一页
      if (list.value.length === 1 && page.value > 1) {
        page.value--
      }
      
      fetchData()
    } catch (error) {
      ElMessage.error('删除失败')
      console.error('删除BOM失败:', error)
    } finally {
      loading.value = false
    }
  }).catch(() => {
    // 用户取消操作
  })
}

function reloadProducts() {
  fetchProductList()
}

// 生命周期钩子
onMounted(() => {
  fetchData()
  fetchProductList()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

// Additional component specific styles
.bom-container {
  // Ensure the product-select gets proper width in dialog
  :deep(.product-select) {
    width: 100%; 
    min-width: 560px;
  }
  
  // Version select remains narrow
  :deep(.version-select) {
    width: 120px;
  }
}
</style>
