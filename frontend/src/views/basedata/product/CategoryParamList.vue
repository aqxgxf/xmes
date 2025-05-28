<template>
  <div class="param-container page-container">
    <!-- 产品类筛选 -->
    <el-card class="filter-card">
      <el-form inline>
        <el-form-item label="产品类:">
          <el-select
            v-model="selectedCategory"
            placeholder="请选择产品类以查看其参数项"
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
    </el-card>

    <data-table
      :data="params"
      :loading="loading"
      :total="total"
      :initial-current-page="currentPage"
      :initial-page-size="pageSize"
      row-key="id"
      :show-actions="true"
      actions-label="操作"
      :actions-width="180"
      :show-search="true"
      search-placeholder="搜索参数项名称"
      @page-change="handleCurrentChange"
      @size-change="handleSizeChange"
      @search="handleSearch"
      :show-toolbar="true"
      empty-text="请先选择一个产品类，或当前产品类下无参数项"
    >
      <!-- Toolbar Actions Slot -->
      <template #actions>
        <el-button type="primary" @click="openAddDialog" :disabled="!selectedCategory">
          <el-icon><Plus /></el-icon> 新增参数项
        </el-button>
        <el-button 
          type="success" 
          @click="saveOrder" 
          :disabled="!orderChanged || !selectedCategory || params.length === 0"
          :loading="savingOrder"
        >
          <el-icon><Sort /></el-icon> 保存排序
        </el-button>
      </template>

      <!-- Columns Definition -->
      <el-table-column prop="name" label="参数项名称" min-width="180" />
      
      <el-table-column label="排序" width="100" align="center">
        <template #default="{ row, $index }">
          <el-button 
            size="small" 
            circle 
            :icon="ArrowUpBold" 
            @click="moveParamUp($index)" 
            :disabled="$index === 0" 
            style="margin-right: 5px;"
          />
          <el-button 
            size="small" 
            circle 
            :icon="ArrowDownBold" 
            @click="moveParamDown($index)" 
            :disabled="$index === params.length - 1" 
          />
        </template>
      </el-table-column>
      <!-- Removed static ID column as it's not usually displayed directly -->
      <!-- Removed category column as it's implied by the filter -->

      <!-- Row Actions Slot -->
      <template #row-actions="{ row }">
        <el-tooltip content="编辑" placement="top">
          <el-button size="small" type="primary" @click="openEditDialog(row)" :style="{padding: '0 6px'}">
            <el-icon><Edit /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="删除" placement="top">
          <el-button size="small" type="danger" @click="confirmDelete(row)" :style="{padding: '0 6px'}">
            <el-icon><Delete /></el-icon>
          </el-button>
        </el-tooltip>
      </template>
    </data-table>
    
    <!-- 添加参数项对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="'新增参数项到 ' + selectedCategoryName"
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
      :title="'编辑参数项 (属于 ' + selectedCategoryName + ')'"
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
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Edit, Delete, Sort, ArrowUpBold, ArrowDownBold } from '@element-plus/icons-vue'
import api from '../../../api/index'
import { useParamStore, type CategoryParam, type ParamForm } from '../../../stores/paramStore'
import DataTable from '../../../components/common/DataTable.vue'
import type { ProductCategory } from '../../../types/common'

const paramStore = useParamStore()

const { 
  params,
  total, 
  loading, 
  currentPage, 
  pageSize, 
  selectedCategory
} = storeToRefs(paramStore)

const searchText = ref('')
const categories = ref<ProductCategory[]>([])
const submitting = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

const orderChanged = ref(false)
const savingOrder = ref(false)

const rules = {
  name: [
    { required: true, message: '请输入参数项名称', trigger: 'blur' },
    { max: 50, message: '最大长度不能超过50个字符', trigger: 'blur' }
  ]
}

const form = reactive<ParamForm>({
  id: null,
  name: '',
  category: null
})

const selectedCategoryName = computed(() => {
  const foundCategory = categories.value.find(cat => cat.id === selectedCategory.value)
  return foundCategory ? foundCategory.display_name : '未知产品类'
})

const fetchCategories = async () => {
  try {
    const response = await api.get('/product-categories/', { 
      params: { page_size: 999, ordering: 'code' }
    })
    
    if (response.data && response.data.results) {
      categories.value = response.data.results
    } else if (Array.isArray(response.data)) {
      categories.value = response.data
    } else {
      categories.value = []
    }
  } catch (error) {
    console.error('获取产品类别失败:', error)
    ElMessage.error('获取产品类别失败')
    categories.value = []
  }
}

const handleSearch = (query: string) => {
  paramStore.setSearch(query)
}

const handleCategoryChange = (value: number | null) => {
  console.log('[CategoryParamList.vue] handleCategoryChange called with new category ID:', value);
  paramStore.setCategory(value)
}

const handleSizeChange = (val: number) => {
  paramStore.setPageSize(val)
}

const handleCurrentChange = (val: number) => {
  paramStore.setPage(val)
}

const moveParamUp = (index: number) => {
  if (index > 0) {
    const item = params.value.splice(index, 1)[0];
    params.value.splice(index - 1, 0, item);
    orderChanged.value = true;
  }
};

const moveParamDown = (index: number) => {
  if (index < params.value.length - 1) {
    const item = params.value.splice(index, 1)[0];
    params.value.splice(index + 1, 0, item);
    orderChanged.value = true;
  }
};

const saveOrder = async () => {
  if (!selectedCategory.value) {
    ElMessage.error("没有选择产品类，无法保存排序。");
    return;
  }
  if (params.value.length === 0) {
    ElMessage.info("当前产品类下没有参数项可排序。");
    return;
  }

  savingOrder.value = true;
  const orderedParams = params.value.map((param, index) => ({
    id: param.id,
    display_order: index + 1,
  }));

  try {
    await paramStore.updateParamsOrder(selectedCategory.value, orderedParams);
    ElMessage.success("参数项排序已保存！");
    orderChanged.value = false;
  } catch (error: any) {
    ElMessage.error(error.message || "保存排序失败，请重试。");
  } finally {
    savingOrder.value = false;
  }
};

const confirmDelete = (row: CategoryParam) => {
  ElMessageBox.confirm(
    `确定要删除参数项 "${row.name}" (属于 ${selectedCategoryName.value}) 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    if (row.id !== null) {
      deleteParam(row.id)
    } else {
      ElMessage.error('无法删除，参数项ID未知')
    }
  }).catch(() => {
    // 用户取消操作
  })
}

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
}

const closeEditDialog = () => {
  showEditDialog.value = false
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.category = selectedCategory.value ?? null
  orderChanged.value = false;
  if (addFormRef.value) addFormRef.value.resetFields()
  if (editFormRef.value) editFormRef.value.resetFields()
}

const saveParam = async () => {
  if (!addFormRef.value) return
  
  addFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    if (!form.category) {
      ElMessage.error('内部错误：产品类ID丢失')
      return
    }
    
    if (params.value.some((p: CategoryParam) => p.name === form.name && p.category === form.category)) {
      ElMessage.error(`参数项 "${form.name}" 已存在于 ${selectedCategoryName.value} 中。`)
      return
    }
    
    submitting.value = true
    try {
      await paramStore.createParam(form)
      ElMessage.success('新增参数项成功')
      closeAddDialog()
      orderChanged.value = false;
    } catch (error: any) {
      ElMessage.error(error.message || '新增参数项失败')
    } finally {
      submitting.value = false
    }
  })
}

const updateParam = async () => {
  if (!editFormRef.value || form.id === null) return
  
  editFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    if (!form.category) {
      ElMessage.error('内部错误：产品类ID丢失')
      return
    }

    if (params.value.some((p: CategoryParam) => p.name === form.name && p.category === form.category && p.id !== form.id)) {
      ElMessage.error(`参数项 "${form.name}" 已存在于 ${selectedCategoryName.value} 中。`)
      return
    }
    
    submitting.value = true
    try {
      await paramStore.updateParam(form.id as number, form)
      ElMessage.success('更新参数项成功')
      closeEditDialog()
    } catch (error: any) {
      ElMessage.error(error.message || '更新参数项失败')
    } finally {
      submitting.value = false
    }
  })
}

const deleteParam = async (id: number) => {
  try {
    await paramStore.deleteParam(id)
    ElMessage.success('删除参数项成功')
  } catch (error: any) {
    ElMessage.error(error.message || '删除参数项失败')
  }
}

onMounted(async () => {
  await fetchCategories()
  if (categories.value.length > 0 && !selectedCategory.value) {
  } else if (selectedCategory.value) {
    paramStore.fetchParams()
  }
  orderChanged.value = false;
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.param-container {
  .filter-card {
    margin-bottom: 16px;
    .el-form-item {
      margin-bottom: 0;
    }
  }
  .category-select {
    width: 600px;
  }
}
</style>

