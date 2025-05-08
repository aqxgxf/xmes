<template>
  <div class="bom-detail-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">BOM明细管理</h2>
          <div class="search-actions">
            <el-select
              v-model="searchBom"
              filterable
              clearable
              placeholder="筛选BOM"
              class="bom-filter"
              @change="handleBomFilterChange"
            >
              <el-option
                v-for="item in bomList"
                :key="item.id"
                :label="`${item.name} (v${item.version}) ${item.product_name}`"
                :value="item.id"
              />
            </el-select>
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon> 新增明细
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
        :data="list"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="bom_name" label="BOM" min-width="160" />
        <el-table-column prop="material_name" label="物料" min-width="120" />
        <el-table-column prop="quantity" label="用量" min-width="100" align="center" />
        <el-table-column prop="remark" label="备注" min-width="200" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" @click="openEditDialog(row)">
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
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
    
    <!-- BOM明细编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="closeDialog"
      destroy-on-close
    >
      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="120px"
        label-position="left"
        class="detail-form form-container"
      >
        <el-form-item label="BOM" prop="bom">
          <el-select
            v-model="form.bom"
            filterable
            placeholder="请选择BOM"
            class="product-select"
          >
            <el-option
              v-for="item in bomList"
              :key="item.id"
              :label="`${item.name} (v${item.version}) ${item.product_name}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="物料" prop="material">
          <el-select
            v-model="form.material"
            filterable
            placeholder="请选择物料"
            class="product-select"
          >
            <el-option
              v-for="item in materialList"
              :key="item.id"
              :label="`${item.name} (${item.code})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="用量" prop="quantity">
          <el-input-number
            v-model="form.quantity"
            :min="0"
            :step="1"
            class="form-input"
          />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            class="form-textarea"
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Upload } from '@element-plus/icons-vue'
import { api } from '../../../api/index'
import type { FormInstance } from 'element-plus'

// 类型定义
interface BomItem {
  id: number
  name: string
  version: string
  product_name: string
}

interface MaterialItem {
  id: number
  name: string
  code: string
}

interface BomDetailItem {
  id: number
  bom: number
  bom_name?: string
  material: number
  material_name?: string
  quantity: number
  remark?: string
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const list = ref<BomDetailItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchBom = ref<number | null>(null)
const dialogVisible = ref(false)
const dialogTitle = ref('新增BOM明细')

// 表单相关
const form = reactive({
  id: null as number | null,
  bom: null as number | null,
  material: null as number | null,
  quantity: 1,
  remark: ''
})

const formRef = ref<FormInstance>()
const bomList = ref<BomItem[]>([])
const materialList = ref<MaterialItem[]>([])

const rules = {
  bom: [{ required: true, message: '请选择BOM', trigger: 'change' }],
  material: [{ required: true, message: '请选择物料', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入用量', trigger: 'blur' }]
}

// 数据加载方法
function fetchBomList() {
  api.get('/api/boms/', { 
    params: { 
      page_size: 1000 
    } 
  })
  .then(response => {
    if (response.data && response.data.success === true) {
      // 处理API封装格式
      const responseData = response.data.data || {}
      if (responseData && Array.isArray(responseData.results)) {
        bomList.value = responseData.results
      } else if (responseData && Array.isArray(responseData)) {
        bomList.value = responseData
      } else {
        bomList.value = []
        console.warn('未识别的BOM数据格式:', responseData)
      }
    } else if (response.data) {
      // 直接处理返回数据
      if (Array.isArray(response.data.results)) {
        bomList.value = response.data.results
      } else if (Array.isArray(response.data)) {
        bomList.value = response.data
      } else {
        bomList.value = []
        console.warn('未识别的BOM数据格式:', response.data)
      }
    } else {
      bomList.value = []
    }
  })
  .catch(error => {
    bomList.value = [] // 确保在错误时设置为空数组
    console.error('获取BOM列表失败:', error)
    ElMessage.error('获取BOM列表失败')
  })
}

function fetchMaterialList() {
  api.get('/api/products/', { 
    params: { 
      page_size: 1000 
    } 
  })
  .then(response => {
    if (response.data && response.data.success === true) {
      // 处理API封装格式
      const responseData = response.data.data || {}
      if (responseData && Array.isArray(responseData.results)) {
        materialList.value = responseData.results
      } else if (responseData && Array.isArray(responseData)) {
        materialList.value = responseData
      } else {
        materialList.value = []
        console.warn('未识别的物料数据格式:', responseData)
      }
    } else if (response.data) {
      // 直接处理返回数据
      if (Array.isArray(response.data.results)) {
        materialList.value = response.data.results
      } else if (Array.isArray(response.data)) {
        materialList.value = response.data
      } else {
        materialList.value = []
        console.warn('未识别的物料数据格式:', response.data)
      }
    } else {
      materialList.value = []
    }
  })
  .catch(error => {
    materialList.value = [] // 确保在错误时设置为空数组
    console.error('获取物料列表失败:', error)
    ElMessage.error('获取物料列表失败')
  })
}

function fetchData() {
  loading.value = true
  const params: any = {
    page: currentPage.value,
    page_size: pageSize.value
  }
  
  if (searchBom.value) {
    params.bom = searchBom.value
  }
  
  api.get('/api/bom-items/', { params })
    .then(response => {
      if (response.data && response.data.success === true) {
        // 处理API封装格式
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
          console.warn('未识别的BOM明细数据格式:', responseData)
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
          list.value = []
          total.value = 0
          console.warn('未识别的BOM明细数据格式:', response.data)
        }
      } else {
        list.value = []
        total.value = 0
      }
    })
    .catch(error => {
      list.value = [] // 确保在错误时设置为空数组
      total.value = 0
      console.error('获取BOM明细列表失败:', error)
      ElMessage.error('获取BOM明细列表失败')
    })
    .finally(() => { 
      loading.value = false 
    })
}

// 处理事件
function handleBomFilterChange() {
  currentPage.value = 1
  fetchData()
}

function handlePageChange(val: number) {
  currentPage.value = val
  fetchData()
}

function handleSizeChange(val: number) {
  pageSize.value = val
  currentPage.value = 1
  fetchData()
}

function openAddDialog() {
  dialogTitle.value = '新增BOM明细'
  Object.assign(form, { 
    id: null, 
    bom: searchBom.value || null, 
    material: null, 
    quantity: 1, 
    remark: '' 
  })
  dialogVisible.value = true
  
  // 等待DOM更新后重置表单验证状态
  setTimeout(() => {
    formRef.value?.clearValidate()
  }, 100)
}

function openEditDialog(row: BomDetailItem) {
  dialogTitle.value = '编辑BOM明细'
  
  // 处理ID可能是字符串的情况
  const bomId = typeof row.bom === 'string' ? Number(row.bom) : row.bom
  const materialId = typeof row.material === 'string' ? Number(row.material) : row.material
  
  Object.assign(form, { 
    ...row,
    id: row.id,
    bom: bomId,
    material: materialId
  })
  
  dialogVisible.value = true
  
  // 等待DOM更新后重置表单验证状态
  setTimeout(() => {
    formRef.value?.clearValidate()
  }, 100)
}

function closeDialog() {
  dialogVisible.value = false
  form.id = null
  form.bom = searchBom.value || null
  form.material = null
  form.quantity = 1
  form.remark = ''
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

function submit() {
  if (!formRef.value) return
  
  formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    if (!form.bom) {
      ElMessage.error('请选择BOM')
      return
    }
    
    const data = {
      bom: form.bom,
      material: form.material,
      quantity: form.quantity,
      remark: form.remark
    }
    
    submitting.value = true
    
    try {
      if (form.id) {
        await api.put(`/api/bom-items/${form.id}/`, data)
        ElMessage.success('修改成功')
      } else {
        await api.post('/api/bom-items/', data)
        ElMessage.success('新增成功')
      }
      
      dialogVisible.value = false
      closeDialog()
      fetchData()
    } catch (error: any) {
      let errorMessage = '保存失败'
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          const match = error.response.data.match(/IntegrityError.*?at.*?\n(.*?)(?:\n|$)/)
          if (match) {
            errorMessage = match[1].trim()
          } else {
            errorMessage = '服务器内部错误，请稍后重试'
          }
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail
        } else if (error.response.data.material) {
          errorMessage = error.response.data.material[0]
        } else if (error.response.data.bom) {
          errorMessage = error.response.data.bom[0]
        } else if (error.response.data.quantity) {
          errorMessage = error.response.data.quantity[0]
        }
      }
      
      ElMessage.error(errorMessage)
    } finally {
      submitting.value = false
    }
  })
}

function remove(row: BomDetailItem) {
  ElMessageBox.confirm(
    '确定要删除该BOM明细吗？此操作不可撤销。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    loading.value = true
    try {
      await api.delete(`/api/bom-items/${row.id}/`)
      ElMessage.success('删除成功')
      
      // 如果当前页删除后没有数据了，尝试跳到上一页
      if (list.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }
      
      fetchData()
    } catch (error) {
      ElMessage.error('删除失败')
      console.error('删除BOM明细失败:', error)
    } finally {
      loading.value = false
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 导入相关
function beforeImport(file: File) {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!["xlsx", "xls", "csv"].includes(ext!)) {
    ElMessage.error('仅支持Excel或CSV文件')
    return false
  }
  return true
}

async function handleImport(option: any) {
  loading.value = true
  const formData = new FormData()
  formData.append('file', option.file)
  
  try {
    const response = await api.post('/api/bom-items/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success(response.data?.msg || '导入成功')
    fetchData()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.msg || '导入失败')
    console.error('导入失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchBomList()
  fetchMaterialList()
  fetchData()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

// Additional component specific styles
.bom-detail-container {
  // Ensure dropdowns are properly sized
  :deep(.product-select) {
    width: 100%;
    min-width: 300px;
  }
  
  // Filter dropdown in header
  .bom-filter {
    width: 320px;
  }
}
</style>
