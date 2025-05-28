<template>
  <div class="product-container page-container">
    <data-table
      :data="productStore.products"
      :loading="productStore.isLoading"
      :total="productStore.totalProducts"
      :initial-current-page="productStore.currentPage"
      :initial-page-size="productStore.pageSize"
      row-key="id"
      :selectable="true"
      :show-actions="true"
      actions-label="操作"
      :actions-width="250"
      :show-search="true"
      search-placeholder="搜索产品代码、名称或类别"
      @page-change="handlePageChange"
      @size-change="handleSizeChange"
      @selection-change="handleSelectionChange"
      @search="handleTableSearch"
      @sort-change="handleSortChange"
    >
      <template #actions>
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon> 新增产品
        </el-button>
        <el-button type="success" @click="downloadTemplate">
          <el-icon><Download /></el-icon> 下载模板
        </el-button>
        <el-button type="success" @click="uploadVisible = true">
          <el-icon><Upload /></el-icon> 导入
        </el-button>
      </template>

      <el-table-column type="selection" width="55" />
      <el-table-column prop="code" label="产品代码" min-width="120" sortable="custom" />
      <el-table-column prop="name" label="产品名称" min-width="150" sortable="custom" />
      <el-table-column prop="category_name" label="产品类别" min-width="120" sortable="custom">
        <template #default="{ row }">
          {{ row.category_name || (row.category ? categoryStore.getCategoryName(row.category) : '-') }}
        </template>
      </el-table-column>
      <el-table-column prop="specification" label="规格" min-width="120" />
      <el-table-column prop="price" label="价格" min-width="100" sortable="custom">
        <template #default="{ row }">
          {{ row.price === 0 ? '0' : (row.price !== null && row.price !== undefined ? Number(row.price).toFixed(2) : '0') }}
        </template>
      </el-table-column>
      <el-table-column prop="unit_name" label="单位" min-width="80" />
      <el-table-column prop="description" label="描述" min-width="200" />
      <el-table-column label="材质" min-width="120">
        <template #default="{ row }">
          {{
            (() => {
              let categoryId = row.category
              if (typeof categoryId === 'object' && categoryId !== null && 'id' in categoryId) categoryId = (categoryId as any).id
              const cat = categoryStore.categories.find(c => c.id === categoryId)
              return cat && cat.material_type ? cat.material_type.name : '-'
            })()
          }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建日期" min-width="160" sortable="custom">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      
      <template #row-actions="{ row }">
        <el-tooltip content="详情" placement="top">
          <el-button type="info" size="small" @click="goToDetail(row)" :style="{padding: '0 6px'}">
            <el-icon><Document /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="编辑" placement="top">
          <el-button type="primary" size="small" @click="openEditDialog(row)" :style="{padding: '0 6px'}">
            <el-icon><Edit /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="删除" placement="top">
          <el-button type="danger" size="small" @click="confirmDelete(row)" :style="{padding: '0 6px'}">
            <el-icon><Delete /></el-icon>
          </el-button>
        </el-tooltip>
      </template>
    </data-table>

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

    <product-form-dialog
      v-model:visible="showProductDialog"
      :title="productDialogTitle"
      :product-data="currentProductForEdit"
      :is-submitting="isFormSubmitting"
      @save="handleSaveProduct"
      @close="handleCloseProductDialog"
    />

    <el-dialog v-model="uploadVisible" title="导入产品" width="600px">
      <el-upload ref="uploadRef" class="upload-container" action="#" :auto-upload="false" :show-file-list="true"
        :limit="1" :on-exceed="() => ElMessage.warning('一次只能上传一个文件')" :before-upload="beforeUpload"
        :http-request="handleUpload">
        <el-button type="primary">
          <el-icon><Upload /></el-icon> 选择文件
        </el-button>
        <template #tip>
          <div class="el-upload__tip">
            只能上传xlsx/xls/csv文件，且不超过10MB
          </div>
        </template>
      </el-upload>
      <div v-if="importResult" class="import-result">
        <el-divider content-position="center">导入结果</el-divider>
        <el-alert :title="importResult.message" :type="importResult.success ? 'success' : 'warning'"
          :description="importResult.details" show-icon />
        <div class="import-stats">
          <el-row :gutter="20">
            <el-col :span="6"><div class="stat-item"><div class="stat-value">{{ importResult.total }}</div><div class="stat-label">总行数</div></div></el-col>
            <el-col :span="6"><div class="stat-item success"><div class="stat-value">{{ importResult.successCount }}</div><div class="stat-label">成功</div></div></el-col>
            <el-col :span="6"><div class="stat-item warning"><div class="stat-value">{{ importResult.skipped }}</div><div class="stat-label">跳过</div></div></el-col>
            <el-col :span="6"><div class="stat-item error"><div class="stat-value">{{ importResult.fail }}</div><div class="stat-label">失败</div></div></el-col>
          </el-row>
        </div>
        <div v-if="importResult.error_details && importResult.error_details.length > 0" class="error-details">
          <h4>错误详情：</h4>
          <el-collapse><el-collapse-item title="查看错误详情" name="1">
            <el-table :data="importResult.error_details" border stripe max-height="250">
              <el-table-column prop="row" label="行号" width="80" />
              <el-table-column prop="message" label="错误信息" />
            </el-table>
          </el-collapse-item></el-collapse>
        </div>
        <div v-if="importResult.duplicate_details && importResult.duplicate_details.length > 0" class="duplicate-details">
          <h4>重复数据详情：</h4>
          <el-collapse><el-collapse-item title="查看重复数据" name="1">
            <el-table :data="importResult.duplicate_details" border stripe max-height="250">
              <el-table-column prop="code" label="产品代码" />
              <el-table-column prop="row" label="行号" width="80" />
            </el-table>
          </el-collapse-item></el-collapse>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadVisible = false">关闭</el-button>
          <el-button v-if="!importResult" type="primary" @click="() => uploadRef?.submit()" :loading="productStore.isLoading">
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Plus, Edit, Delete, Download, Upload, Document } from '@element-plus/icons-vue';
import type { UploadInstance } from 'element-plus';
import { useProductStore } from '../../../stores/product';
import { useCategoryStore } from '../../../stores/categoryStore';
import { formatDateTime, generateExcelTemplate } from '../../../utils/helpers';
import type { Product, Unit } from '../../../types/common';
import type { ProductParam, ProductParamValue } from '../../../types';
import api from '../../../api';
import { applyMaterialRules, createProductProcess, saveProductParamValues } from '../../../utils/productHelper';
import DataTable from '../../../components/common/DataTable.vue';
import ProductFormDialog from '../../../components/basedata/ProductFormDialog.vue';

const productStore = useProductStore();
const categoryStore = useCategoryStore();
const router = useRouter();

const uploadVisible = ref(false);
const multipleSelection = ref<Product[]>([]);
const uploadRef = ref<UploadInstance>();
const importResult = ref<{
  success: boolean;
  message: string;
  details: string;
  total: number;
  successCount: number;
  fail: number;
  skipped: number;
  error_details?: { row: string; message: string }[];
  duplicate_details?: { code: string; row: string | number }[];
} | null>(null);

const showProductDialog = ref(false);
const productDialogTitle = ref('新增产品');
const currentProductForEdit = ref<Product | null>(null);
const isFormSubmitting = ref(false);

onMounted(async () => {
  await productStore.initialize();
  await categoryStore.initialize();
});

const openAddDialog = () => {
  currentProductForEdit.value = null;
  productDialogTitle.value = '新增产品';
  showProductDialog.value = true;
};

const openEditDialog = (row: Product) => {
  currentProductForEdit.value = { ...row };
  productDialogTitle.value = '编辑产品';
  showProductDialog.value = true;
};

const handleCloseProductDialog = () => {
  showProductDialog.value = false;
};

const handleSaveProduct = async (formData: Partial<Product> & { paramValues: Record<number, string> }) => {
  isFormSubmitting.value = true;
  let productSuccessfullyCreatedOrUpdated = false;
  try {
    let savedProduct: Product | null = null;
    const paramValuesToSave = formData.paramValues;
    const productDataPayload: Partial<Product> = { ...formData };
    delete (productDataPayload as any).paramValues;

    if (currentProductForEdit.value && currentProductForEdit.value.id) { // Editing
      savedProduct = await productStore.updateProduct(currentProductForEdit.value.id, productDataPayload);
    } else { // Adding
      savedProduct = await productStore.createProduct(productDataPayload);
    }

    if (savedProduct && savedProduct.id) {
      productSuccessfullyCreatedOrUpdated = true;
      await saveProductParamValues(savedProduct.id, paramValuesToSave || {});
      console.log('Saved product:', JSON.parse(JSON.stringify(savedProduct))); // Log a deep copy for inspection
      
      if (!currentProductForEdit.value) { // This is a new product
        console.log('New product detected. Checking is_material state:', savedProduct.is_material);
        // Ensure savedProduct.is_material is explicitly checked. 
        // Backend might set it, or it defaults to false from our store mapping if not sent by backend.
        if (savedProduct.is_material === false) {
          console.log('Product is not a material. Attempting to apply material rules and create product process...');
          try {
            await applyMaterialRules(savedProduct.id);
            console.log('Applied material rules successfully for product ID:', savedProduct.id);
            await createProductProcess(savedProduct.id);
            console.log('Created product process successfully for product ID:', savedProduct.id);
          } catch (rulesOrProcessError: any) {
            console.error('Error during material rules application or process creation:', rulesOrProcessError);
            ElMessage.error(`产品已保存，但自动生成BOM或工艺流程失败: ${rulesOrProcessError.message || '未知错误'}`); 
            // Set flag to false if BOM/Process is critical for success message, or handle separately
          }
        } else {
          console.log(`Product (ID: ${savedProduct.id}) is_material is ${savedProduct.is_material}, skipping BOM/process generation.`);
        }
      }
      // Moved success message to be more conditional if needed, or to finally block
    } else {
      // This case implies store action returned null or product without ID, which should be an error itself
      ElMessage.error(currentProductForEdit.value ? '产品更新失败 (store did not return valid product)' : '产品创建失败 (store did not return valid product)');
    }
  } catch (error: any) {
    // This catches errors from store actions (createProduct/updateProduct) if they throw
    console.error('Error saving product in handleSaveProduct:', error);
    ElMessage.error(`操作失败: ${error.response?.data?.detail || error.message || '未知错误'}`);
  } finally {
    isFormSubmitting.value = false;
    if (productSuccessfullyCreatedOrUpdated) {
      ElMessage.success(currentProductForEdit.value ? '产品更新成功' : '产品创建成功');
      showProductDialog.value = false; // Close dialog only on full success
    } 
    // If !productSuccessfullyCreatedOrUpdated and an error specific to BOM/Process occurred,
    // the dialog might remain open or you might choose to close it based on UX preference.
    // Currently, it closes only if the main save was successful.
  }
};

const handlePageChange = (page: number) => {
  productStore.handleCurrentChange(page);
};

const handleSizeChange = (size: number) => {
  productStore.handleSizeChange(size);
};

const handleTableSearch = (query: string) => {
  productStore.setSearchQuery(query);
};

type SortOrder = 'ascending' | 'descending' | null;
const handleSortChange = (sortInfo: { column: any, prop: string, order: SortOrder }) => {
  const fieldMapping: Record<string, string> = {
    'code': 'code',
    'name': 'name',
    'category_name': 'category__name',
    'price': 'price',
    'created_at': 'created_at'
  };
  const backendField = sortInfo.prop ? fieldMapping[sortInfo.prop] || sortInfo.prop : '';
  if (backendField) {
      productStore.setSorting(backendField, sortInfo.order);
  } else {
      productStore.setSorting('', null);
  }
};

const handleSelectionChange = (selection: Product[]) => {
  multipleSelection.value = selection;
};

const goToDetail = (row: Product) => {
  router.push(`/products/${row.id}/detail`);
};

const confirmDelete = (row: Product) => {
  ElMessageBox.confirm(
    `确定要删除产品 "${row.name}" 吗？这个操作不可逆。`,
    '删除确认',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
      await productStore.deleteProduct(row.id); // Assumes deleteProduct refreshes list or handles total count
      // ElMessage.success is usually handled by store or if not, can be added here
  }).catch(() => {});
};

const confirmBatchDelete = () => {
  if (multipleSelection.value.length === 0) return;
  ElMessageBox.confirm(
    `确定要删除选中的 ${multipleSelection.value.length} 个产品吗？这个操作不可逆。`,
    '批量删除确认',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    // A more robust batch delete might involve a single API call if backend supports it.
    // For now, deleting one by one and then refreshing.
    const deletePromises = multipleSelection.value.map(product => productStore.deleteProduct(product.id!));
    await Promise.all(deletePromises);
    ElMessage.success('批量删除成功');
    multipleSelection.value = []; 
    // productStore.fetchProducts(); // Assuming deleteProduct actions in store manage list refresh or total count correctly
  }).catch(() => {});
};

const downloadTemplate = () => {
  const headers = ['code', 'name', 'category_code', 'specification', 'description', 'unit_code', 'price'];
  const exampleData = [
    ['P001', '产品A', 'CAT001', '规格1', '描述1', 'PCS', 100.50],
    ['P002', '产品B', 'CAT002', '规格2', '描述2', 'KG', 25.00],
  ];
  generateExcelTemplate(headers, exampleData, '产品导入模板', '产品导入模板.xlsx');
};

function beforeUpload(file: File) {
  const isExcel = file.type.includes('excel') || file.type.includes('spreadsheet') || file.name.endsWith('.csv');
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isExcel) {
    ElMessage.error('只能上传Excel或CSV文件');
    return false;
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB');
    return false;
  }
  return true;
}

async function handleUpload(option: any) {
  importResult.value = null; // Reset previous result before new upload
  try {
    const result = await productStore.importProducts(option.file);
    if (result) {
        const errorDetailsList = result.fail_msgs 
            ? result.fail_msgs.map((msg: string, index: number) => ({ row: String(index + 1), message: msg })) 
            : [];
        const duplicateDetailsList = result.duplicate_codes 
            ? result.duplicate_codes.map((code: string, index: number) => ({ code: code, row: 'N/A' })) 
            : [];
        const messageFromServer = result.msg || `导入完成: ${result.success}成功, ${result.fail}失败, ${result.skipped}跳过.`;
        importResult.value = {
            success: (result.fail === 0 && result.skipped === 0 && result.success > 0), // success only if some rows succeeded and no fails/skips
            message: messageFromServer,
            details: errorDetailsList.map(err => `行 ${err.row}: ${err.message}`).join('\n'),
            total: result.total || ( (result.success || 0) + (result.fail || 0) + (result.skipped || 0) ),
            successCount: result.success || 0,
            fail: result.fail || 0,
            skipped: result.skipped || 0,
            error_details: errorDetailsList,
            duplicate_details: duplicateDetailsList
        };
        if(importResult.value.success){
            ElMessage.success(importResult.value.message || '导入成功完成');
        } else {
            ElMessage.warning(importResult.value.message || '导入已处理，但有失败或跳过的行。');
        }
        option.onSuccess(result);
    } else {
        importResult.value = { 
            success: false, 
            message: '导入处理失败，请检查后台日志或文件格式', 
            details: '', total:0, successCount:0, fail:0, skipped:0 
        };
        ElMessage.error(importResult.value.message);
        option.onError(new Error('Import processing failed in store'));
    }
  } catch (e: any) {
    importResult.value = { 
        success: false, 
        message: e.message || '上传或处理导入文件时发生错误', 
        details: e.response?.data?.detail || '', total:0, successCount:0, fail:0, skipped:0 
    };
    ElMessage.error(importResult.value.message);
    option.onError(e);
  } finally {
    if (uploadRef.value) {
        uploadRef.value.clearFiles();
    }
  }
}
</script>

<style scoped>
.product-container {
  padding: 20px;
}

.batch-actions-external { 
  margin-top: 16px;
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

.import-result {
  margin-top: 20px;
}

.import-stats {
  margin-top: 10px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.error-details,
.duplicate-details {
  margin-top: 10px;
}
</style>

<style lang="scss">
.import-error-message .el-message__content {
  white-space: pre-wrap; 
}
</style>
