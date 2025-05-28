<template>
  <div class="category-process-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">产品类工艺关联</h2>
          <div class="actions">
            <el-button type="primary" @click="openAddDialog">
              <el-icon>
                <Plus />
              </el-icon> 新增关联
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选区域 -->
      <div class="filter-container">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="产品类">
            <el-select v-model="categoryProcessCodeStore.searchParams.category" placeholder="请选择产品类" filterable clearable
              @change="categoryProcessCodeStore.handleSearch" class="filter-select">
              <el-option v-for="category in categoryProcessCodeStore.categories" :key="category.id"
                :label="`${category.display_name} (${category.code || ''})`" :value="category.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="工艺流程代码">
            <el-select v-model="categoryProcessCodeStore.searchParams.processCode" placeholder="请选择工艺流程代码" filterable
              clearable @change="categoryProcessCodeStore.handleSearch" class="filter-select">
              <el-option v-for="code in categoryProcessCodeStore.processCodes" :key="code.id"
                :label="`${code.code} (${code.version})`" :value="code.id" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="categoryProcessCodeStore.handleSearch">查询</el-button>
            <el-button @click="categoryProcessCodeStore.resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 表格区域 -->
      <el-table :data="categoryProcessCodeStore.categoryProcessCodes" v-loading="categoryProcessCodeStore.loading"
        border stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="category_code" label="产品类代码" min-width="120" />
        <el-table-column prop="category_name" label="产品类名称" min-width="150" />
        <el-table-column prop="process_code_text" label="工艺流程代码" min-width="150" />
        <el-table-column prop="process_code_version" label="版本" width="100" />
        <el-table-column label="是否默认" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_default ? 'success' : 'info'">{{ row.is_default ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 关联管理对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑关联' : '新增关联'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" label-position="left">
        <el-form-item label="产品类" prop="category">
          <el-select v-model="form.category" placeholder="请选择产品类" filterable class="form-input">
            <el-option v-for="category in categoryProcessCodeStore.categories" :key="category.id"
              :label="`${category.display_name} (${category.code || ''})`" :value="category.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="工艺流程代码" prop="process_code">
          <el-select v-model="form.process_code" placeholder="请选择工艺流程代码" filterable class="form-input">
            <el-option v-for="code in categoryProcessCodeStore.processCodes" :key="code.id"
              :label="`${code.code} (${code.version})`" :value="code.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="categoryProcessCodeStore.submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useCategoryProcessCodeStore } from '../../../stores/categoryProcessCodeStore'
import type { FormInstance } from 'element-plus'

// 状态定义
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const isEdit = ref(false)
const categoryProcessCodeStore = useCategoryProcessCodeStore()

// 表单数据
const form = reactive({
  id: undefined as number | undefined,
  category: null as number | null,
  process_code: null as number | null,
  is_default: false
})

// 表单验证规则
const rules = reactive({
  category: [{ required: true, message: '请选择产品类', trigger: 'change' }],
  process_code: [{ required: true, message: '请选择工艺流程代码', trigger: 'change' }]
})

// 初始化数据
onMounted(async () => {
  await categoryProcessCodeStore.initialize()
})

// 打开新增对话框
const openAddDialog = () => {
  isEdit.value = false
  form.id = undefined
  form.category = null
  form.process_code = null
  form.is_default = false
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (row: any) => {
  console.log('--- openEditDialog ---');
  console.log('row:', row);
  isEdit.value = true;
  console.log('form.category before:', form.category);
  form.id = row.id;
  form.category = row.category;
  form.process_code = row.process_code;
  form.is_default = row.is_default;
  console.log('form.category after:', form.category);
  console.log('categoryProcessCodeStore.categories:', categoryProcessCodeStore.categories);
  dialogVisible.value = true;
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    const formToSubmit = {
      ...form,
      category: form.category ?? 0,
      process_code: form.process_code ?? 0,
    };
    if (isEdit.value && form.id !== undefined) {
      await categoryProcessCodeStore.updateCategoryProcessCode(form.id, formToSubmit)
      ElMessage.success('更新成功')
    } else {
      await categoryProcessCodeStore.createCategoryProcessCode(formToSubmit)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
  } catch (err) {
    console.error('表单提交错误:', err)
  }
}

// 删除关联
const handleDelete = (row: any) => {
  ElMessageBox.confirm('确定要删除此关联吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await categoryProcessCodeStore.deleteCategoryProcessCode(row.id)
      ElMessage.success('删除成功')
    } catch (err) {
      console.error('删除失败:', err)
    }
  }).catch(() => {
    // 取消删除
  })
}

interface ProductCategoryProcessCodeForm {
  id?: number;
  category: number;
  process_code: number | null;
  is_default: boolean;
}
</script>

<style scoped>
.category-process-container {
  margin-top: 20px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 18px;
}

.filter-container {
  margin-bottom: 20px;
}

.filter-select {
  width: 250px;
}

.form-input {
  width: 100%;
}
</style> 