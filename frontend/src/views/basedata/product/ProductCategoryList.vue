<template>
  <div class="product-category-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">产品类管理</h2>
          <div class="search-actions">
            <el-input v-model="categoryStore.searchQuery" placeholder="搜索产品类编码或名称" clearable @input="handleSearch">
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="openAddDialog">
              <el-icon>
                <Plus />
              </el-icon> 新增产品类
            </el-button>
            <el-button type="success" @click="uploadVisible = true">
              <el-icon>
                <Upload />
              </el-icon> 导入
            </el-button>
            <el-button type="info" @click="downloadTemplate">
              <el-icon>
                <Download />
              </el-icon> 下载模板
            </el-button>
            <el-button type="success" @click="exportCategoryParams">
              <el-icon>
                <Document />
              </el-icon> 导出参数
            </el-button>
          </div>
        </div>
      </template>

      <!-- 批量操作区域 -->
      <div class="batch-actions" v-if="multipleSelection.length > 0">
        <el-alert title="批量操作区域" type="info" :closable="false" show-icon>
          <div class="batch-buttons">
            <span>已选择 {{ multipleSelection.length }} 项</span>
            <el-button size="small" type="danger" @click="confirmBatchDelete">
              <el-icon>
                <Delete />
              </el-icon> 批量删除
            </el-button>
          </div>
        </el-alert>
      </div>

      <!-- 数据表格 -->
      <el-table :data="categoryStore.categories" v-loading="categoryStore.loading" border stripe row-key="id"
        style="width: 100%" @selection-change="handleSelectionChange" @sort-change="handleSortChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="code" label="产品类编码" min-width="120" sortable="custom" />
        <el-table-column prop="display_name" label="产品类名称" min-width="150" sortable="custom" />
        <el-table-column prop="company_name" label="公司" min-width="120" sortable="custom" />
        <el-table-column prop="unit_name" label="单位" min-width="80" />
        <el-table-column label="图纸PDF" align="center" width="120">
          <template #default="{ row }">
            <el-link v-if="row.drawing_pdf" :href="'/native-pdf-viewer?url=' + encodeURIComponent(row.drawing_pdf)"
              target="_blank" type="primary">
              <el-icon>
                <Document />
              </el-icon> 查看
            </el-link>
            <span v-else class="no-file">无</span>
          </template>
        </el-table-column>
        <el-table-column label="工艺PDF" align="center" width="120">
          <template #default="{ row }">
            <el-link v-if="row.process_pdf" :href="'/native-pdf-viewer?url=' + encodeURIComponent(row.process_pdf)"
              target="_blank" type="primary">
              <el-icon>
                <Document />
              </el-icon> 查看
            </el-link>
            <span v-else class="no-file">无</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
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
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页控件 -->
      <div class="pagination-container">
        <el-pagination :current-page="categoryStore.currentPage" :page-size="categoryStore.pageSize"
          @update:current-page="val => categoryStore.currentPage = val" 
          @update:page-size="val => categoryStore.pageSize = val"
          :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" :total="categoryStore.total"
          @size-change="categoryStore.handleSizeChange" @current-change="categoryStore.handleCurrentChange"
          background />
      </div>
    </el-card>

    <!-- 产品类表单对话框 -->
    <category-form-dialog :visible="showDialog" @update:visible="showDialog = $event" :loading="categoryStore.submitting"
      :title="currentFormMode === 'add' ? '新增产品类' : '编辑产品类'" :companies="categoryStore.companies"
      :units="categoryStore.units" :form="formStore.form" :rules="formStore.rules" @save="saveCategory"
      @close="closeDialog" />

    <!-- 导入对话框 -->
    <el-dialog v-model="uploadVisible" title="导入产品类" width="400px">
      <el-upload ref="uploadRef" class="upload-container" action="#" :auto-upload="false" :show-file-list="true"
        :limit="1" :on-exceed="() => ElMessage.warning('一次只能上传一个文件')" :before-upload="beforeUpload"
        :http-request="handleImport">
        <el-button type="primary">
          <el-icon>
            <Upload />
          </el-icon> 选择文件
        </el-button>
        <template #tip>
          <div class="el-upload__tip">
            只能上传xlsx/xls/csv文件，且不超过10MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadVisible = false">取消</el-button>
          <el-button type="primary" @click="() => uploadRef?.submit()" :loading="categoryStore.loading">
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Upload, Download, Search, Document } from '@element-plus/icons-vue'
import type { UploadInstance } from 'element-plus'
import type { ProductCategory } from '../../../types/common'
import { generateExcelTemplate } from '../../../utils/helpers'
import api from '../../../api'

// @ts-ignore - Vue SFC没有默认导出，但在Vue项目中可以正常工作
import CategoryFormDialog from '../../../components/basedata/CategoryFormDialog.vue'
import { useCategoryForm } from '../../../composables/useCategoryForm'
import { useCategoryStore } from '../../../stores/categoryStore'
import { useProductStore } from '../../../stores/product'

// 使用Store
const categoryStore = useCategoryStore()
const productStore = useProductStore()

// 使用表单逻辑组合式函数
const formStore = useCategoryForm()

// 对话框状态
const showDialog = ref(false)
const currentFormMode = ref<'add' | 'edit'>('add')
const uploadVisible = ref(false)
const uploadRef = ref<UploadInstance>()
const multipleSelection = ref<ProductCategory[]>([])

// 处理多选变化
const handleSelectionChange = (selection: ProductCategory[]) => {
  multipleSelection.value = selection
  console.log('当前选中项:', selection)
}

// 处理排序变化
const handleSortChange = (column: { prop: string, order: 'ascending' | 'descending' | null }) => {
  // 映射前端字段到后端字段
  const fieldMapping: Record<string, string> = {
    'code': 'code',
    'display_name': 'display_name',
    'company_name': 'company__name'  // 确保使用双下划线
  }

  console.log('排序变更:', column)
  const backendField = column.prop ? fieldMapping[column.prop] || column.prop : ''
  console.log('映射后的排序字段:', backendField)
  categoryStore.setSorting(backendField, column.order)
}

// 搜索处理
const handleSearch = () => {
  categoryStore.setSearchQuery(categoryStore.searchQuery)
}

// 对话框操作
const openAddDialog = () => {
  formStore.resetForm()
  currentFormMode.value = 'add'
  showDialog.value = true
}

const openEditDialog = (category: ProductCategory) => {
  formStore.resetForm()
  formStore.fillForm(category)
  currentFormMode.value = 'edit'
  showDialog.value = true
}

const closeDialog = () => {
  showDialog.value = false
}

// 保存产品类
const saveCategory = async () => {
  try {
    if (currentFormMode.value === 'add') {
      await categoryStore.createCategory(formStore.form)
      ElMessage.success('添加产品类成功')
    } else {
      if (!formStore.form.id) return
      await categoryStore.updateCategory(formStore.form.id, formStore.form)
      ElMessage.success('更新产品类成功')
    }
    closeDialog()
  } catch (error: any) {
    const errorMsg = categoryStore.handleApiError(error, '保存产品类失败')
    ElMessage.error(errorMsg)
  }
}

// 删除产品类
const confirmDelete = (category: ProductCategory) => {
  if (!category.id) return

  ElMessageBox.confirm(
    `确定要删除产品类 "${category.display_name}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await categoryStore.deleteCategory(category.id)
      ElMessage.success('删除产品类成功')
    } catch (error: any) {
      const errorMsg = categoryStore.handleApiError(error, '删除产品类失败')
      ElMessage.error(errorMsg)
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 批量删除产品类
const confirmBatchDelete = () => {
  if (multipleSelection.value.length === 0) return

  // 保存选中项的数量，避免异步操作过程中值被改变
  const selectedCount = multipleSelection.value.length;
  const selectedItems = [...multipleSelection.value];

  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedCount} 个产品类吗？此操作不可撤销。`,
    '批量删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      // 先获取总数，用于计算页码调整
      const totalBeforeDelete = categoryStore.total;
      const totalPagesBefore = Math.ceil(totalBeforeDelete / categoryStore.pageSize);
      
      // 删除第一个项目时，store里的deleteCategory会处理页码和数据刷新
      if (selectedItems.length > 0) {
        await categoryStore.deleteCategory(selectedItems[0].id);
      }
      
      // 删除其余项目，但不自动刷新页面（避免多次刷新）
      if (selectedItems.length > 1) {
        const remainingDeletePromises = selectedItems.slice(1).map(category =>
          api.delete(`/product-categories/${category.id}/`)
        );
        await Promise.all(remainingDeletePromises);
        
        // 计算删除后预计的总数和总页数
        const expectedRemainingItems = totalBeforeDelete - selectedCount;
        const expectedTotalPages = Math.ceil(expectedRemainingItems / categoryStore.pageSize);
        
        // 如果当前页超出了预计的总页数，调整到有效页码
        if (expectedTotalPages > 0 && categoryStore.currentPage > expectedTotalPages) {
          categoryStore.currentPage = expectedTotalPages;
        } else if (expectedTotalPages === 0) {
          categoryStore.currentPage = 1;
        }
        
        // 使用调整后的页码刷新数据
        await categoryStore.fetchCategories();
      }
      
      ElMessage.success(`成功删除 ${selectedCount} 个产品类`);
      // 清空选择
      multipleSelection.value = [];
    } catch (error: any) {
      const errorMsg = categoryStore.handleApiError(error, '批量删除产品类失败');
      ElMessage.error(errorMsg);
    }
  }).catch(() => {
    // 用户取消删除
  });
}

// 导出产品类参数到Excel
const exportCategoryParams = () => {
  try {
    // 使用window.open直接打开导出API，触发文件下载
    window.open('/api/product-categories/export-params/', '_blank')
    ElMessage.success('开始导出产品类参数')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出产品类参数失败')
  }
}

// 下载模板
const downloadTemplate = () => {
  // 定义产品类模板表头
  const headers = ['代码', '名称', '公司', '单位']

  // 定义示例数据（可选）
  const exampleData = [
    ['CAT001', '生产类', '', ''],
    ['CAT002', '零部件类', '', '']
  ]

  // 生成并下载 Excel 模板
  generateExcelTemplate(
    headers,
    exampleData,
    '产品类导入模板',
    'product_categories_template.xlsx'
  )
}

// 导入产品类
const beforeUpload = (file: File) => {
  const validExtensions = ['.xlsx', '.xls', '.csv']
  const fileName = file.name
  const extension = fileName.slice(fileName.lastIndexOf('.'))

  if (!validExtensions.includes(extension)) {
    ElMessage.error('仅支持Excel或CSV文件导入')
    return false
  }

  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB!')
    return false
  }

  return true
}

const handleImport = async (options: any) => {
  try {
    await categoryStore.importCategories(options.file)
    ElMessage.success('导入产品类成功')
    uploadVisible.value = false
  } catch (error: any) {
    const errorMsg = categoryStore.handleApiError(error, '导入产品类失败')
    ElMessage.error(errorMsg)
  }
}

// 页面初始化
onMounted(async () => {
  await categoryStore.initialize()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.product-category-container {
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page-title {
    margin: 0;
    font-size: 18px;
  }

  .search-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .no-file {
    color: #909399;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }

  .upload-container {
    text-align: center;
  }

  .batch-actions {
    margin-bottom: 16px;

    .batch-buttons {
      display: flex;
      justify-content: space-between;
      align-items: center;

      span {
        font-weight: bold;
      }
    }
  }
}
</style>
