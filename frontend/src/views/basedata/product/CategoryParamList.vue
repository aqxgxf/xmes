<template>
  <div class="param-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">参数项管理</h2>
          <div class="search-actions">
            <el-input
              v-model="search"
              placeholder="搜索参数项名称"
              clearable
              prefix-icon="Search"
              @input="handleSearch"
            />
            <el-button type="primary" @click="openAddDialog" :disabled="!selectedCategory">
              <el-icon><Plus /></el-icon> 新增参数项
            </el-button>
          </div>
        </div>
      </template>

      <!-- 分类筛选区域 -->
      <div class="filter-container">
        <el-form inline>
          <el-form-item label="产品类">
            <el-select
              v-model="selectedCategory"
              placeholder="请选择产品类"
              filterable
              clearable
              class="category-select"
              @change="fetchParams"
            >
              <el-option
                v-for="cat in categories"
                :key="cat.id"
                :label="cat.display_name + ' (' + cat.code + ')'"
                :value="cat.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 数据表格 -->
      <el-table
        :data="filteredParams"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="参数项名称" min-width="180" />
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
    
    <!-- 添加参数项对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="新增参数项"
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
        <el-form-item label="参数项名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入参数项名称"
            maxlength="50"
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
          @click="saveParam"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑参数项对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑参数项"
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
        <el-form-item label="参数项名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入参数项名称"
            maxlength="50"
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
          @click="updateParam"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { api } from '../../../api/index'
import apiService from '../../../api/index'

// 类型定义
interface CategoryParam {
  id: number;
  name: string;
  category: number;
}

interface Category {
  id: number;
  code: string;
  display_name: string;
  company: number;
}

interface ParamForm {
  id: number | null;
  name: string;
  category: number | null;
}

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入参数项名称', trigger: 'blur' },
    { max: 50, message: '最大长度不能超过50个字符', trigger: 'blur' }
  ]
}

// 状态定义
const loading = ref(false)
const submitting = ref(false)
const categories = ref<Category[]>([])
const params = ref<CategoryParam[]>([])
const selectedCategory = ref<number | null>(null)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const search = ref('')

// 表单对象
const form = reactive<ParamForm>({
  id: null,
  name: '',
  category: null
})

// 计算属性
const filteredParams = computed(() => {
  if (!search.value) return params.value
  
  return params.value.filter(p => 
    p.name.toLowerCase().includes(search.value.toLowerCase())
  )
})

// 数据加载方法
const fetchCategories = async () => {
  loading.value = true
  
  try {
    // 使用API索引中预定义的方法获取产品类别
    const response = await apiService.basedata.getProductCategories({ page_size: 999 })
    
    console.log('产品类别原始响应:', response.data) // 添加日志，查看原始响应
    
    // 使用统一的数据处理逻辑
    if (response.data && response.data.success === true) {
      const responseData = response.data.data || {}
      
      if (responseData && Array.isArray(responseData.results)) {
        categories.value = responseData.results
      } else if (responseData && Array.isArray(responseData)) {
        categories.value = responseData
      } else {
        categories.value = []
      }
    } else if (response.data) {
      if (Array.isArray(response.data.results)) {
        categories.value = response.data.results
      } else if (Array.isArray(response.data)) {
        categories.value = response.data
      } else {
        categories.value = []
      }
    } else {
      categories.value = []
    }
    
    console.log('处理后的产品类别数据:', categories.value) // 添加日志，查看处理后数据
    
    // 自动选中第一个产品类并加载参数项
    if (categories.value && categories.value.length > 0) {
      if (!selectedCategory.value) {
        selectedCategory.value = categories.value[0].id
        await fetchParams()
      }
    } else {
      params.value = []
      total.value = 0
      ElMessage.warning('没有可用的产品类，请先创建产品类')
    }
  } catch (error) {
    console.error('获取产品类别失败:', error)
    ElMessage.error('获取产品类别失败')
    categories.value = []
  } finally {
    loading.value = false
  }
}

const fetchParams = async () => {
  if (!selectedCategory.value) {
    params.value = []
    total.value = 0
    return
  }
  
  loading.value = true
  
  try {
    const reqParams = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // 确保在使用 selectedCategory.value 构建 URL 前已经检查了它是否为 null
    const categoryId = selectedCategory.value
    if (!categoryId) {
      params.value = []
      total.value = 0
      loading.value = false
      return
    }
    
    // 直接获取API响应，因为没有预定义的API方法
    const response = await api.get(`/api/product-categories/${categoryId}/params/`, { params: reqParams })
    
    console.log(`产品类别${categoryId}的参数项原始响应:`, response.data) // 添加日志
    
    // 使用统一的数据处理逻辑，与fetchCategories保持一致
    if (response.data && response.data.success === true) {
      const responseData = response.data.data || {}
      
      if (responseData && Array.isArray(responseData.results)) {
        params.value = responseData.results
        total.value = responseData.count || 0
      } else if (responseData && Array.isArray(responseData)) {
        params.value = responseData
        total.value = responseData.length
      } else {
        params.value = []
        total.value = 0
      }
    } else if (response.data) {
      if (Array.isArray(response.data.results)) {
        params.value = response.data.results
        total.value = response.data.count || 0
      } else if (Array.isArray(response.data)) {
        params.value = response.data
        total.value = response.data.length
      } else {
        params.value = []
        total.value = 0
      }
    } else {
      params.value = []
      total.value = 0
    }
    
    console.log('处理后的参数项数据:', params.value) // 添加日志
  } catch (error: any) {
    params.value = []
    total.value = 0
    console.error(`获取产品类别${selectedCategory.value}的参数项失败:`, error)
    
    // 更详细的错误信息
    if (error.response?.status === 404) {
      ElMessage.error(`产品类别ID ${selectedCategory.value} 不存在`)
    } else {
      ElMessage.error(`获取参数项列表失败: ${error.message || '未知错误'}`)
    }
  } finally {
    loading.value = false
  }
}

// 处理事件
const handleSearch = () => {
  // 本地筛选，不需要重新加载
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchParams()
}

const handleCurrentChange = () => {
  fetchParams()
}

const confirmDelete = (row: CategoryParam) => {
  ElMessageBox.confirm(
    `确定要删除参数项 "${row.name}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteParam(row.id)
  }).catch(() => {
    // 用户取消操作
  })
}

// 对话框处理
const openAddDialog = () => {
  if (!selectedCategory.value) {
    ElMessage.warning('请先选择产品类')
    return
  }
  
  resetForm()
  form.category = selectedCategory.value
  showAddDialog.value = true
}

const openEditDialog = (row: CategoryParam) => {
  resetForm()
  
  form.id = row.id
  form.name = row.name
  form.category = row.category
  
  showEditDialog.value = true
}

const closeAddDialog = () => {
  showAddDialog.value = false
  resetForm()
}

const closeEditDialog = () => {
  showEditDialog.value = false
  resetForm()
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.category = selectedCategory.value || null
}

// 表单提交
const saveParam = async () => {
  if (!addFormRef.value) return
  
  addFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    // 确保有选中的产品类
    if (!form.category) {
      ElMessage.error('请先选择产品类')
      return
    }
    
    // 验证参数项名称是否重复
    if (params.value.some(p => p.name === form.name)) {
      ElMessage.error('该产品类下参数项名称已存在！')
      return
    }
    
    submitting.value = true
    
    try {
      await api.post('/api/category-params/', {
        name: form.name,
        category: form.category
      })
      
      ElMessage.success('新增参数项成功')
      closeAddDialog()
      fetchParams()
    } catch (error: any) {
      let errorMsg = '新增参数项失败'
      
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
      console.error('新增参数项失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const updateParam = async () => {
  if (!editFormRef.value) return
  
  editFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    // 确保有选中的产品类
    if (!form.category) {
      ElMessage.error('请先选择产品类')
      return
    }
    
    // 验证参数项名称是否重复（排除自身）
    if (params.value.some(p => p.name === form.name && p.id !== form.id)) {
      ElMessage.error('该产品类下参数项名称已存在！')
      return
    }
    
    submitting.value = true
    
    try {
      await api.put(`/api/category-params/${form.id}/`, {
        name: form.name,
        category: form.category
      })
      
      ElMessage.success('更新参数项成功')
      closeEditDialog()
      fetchParams()
    } catch (error: any) {
      let errorMsg = '更新参数项失败'
      
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
      console.error('更新参数项失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteParam = async (id: number) => {
  loading.value = true
  
  try {
    await api.delete(`/api/category-params/${id}/`)
    ElMessage.success('删除参数项成功')
    
    // 如果当前页删除后没有数据了，尝试跳到上一页
    if (params.value.length === 1 && currentPage.value > 1) {
      currentPage.value--
    }
    
    fetchParams()
  } catch (error) {
    ElMessage.error('删除参数项失败')
    console.error('删除参数项失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  fetchCategories()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

// 参数项管理特有样式
.param-container {
  .filter-container {
    margin-bottom: 16px;
    text-align: left;
  }
  
  .category-select {
    width: 320px;
  }
}
</style>
