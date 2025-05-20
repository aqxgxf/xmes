<template>
  <div class="category-material-rule-list">
    <div class="page-header">
      <h2>产品类BOM物料规则</h2>
      <el-button type="primary" @click="openRuleDialog()">新增物料规则</el-button>
    </div>
    
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="产品类">
          <el-select
            v-model="searchForm.source_category"
            placeholder="请选择产品类"
            clearable
            filterable
          >
            <el-option
              v-for="category in productCategories"
              :key="category.id"
              :label="`${category.code}-${category.display_name}`"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="物料产品类">
          <el-select
            v-model="searchForm.target_category"
            placeholder="请选择物料产品类"
            clearable
            filterable
          >
            <el-option
              v-for="category in productCategories"
              :key="category.id"
              :label="`${category.code}-${category.display_name}`"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-table
      v-loading="loading"
      :data="rules"
      border
      style="width: 100%"
    >
      <el-table-column label="ID" prop="id" width="80" />
      <el-table-column label="产品类代码" prop="source_category_code" width="150" />
      <el-table-column label="产品类名称" prop="source_category_name" min-width="200" />
      <el-table-column label="物料产品类代码" prop="target_category_code" width="150" />
      <el-table-column label="物料产品类名称" prop="target_category_name" min-width="200" />
      <el-table-column label="创建时间" prop="created_at" width="180" />
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="showParamExpressions(row)">
            参数表达式
          </el-button>
          <el-button type="warning" size="small" @click="openRuleDialog(row)">
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 产品类BOM物料规则表单对话框 -->
    <el-dialog
      v-model="ruleDialogVisible"
      :title="isEditing ? '编辑产品类BOM物料规则' : '新增产品类BOM物料规则'"
      width="500px"
    >
      <el-form
        ref="ruleFormRef"
        :model="ruleForm"
        :rules="ruleFormRules"
        label-width="120px"
        label-position="right"
      >
        <el-form-item label="产品类" prop="source_category">
          <el-select
            v-model="ruleForm.source_category"
            placeholder="请选择产品类"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="category in productCategories"
              :key="category.id"
              :label="`${category.code}-${category.display_name}`"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="物料产品类" prop="target_category">
          <el-select
            v-model="ruleForm.target_category"
            placeholder="请选择物料产品类"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="category in productCategories"
              :key="category.id"
              :label="`${category.code}-${category.display_name}`"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="ruleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitRuleForm">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 参数表达式对话框 -->
    <el-dialog
      v-model="paramsDialogVisible"
      :title="`${currentRule?.source_category_name || ''} → ${currentRule?.target_category_name || ''} 参数表达式`"
      width="800px"
    >
      <el-alert
        type="info"
        show-icon
        :closable="false"
        style="margin-bottom: 20px"
      >
        <p>使用<code>${参数表达式}</code>格式设置表达式，例如<code>${D2+3}</code>。</p>
        <p>表达式支持产品类的参数值和简单数学计算。</p>
      </el-alert>
      
      <!-- 替换为直接显示所有参数项的表单 -->
      <el-form :model="paramExpressionForm" label-width="120px">
        <el-form-item 
          v-for="param in targetCategoryParams" 
          :key="param.id"
          :label="param.name"
        >
          <div class="param-expression-row">
            <el-input 
              v-model="paramExpressionForm[param.id]" 
              placeholder="请输入表达式，如${D2+3}"
              clearable
            >
              <template #append>
                <el-button 
                  type="primary" 
                  @click="saveParamExpression(param.id)"
                  :loading="savingParam === param.id"
                >
                  保存
                </el-button>
              </template>
            </el-input>
          </div>
        </el-form-item>
      </el-form>
      
      <!-- 现有参数表达式列表 -->
      <div v-if="paramExpressions.length > 0" style="margin-top: 20px">
        <h3>已配置参数表达式</h3>
        <el-table
          :data="paramExpressions"
          border
          style="width: 100%"
        >
          <el-table-column label="参数名称" prop="param_name" width="180" />
          <el-table-column label="表达式" prop="expression" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button type="danger" size="small" @click="deleteExpression(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import axios from '../../../api'
import { useCategoryMaterialRuleStore } from '../../../stores/categoryMaterialRuleStore'
import type { CategoryMaterialRule, CategoryMaterialRuleForm, CategoryMaterialRuleParam, ProductCategory, CategoryParam } from '../../../types'

// 组件状态
const loading = ref(false)
const rules = ref<CategoryMaterialRule[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchForm = reactive({
  source_category: undefined as number | undefined,
  target_category: undefined as number | undefined,
})

// 对话框状态
const ruleDialogVisible = ref(false)
const isEditing = ref(false)
const ruleFormRef = ref<FormInstance>()
const ruleForm = reactive<CategoryMaterialRuleForm>({
  id: null,
  source_category: 0,
  target_category: 0
})

// 表单验证规则
const ruleFormRules = {
  source_category: [
    { required: true, message: '请选择产品类', trigger: 'change' }
  ],
  target_category: [
    { required: true, message: '请选择物料产品类', trigger: 'change' }
  ]
}

// 产品类数据
const productCategories = ref<ProductCategory[]>([])

// 参数表达式相关状态
const paramsDialogVisible = ref(false)
const currentRule = ref<CategoryMaterialRule | null>(null)
const paramExpressions = ref<CategoryMaterialRuleParam[]>([])
const savingParam = ref<number | null>(null)

// 目标产品类参数
const targetCategoryParams = ref<CategoryParam[]>([])

// 参数表达式表单
const paramExpressionForm = reactive<Record<number, string>>({})

// Store
const categoryMaterialRuleStore = useCategoryMaterialRuleStore()

// 生命周期钩子
onMounted(async () => {
  await fetchProductCategories()
  await fetchRules()
})

// 获取产品类数据
async function fetchProductCategories() {
  loading.value = true
  try {
    const response = await axios.get('/product-categories/')
    productCategories.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取产品类数据失败')
  } finally {
    loading.value = false
  }
}

// 获取规则列表
async function fetchRules() {
  loading.value = true
  const params = {
    page: currentPage.value,
    page_size: pageSize.value,
    ...searchForm
  }
  
  try {
    await categoryMaterialRuleStore.fetchRules(params)
    rules.value = categoryMaterialRuleStore.rules
    total.value = categoryMaterialRuleStore.total
  } finally {
    loading.value = false
  }
}

// 搜索处理
function handleSearch() {
  currentPage.value = 1
  fetchRules()
}

// 重置搜索
function resetSearch() {
  searchForm.source_category = undefined
  searchForm.target_category = undefined
  currentPage.value = 1
  fetchRules()
}

// 分页处理
function handleSizeChange(val: number) {
  pageSize.value = val
  fetchRules()
}

function handleCurrentChange(val: number) {
  currentPage.value = val
  fetchRules()
}

// 打开规则对话框
function openRuleDialog(row?: CategoryMaterialRule) {
  isEditing.value = !!row
  if (row) {
    ruleForm.id = row.id
    ruleForm.source_category = row.source_category
    ruleForm.target_category = row.target_category
  } else {
    ruleForm.id = null
    ruleForm.source_category = 0
    ruleForm.target_category = 0
  }
  ruleDialogVisible.value = true
}

// 提交规则表单
async function submitRuleForm() {
  if (!ruleFormRef.value) return
  
  await ruleFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      loading.value = true
      if (isEditing.value && ruleForm.id) {
        await categoryMaterialRuleStore.updateRule(ruleForm.id, ruleForm)
      } else {
        await categoryMaterialRuleStore.createRule(ruleForm)
      }
      
      ruleDialogVisible.value = false
      fetchRules()
    } finally {
      loading.value = false
    }
  })
}

// 删除规则
function handleDelete(row: CategoryMaterialRule) {
  ElMessageBox.confirm(
    `确定要删除规则"${row.source_category_name} → ${row.target_category_name}"吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      loading.value = true
      try {
        const success = await categoryMaterialRuleStore.deleteRule(row.id)
        if (success) {
          fetchRules()
        }
      } finally {
        loading.value = false
      }
    })
    .catch(() => {
      // 用户取消删除操作
    })
}

// 显示参数表达式
async function showParamExpressions(rule: CategoryMaterialRule) {
  currentRule.value = rule
  
  // 清空表单数据
  Object.keys(paramExpressionForm).forEach(key => {
    delete paramExpressionForm[Number(key)]
  })
  
  await fetchTargetCategoryParams(rule.target_category)
  await fetchParamExpressions(rule.id)
  
  // 将已存在的表达式填充到表单中
  paramExpressions.value.forEach(expr => {
    paramExpressionForm[expr.target_param] = expr.expression
  })
  
  paramsDialogVisible.value = true
}

// 获取参数表达式列表
async function fetchParamExpressions(ruleId: number) {
  loading.value = true
  try {
    const expressions = await categoryMaterialRuleStore.fetchRuleParams(ruleId)
    paramExpressions.value = expressions
  } finally {
    loading.value = false
  }
}

// 获取目标产品类参数
async function fetchTargetCategoryParams(categoryId: number) {
  loading.value = true
  try {
    const response = await axios.get('/category-params/', {
      params: { category: categoryId }
    })
    targetCategoryParams.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取产品类参数失败')
  } finally {
    loading.value = false
  }
}

// 保存参数表达式
async function saveParamExpression(paramId: number) {
  if (!currentRule.value) return
  
  const expression = paramExpressionForm[paramId]
  if (!expression) {
    ElMessage.warning('请输入表达式')
    return
  }
  
  savingParam.value = paramId
  
  try {
    // 查找现有表达式
    const existingExpr = paramExpressions.value.find(expr => expr.target_param === paramId)
    
    if (existingExpr) {
      // 更新现有表达式
      await categoryMaterialRuleStore.updateRuleParam(existingExpr.id!, {
        rule: currentRule.value.id,
        target_param: paramId,
        expression: expression
      })
      ElMessage.success('更新表达式成功')
    } else {
      // 创建新表达式
      await categoryMaterialRuleStore.createRuleParam({
        rule: currentRule.value.id,
        target_param: paramId,
        expression: expression
      })
      ElMessage.success('添加表达式成功')
    }
    
    // 重新获取表达式列表
    await fetchParamExpressions(currentRule.value.id)
  } catch (error) {
    console.error('保存表达式失败:', error)
    ElMessage.error('保存表达式失败')
  } finally {
    savingParam.value = null
  }
}

// 删除表达式
function deleteExpression(row: CategoryMaterialRuleParam) {
  ElMessageBox.confirm(
    '确定要删除该参数表达式吗？',
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      loading.value = true
      try {
        const success = await categoryMaterialRuleStore.deleteRuleParam(row.id!)
        if (success && currentRule.value) {
          // 重新获取表达式列表
          await fetchParamExpressions(currentRule.value.id)
          
          // 从表单中移除该参数的表达式
          delete paramExpressionForm[row.target_param]
        }
      } finally {
        loading.value = false
      }
    })
    .catch(() => {
      // 用户取消删除操作
    })
}
</script>

<style scoped>
.category-material-rule-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.el-form-item {
  margin-bottom: 20px;
}

/* 参数表达式行样式 */
.param-expression-row {
  display: flex;
  align-items: center;
  width: 100%;
}

.param-expression-row .el-input {
  flex: 1;
}
</style> 