<template>
  <div class="param-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">参数项管理</h2>
          <div class="search-actions">
            <el-input
              v-model="searchText"
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
              @change="handleCategoryChange"
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
import { ref, reactive, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import api from '../../../api/index'
import { useCategoryStore } from '../../../stores/category'
import { useParamStore, type CategoryParam, type ParamForm } from '../../../stores/param'

// 使用Pinia Store
const categoryStore = useCategoryStore()
const paramStore = useParamStore()

// 获取参数Store状态 - 使用storeToRefs保持响应式
const { 
  params, 
  filteredParams, 
  total, 
  loading, 
  currentPage, 
  pageSize, 
  selectedCategory 
} = storeToRefs(paramStore)

// 本地状态
const searchText = ref('')
const categories = ref<any[]>([])
const submitting = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入参数项名称', trigger: 'blur' },
    { max: 50, message: '最大长度不能超过50个字符', trigger: 'blur' }
  ]
}

// 表单对象
const form = reactive<ParamForm>({
  id: null,
  name: '',
  category: null
})

// 数据加载方法
const fetchCategories = async () => {
  try {
    // 使用api直接获取产品类别，修复URL重复的api前缀
    const response = await api.get('/product-categories/', { 
      params: { page_size: 999 } 
    })
    
    // 处理响应数据
    if (response.data && response.data.results) {
      categories.value = response.data.results
    } else if (Array.isArray(response.data)) {
      categories.value = response.data
    } else {
      categories.value = []
    }
    
    // 自动选中第一个产品类并加载参数项
    if (categories.value && categories.value.length > 0 && !selectedCategory.value) {
      paramStore.setCategory(categories.value[0].id)
    }
  } catch (error) {
    console.error('获取产品类别失败:', error)
    ElMessage.error('获取产品类别失败')
    categories.value = []
  }
}

// 处理事件
const handleSearch = () => {
  paramStore.setSearch(searchText.value)
}

const handleCategoryChange = (value: number | null) => {
  paramStore.setCategory(value)
}

const handleSizeChange = (val: number) => {
  paramStore.setPageSize(val)
}

const handleCurrentChange = (val: number) => {
  paramStore.setPage(val)
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
  form.category = selectedCategory.value ?? null
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
    if (params.value && params.value.some((p: CategoryParam) => p.name === form.name)) {
      ElMessage.error('该产品类下参数项名称已存在！')
      return
    }
    
    submitting.value = true
    
    try {
      const result = await paramStore.createParam(form)
      
      if (result.success) {
        ElMessage.success('新增参数项成功')
        closeAddDialog()
      } else {
        let errorMsg = '新增参数项失败'
        
        if (typeof result.error === 'object') {
          errorMsg = Object.values(result.error).join('; ')
        } else if (result.error) {
          errorMsg = result.error as string
        }
        
        ElMessage.error(errorMsg)
      }
    } catch (error) {
      ElMessage.error('新增参数项失败')
      console.error('新增参数项失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const updateParam = async () => {
  if (!editFormRef.value || form.id === null) return
  
  editFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    // 确保有选中的产品类
    if (!form.category) {
      ElMessage.error('请先选择产品类')
      return
    }
    
    // 验证参数项名称是否重复（排除自身）
    if (params.value && params.value.some((p: CategoryParam) => p.name === form.name && p.id !== form.id)) {
      ElMessage.error('该产品类下参数项名称已存在！')
      return
    }
    
    submitting.value = true
    
    try {
      // Ensure form.id is not null when we call updateParam
      const result = await paramStore.updateParam(form.id as number, form)
      
      if (result.success) {
        ElMessage.success('更新参数项成功')
        closeEditDialog()
      } else {
        let errorMsg = '更新参数项失败'
        
        if (typeof result.error === 'object') {
          errorMsg = Object.values(result.error).join('; ')
        } else if (result.error) {
          errorMsg = result.error as string
        }
        
        ElMessage.error(errorMsg)
      }
    } catch (error) {
      ElMessage.error('更新参数项失败')
      console.error('更新参数项失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteParam = async (id: number) => {
  try {
    const result = await paramStore.deleteParam(id)
    
    if (result.success) {
      ElMessage.success('删除参数项成功')
    } else {
      ElMessage.error(result.error || '删除参数项失败')
    }
  } catch (error) {
    ElMessage.error('删除参数项失败')
    console.error('删除参数项失败:', error)
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

