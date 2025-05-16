<!-- filepath: h:\xmes\frontend\src\views\basedata\process/ProductProcessCodeList.vue -->
<template>
  <div class="product-process-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">产品工艺关联</h2>
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
          <el-form-item label="产品">
            <el-select v-model="productProcessCodeStore.searchParams.product" placeholder="请选择产品" filterable clearable
              @change="productProcessCodeStore.handleSearch" class="filter-select">
              <el-option v-for="product in productProcessCodeStore.products" :key="product.id"
                :label="`${product.name} (${product.code || ''})`" :value="product.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="工艺流程代码">
            <el-select v-model="productProcessCodeStore.searchParams.processCode" placeholder="请选择工艺流程代码" filterable
              clearable @change="productProcessCodeStore.handleSearch" class="filter-select">
              <el-option v-for="code in productProcessCodeStore.processCodes" :key="code.id"
                :label="`${code.code} (${code.version})`" :value="code.id" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="productProcessCodeStore.handleSearch">
              <el-icon>
                <Search />
              </el-icon> 搜索
            </el-button>
            <el-button @click="productProcessCodeStore.resetSearch">
              <el-icon>
                <RefreshRight />
              </el-icon> 重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 数据表格 -->
      <el-table :data="productProcessCodeStore.productProcessCodes" border stripe
        v-loading="productProcessCodeStore.loading" style="width: 100%">
        <el-table-column prop="product_name" label="产品名称" min-width="150" />
        <el-table-column prop="product_code" label="产品编码" min-width="120" />
        <el-table-column prop="process_code_text" label="工艺流程代码" min-width="150" />
        <el-table-column prop="process_code_version" label="版本" width="80" />
        <el-table-column label="默认工艺" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_default ? 'success' : 'info'" effect="plain">
              {{ row.is_default ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="200" />
        <el-table-column label="操作" fixed="right" min-width="240">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" @click="openEditDialog(row)">
                <el-icon>
                  <Edit />
                </el-icon> 编辑
              </el-button>
              <el-button size="small" type="danger" @click="confirmDelete(row)">
                <el-icon>
                  <Delete />
                </el-icon> 删除
              </el-button>
              <el-button v-if="!row.is_default" size="small" type="success" @click="setAsDefault(row)">
                <el-icon>
                  <Check />
                </el-icon> 设为默认
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页控件 -->
      <div class="pagination-container">
        <el-pagination :current-page="productProcessCodeStore.currentPage"
          :page-size="productProcessCodeStore.pageSize" 
          @update:current-page="val => productProcessCodeStore.currentPage = val"
          @update:page-size="val => productProcessCodeStore.pageSize = val"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper" :total="productProcessCodeStore.total"
          @size-change="productProcessCodeStore.handleSizeChange"
          @current-change="productProcessCodeStore.handleCurrentChange" background />
      </div>
    </el-card>

    <!-- 产品工艺关联表单对话框 -->
    <product-process-code-form-dialog :visible="showDialog" @update:visible="showDialog = $event"
      :title="currentFormMode === 'add' ? '新增产品工艺关联' : '编辑产品工艺关联'" :loading="productProcessCodeStore.submitting"
      :form="formStore.form" :rules="formStore.rules" :products="productProcessCodeStore.products"
      :process-codes="productProcessCodeStore.processCodes" @save="saveProductProcessCode" @close="closeDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Check, Search, RefreshRight } from '@element-plus/icons-vue'
import { useProductProcessCodeStore } from '../../../stores/productProcessCodeStore'
import { useProductProcessCodeForm } from '../../../composables/useProductProcessCodeForm'
// @ts-ignore - Vue SFC默认没有导出，但在Vue项目中可以正常使用
import ProductProcessCodeFormDialog from '../../../components/basedata/ProductProcessCodeFormDialog.vue'
import type { ProductProcessCode } from '../../../types/common'

// 获取Store
const productProcessCodeStore = useProductProcessCodeStore()

// 使用表单逻辑组合式函数
const formStore = useProductProcessCodeForm()

// 对话框状态
const showDialog = ref(false)
const currentFormMode = ref<'add' | 'edit'>('add')

// 添加产品工艺关联
const openAddDialog = () => {
  formStore.resetForm()
  currentFormMode.value = 'add'
  showDialog.value = true
}

// 编辑产品工艺关联
const openEditDialog = (item: ProductProcessCode) => {
  formStore.fillForm(item)
  currentFormMode.value = 'edit'
  showDialog.value = true
}

// 关闭对话框
const closeDialog = () => {
  showDialog.value = false
}

// 保存产品工艺关联
const saveProductProcessCode = async () => {
  try {
    if (currentFormMode.value === 'add') {
      await productProcessCodeStore.createProductProcessCode(formStore.form)
      ElMessage.success('添加产品工艺关联成功')
    } else {
      if (!formStore.form.id) return
      await productProcessCodeStore.updateProductProcessCode(formStore.form.id, formStore.form)
      ElMessage.success('更新产品工艺关联成功')
    }

    closeDialog()
  } catch (error: any) {
    const errorMsg = productProcessCodeStore.handleApiError(error, '保存产品工艺关联失败')
    ElMessage.error(errorMsg)
  }
}

// 确认删除
const confirmDelete = (row: ProductProcessCode) => {
  if (!row.id) return

  ElMessageBox.confirm(
    `确定要删除该产品工艺关联吗？此操作不可恢复。`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  ).then(async () => {
    try {
      await productProcessCodeStore.deleteProductProcessCode(row.id)
      ElMessage.success('删除产品工艺关联成功')
    } catch (error: any) {
      const errorMsg = productProcessCodeStore.handleApiError(error, '删除产品工艺关联失败')
      ElMessage.error(errorMsg)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 设置为默认工艺
const setAsDefault = async (row: ProductProcessCode) => {
  if (!row.id) return

  try {
    await productProcessCodeStore.setAsDefault(row.id)
    ElMessage.success('设置默认工艺成功')
  } catch (error: any) {
    const errorMsg = productProcessCodeStore.handleApiError(error, '设置默认工艺失败')
    ElMessage.error(errorMsg)
  }
}

// 页面初始化
onMounted(() => {
  productProcessCodeStore.initialize()
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
