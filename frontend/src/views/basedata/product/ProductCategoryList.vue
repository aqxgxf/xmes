<template>
  <div class="product-category-container page-container">
    <data-table
      :data="categoryStore.categories"
      :loading="categoryStore.loading"
      :total="categoryStore.total"
      :initial-current-page="categoryStore.currentPage"
      :initial-page-size="categoryStore.pageSize"
      row-key="id"
      :selectable="true"
      :show-actions="true"
      actions-label="操作"
      :actions-width="180" 
      :show-search="true"
      search-placeholder="搜索产品类编码或名称"
      @page-change="categoryStore.handleCurrentChange"
      @size-change="categoryStore.handleSizeChange"
      @selection-change="handleSelectionChange"
      @search="handleTableSearch" 
      @sort-change="handleSortChange"
    >
      <!-- Toolbar Actions Slot -->
      <template #actions>
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon> 新增产品类
        </el-button>
        <el-button type="success" @click="uploadVisible = true">
          <el-icon><Upload /></el-icon> 导入
        </el-button>
        <el-button type="info" @click="downloadTemplate">
          <el-icon><Download /></el-icon> 下载模板
        </el-button>
        <el-button type="success" @click="exportCategoryParams">
          <el-icon><Document /></el-icon> 导出参数
        </el-button>
      </template>

      <!-- Columns Definition -->
      <el-table-column prop="code" label="产品类编码" min-width="120" sortable="custom" />
      <el-table-column prop="display_name" label="产品类名称" min-width="150" sortable="custom" />
      <el-table-column label="客户/公司" min-width="120" sortable="custom" prop="company.name"> 
        <template #default="{ row }">
          {{ row.company?.name || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="单位" min-width="80" prop="unit.name">
        <template #default="{ row }">
          {{ row.unit?.name || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="材质" min-width="120" prop="material_type.name">
        <template #default="{ row }">
          {{ row.material_type?.name || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="创建时间" min-width="160">
        <template #default="{ row }">
          {{ row.created_at ? row.created_at.slice(0, 19).replace('T', ' ') : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="图纸PDF" prop="drawing_pdf" width="120">
        <template #default="{ row }">
          <el-link v-if="row.drawing_pdf" :href="getCorrectPdfViewerUrl(row.drawing_pdf)" target="_blank" type="primary">
            查看图纸
          </el-link>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="工艺PDF" prop="process_pdf" width="120">
        <template #default="{ row }">
          <el-link v-if="row.process_pdf" :href="getCorrectPdfViewerUrl(row.process_pdf)" target="_blank" type="primary">
            查看工艺
          </el-link>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <!-- Row Actions Slot -->
      <template #row-actions="{ row }">
        <el-tooltip content="编辑" placement="top">
          <el-button size="small" type="primary" @click="openEditDialog(row)" :style="{padding: '0 6px'}">
            <el-icon><Edit /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="详情" placement="top">
          <el-button size="small" type="info" @click="viewDetails(row)" :style="{padding: '0 6px'}">
            <el-icon><View /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="删除" placement="top">
          <el-button size="small" type="danger" @click="confirmDelete(row)" :style="{padding: '0 6px'}">
            <el-icon><Delete /></el-icon>
          </el-button>
        </el-tooltip>
      </template>
    </data-table>

    <!-- 批量操作区域 (如果需要，可以放在 DataTable 外部或者通过一个 slot 传入 DataTable 的 toolbar) -->
    <div class="batch-actions-external" v-if="multipleSelection.length > 0">
        <el-alert title="批量操作区域" type="info" :closable="false" show-icon>
          <div class="batch-buttons">
            <span>已选择 {{ multipleSelection.length }} 项</span>
            <el-button size="small" type="danger" @click="confirmBatchDelete">
              <el-icon><Delete /></el-icon> 批量删除
            </el-button>
          </div>
        </el-alert>
      </div>

    <!-- 产品类表单对话框 -->
    <category-form-dialog 
      :visible="showDialog" 
      @update:visible="showDialog = $event" 
      :loading="categoryStore.submitting"
      :title="currentFormMode === 'add' ? '新增产品类' : '编辑产品类'" 
      :companies="categoryStore.companies"
      :units="categoryStore.units" 
      :form="formStore.form" 
      :rules="formStore.rules" 
      :materials="materialTypes"
      @save="saveCategory" 
      @close="closeDialog" />

    <!-- 导入对话框 -->
    <el-dialog v-model="uploadVisible" title="导入产品类" width="400px">
      <el-upload 
        ref="uploadRef" 
        class="upload-container" 
        action="#" 
        :auto-upload="false" 
        :show-file-list="true"
        :limit="1" 
        :on-exceed="() => ElMessage.warning('一次只能上传一个文件')" 
        :before-upload="beforeUpload"
        :http-request="handleImport">
        <el-button type="primary">
          <el-icon><Upload /></el-icon> 选择文件
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
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Upload, Download, Search, Document, View } from '@element-plus/icons-vue'
import type { UploadInstance } from 'element-plus'
import type { ProductCategory, MaterialType } from '../../../types/common'
import { generateExcelTemplate } from '../../../utils/helpers'
import api from '../../../api'
import { getCorrectPdfViewerUrl } from '../../../utils/pdfHelpers'

import DataTable from '../../../components/common/DataTable.vue' // Import DataTable
import CategoryFormDialog from '../../../components/basedata/CategoryFormDialog.vue'
import { useCategoryForm } from '../../../composables/useCategoryForm'
import { useCategoryStore } from '../../../stores/categoryStore'
import { useProductStore } from '../../../stores/product' // 保留，可能viewDetails或其他地方用到
import { useUserStore } from '../../../stores/user' // 保留，可能viewDetails或其他地方用到
import { useMaterialStore } from '../../../stores/materialStore'

const categoryStore = useCategoryStore()
const productStore = useProductStore()
const userStore = useUserStore()
const router = useRouter()
const materialStore = useMaterialStore()
const formStore = useCategoryForm()

const showDialog = ref(false)
const currentFormMode = ref<'add' | 'edit'>('add')
const uploadVisible = ref(false)
const uploadRef = ref<UploadInstance>()
const multipleSelection = ref<ProductCategory[]>([])
const materialTypes = ref<MaterialType[]>([]) 

// 处理 DataTable 的选择变化
const handleSelectionChange = (selection: ProductCategory[]) => {
  multipleSelection.value = selection
  console.log('DataTable current selection:', selection)
}

// 处理 DataTable 的排序变化 (旧的 handleSortChange 需要适配新的事件参数)
type SortOrder = 'ascending' | 'descending' | null;
const handleSortChange = (sortInfo: { column: any, prop: string, order: SortOrder }) => {
  const fieldMapping: Record<string, string> = {
    'code': 'code',
    'display_name': 'display_name',
    'company.name': 'company__name',
    'unit.name': 'unit__name',
    'material_type.name': 'material_type__name'
  }
  const backendField = sortInfo.prop ? fieldMapping[sortInfo.prop] || sortInfo.prop : ''
  categoryStore.setSorting(backendField, sortInfo.order)
}

// 处理 DataTable 的搜索 (旧的 handleSearch 需要重命名或适配)
const handleTableSearch = (query: string) => {
  categoryStore.setSearchQuery(query) 
}

const openAddDialog = async () => {
  await materialStore.fetchMaterialTypes();
  materialTypes.value = materialStore.materialTypes;
  formStore.resetForm();
  currentFormMode.value = 'add';
  showDialog.value = true;
}

const openEditDialog = async (category: ProductCategory) => {
  await materialStore.fetchMaterialTypes();
  materialTypes.value = materialStore.materialTypes;
  
  formStore.resetForm();
  formStore.fillForm(category as unknown as import('../../../types/common').ProductCategoryForm);
  
  currentFormMode.value = 'edit';
  showDialog.value = true;
}

const closeDialog = () => {
  showDialog.value = false
}

const saveCategory = async () => {
  try {
    const form = formStore.form as any; // Use 'as any' for form to bypass strict type checking for dynamic properties
    const payload: any = { ...form };

    // Log the source values for debugging
    console.log('[DEBUG] saveCategory - form.company_id:', form.company_id);
    console.log('[DEBUG] saveCategory - form.company:', JSON.stringify(form.company));
    console.log('[DEBUG] saveCategory - form.unit_id:', form.unit_id);
    console.log('[DEBUG] saveCategory - form.unit:', JSON.stringify(form.unit));
    console.log('[DEBUG] saveCategory - form.material_type_id:', form.material_type_id);
    console.log('[DEBUG] saveCategory - form.material_type:', JSON.stringify(form.material_type));

    // Helper function to safely get ID
    const getNumericId = (value: any): number | null => {
      if (typeof value === 'number') return value;
      if (typeof value === 'object' && value !== null && typeof value.id === 'number') return value.id;
      if (typeof value === 'string' && value.trim() !== '' && !isNaN(Number(value))) return Number(value);
      return null;
    };

    payload.company_id = getNumericId(form.company_id || form.company);
    payload.unit_id = getNumericId(form.unit_id || form.unit);
    payload.material_type_id = getNumericId(form.material_type_id || form.material_type);

    // Remove original fields if they were objects, to only send xxx_id
    delete payload.company;
    delete payload.unit;
    delete payload.material_type;

    // Ensure IDs are either numbers or explicitly null, not NaN or undefined
    payload.company_id = (payload.company_id === null || isNaN(payload.company_id)) ? null : Number(payload.company_id);
    payload.unit_id = (payload.unit_id === null || isNaN(payload.unit_id)) ? null : Number(payload.unit_id);
    payload.material_type_id = (payload.material_type_id === null || isNaN(payload.material_type_id)) ? null : Number(payload.material_type_id);
    
    console.log('[DEBUG] saveCategory - final payload being sent:', JSON.stringify(payload));

    if (currentFormMode.value === 'add') {
      await categoryStore.createCategory(payload)
      ElMessage.success('添加产品类成功')
    } else {
      if (!form.id) return
      await categoryStore.updateCategory(form.id, payload)
      ElMessage.success('更新产品类成功')
    }
    closeDialog()
  } catch (error: any) {
    const errorMsg = categoryStore.handleApiError(error, '保存产品类失败')
    ElMessage.error(errorMsg)
  }
}

const confirmDelete = (category: ProductCategory) => {
  if (!category.id) return
  ElMessageBox.confirm(
    `确定要删除产品类 "${category.display_name}" 吗？此操作不可撤销。`,
    '删除确认',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    try {
      await categoryStore.deleteCategory(category.id)
      ElMessage.success('删除产品类成功')
    } catch (error: any) {
      const errorMsg = categoryStore.handleApiError(error, '删除产品类失败')
      ElMessage.error(errorMsg)
    }
  }).catch(() => { /* User cancelled */ })
}

const confirmBatchDelete = () => {
  if (multipleSelection.value.length === 0) return
  const selectedCount = multipleSelection.value.length;
  const selectedItems = [...multipleSelection.value];
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedCount} 个产品类吗？此操作不可撤销。`,
    '批量删除确认',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    try {
      const totalBeforeDelete = categoryStore.total;
      if (selectedItems.length > 0) {
        await categoryStore.deleteCategory(selectedItems[0].id);
      }
      if (selectedItems.length > 1) {
        const remainingDeletePromises = selectedItems.slice(1).map(category =>
          api.delete(`/product-categories/${category.id}/`)
        );
        await Promise.all(remainingDeletePromises);
        const expectedRemainingItems = totalBeforeDelete - selectedCount;
        const expectedTotalPages = Math.ceil(expectedRemainingItems / categoryStore.pageSize);
        if (expectedTotalPages > 0 && categoryStore.currentPage > expectedTotalPages) {
          categoryStore.currentPage = expectedTotalPages;
        } else if (expectedTotalPages === 0) {
          categoryStore.currentPage = 1;
        }
        await categoryStore.fetchCategories();
      }
      ElMessage.success(`成功删除 ${selectedCount} 个产品类`);
      multipleSelection.value = [];
    } catch (error: any) {
      const errorMsg = categoryStore.handleApiError(error, '批量删除产品类失败');
      ElMessage.error(errorMsg);
    }
  }).catch(() => { /* User cancelled */ });
}

const exportCategoryParams = () => {
  try {
    window.open('/api/product-categories/export-params/', '_blank')
    ElMessage.success('开始导出产品类参数')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出产品类参数失败')
  }
}

const downloadTemplate = () => {
  const headers = ['code', 'display_name', 'company', 'unit', 'material_type'];
  const exampleData = [
    ['CAT001', '生产类', '客户A', 'PCS', 'S45C'], // Example using code for material_type
    ['CAT002', '零部件类', '客户B', 'BOX', 'Q235'] 
  ];
  generateExcelTemplate(headers, exampleData, '产品类导入模板', 'product_categories_template.xlsx')
}

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
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
  } catch (error: any) {
    const errorData = error.response?.data
    let formattedErrorMsg = '导入产品类失败'
    if (errorData && typeof errorData === 'object') {
      if (errorData.errors && typeof errorData.errors === 'object') {
        const errorDetails = Object.entries(errorData.errors)
          .map(([row, msg]) => `第${row}行: ${msg}`)
          .join('\n');
        if (errorDetails) {
          formattedErrorMsg = `导入失败，详情如下:\n${errorDetails}`;
        } else if (errorData.msg) {
          formattedErrorMsg = errorData.msg;
        }
      } else if (errorData.msg) {
        formattedErrorMsg = errorData.msg;
      } else if (errorData.detail) {
        formattedErrorMsg = errorData.detail;
      } else {
        const firstErrorKey = Object.keys(errorData)[0];
        if (firstErrorKey && Array.isArray(errorData[firstErrorKey]) && errorData[firstErrorKey].length > 0) {
          formattedErrorMsg = errorData[firstErrorKey][0];
        } else if (firstErrorKey && typeof errorData[firstErrorKey] === 'string') {
          formattedErrorMsg = errorData[firstErrorKey];
        }
      }
    }
    ElMessage.error({ 
      message: formattedErrorMsg, 
      dangerouslyUseHTMLString: true, 
      duration: 0, 
      showClose: true, 
      customClass: 'import-error-message' 
    });
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
  }
}

const viewDetails = (row: any) => {
  if (row.id) {
    router.push(`/product-categories/${row.id}/detail`);
  }
};

onMounted(async () => {
  await materialStore.fetchMaterialTypes();
  materialTypes.value = materialStore.materialTypes;
  await categoryStore.initialize()
})

</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.product-category-container {
  // .header-container, .search-actions, .pagination-container removed as DataTable handles them

  .no-file {
    color: #909399;
  }

  // .action-buttons styling might still be relevant for #row-actions slot items if not handled by DataTable implicitly
  // We might need to adjust if the layout within the slot needs specific styling, 
  // but el-button already has good default spacing.

  .upload-container {
    text-align: center;
  }

  .batch-actions-external {
    margin-top: 16px; // Add some space if DataTable pagination is also shown
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

<style lang="scss"> 
.import-error-message .el-message__content {
  white-space: pre-wrap; 
}
</style>
