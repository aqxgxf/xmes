<template>
  <div class="material-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">物料管理</h2>
          <div class="search-actions">
            <el-input v-model="materialStore.searchQuery" placeholder="搜索物料名称/代码" clearable @input="handleSearch">
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="openAddDialog">
              <el-icon>
                <Plus />
              </el-icon> 新增物料
            </el-button>
            <el-upload :show-file-list="false" :before-upload="beforeImport" :http-request="handleImport"
              accept=".xlsx,.xls,.csv">
              <el-button type="success">
                <el-icon>
                  <Upload />
                </el-icon> 导入
              </el-button>
            </el-upload>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table :data="materialStore.materials" v-loading="materialStore.loading" border stripe style="width: 100%">
        <el-table-column prop="code" label="物料代码" min-width="120" />
        <el-table-column prop="name" label="物料名称" min-width="200" />
        <el-table-column prop="price" label="单价" min-width="100" />
        <el-table-column prop="category_name" label="物料类别" min-width="120" />
        <el-table-column prop="unit_name" label="单位" min-width="80" />
        <el-table-column label="材质" min-width="120">
          <template #default="{ row }">
            {{ row.category?.material?.name || row.material?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="drawing_pdf_url" label="图纸文件" width="120">
          <template #default="{ row }">
            <el-link v-if="row.drawing_pdf_url"
                     :href="getCorrectPdfViewerUrl(row.drawing_pdf_url.replace(/\/$/, ''))"
                     target="_blank" type="primary">
              <el-icon><Document /></el-icon> 查看
            </el-link>
            <span v-else>-</span>
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
        <el-pagination 
          v-model="materialStore.currentPage"
          :page-size="materialStore.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="materialStore.total"
          @size-change="materialStore.handleSizeChange"
          @current-change="materialStore.handleCurrentChange"
          background />
      </div>
    </el-card>

    <!-- 物料表单对话框 -->
    <MaterialFormDialog 
      :visible="showDialog"
      :loading="materialStore.submitting"
      :title="currentFormMode === 'add' ? '新增物料' : '编辑物料'"
      :categories="materialStore.categories"
      :units="materialStore.units"
      :params="materialStore.params"
      :form="formStore.form"
      :rules="formStore.rules"
      @save="saveMaterial"
      @close="closeDialog"
      @category-change="onCategoryChange"
      @param-change="handleParamValueChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineAsyncComponent } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Upload, Search, Document } from '@element-plus/icons-vue'
import type { MaterialType } from '../../../types/common'
import { getCorrectPdfViewerUrl } from '../../../utils/pdfHelpers'

import { useMaterialForm } from '../../../composables/useMaterialForm'
import { useMaterialStore } from '../../../stores/materialStore'

// 使用Store
const materialStore = useMaterialStore()

// 使用表单逻辑组合式函数
const formStore = useMaterialForm()

// 对话框状态
const showDialog = ref(false)
const currentFormMode = ref<'add' | 'edit'>('add')

// 监听参数值变化
const handleParamValueChange = () => {
  // 参数值变化时自动更新代码和名称（新增和编辑模式都更新）
  formStore.autoFillMaterialCode(materialStore.categories, materialStore.params);
  formStore.autoFillMaterialName(materialStore.categories, materialStore.params);
}

// 搜索处理
const handleSearch = () => {
  materialStore.setSearchQuery(materialStore.searchQuery)
}

// 选择类别变更时获取参数
const onCategoryChange = async (categoryId: number) => {
  // 清空参数值
  formStore.form.paramValues = {}

  if (categoryId) {
    // 找到选中的类别
    const selectedCategory = materialStore.categories.find(cat => cat.id === categoryId);

    // 如果类别有默认单位，自动填充单位
    if (selectedCategory && selectedCategory.unit) {
      formStore.form.unit = selectedCategory.unit;
      console.log(`自动设置单位ID: ${selectedCategory.unit}`);
    }

    await materialStore.fetchCategoryParams(categoryId)

    // 如果是新增模式（ID为空），自动生成代码和名称
    if (!formStore.form.id) {
      formStore.autoFillMaterialCode(materialStore.categories, materialStore.params);
      formStore.autoFillMaterialName(materialStore.categories, materialStore.params);
    }
  }
}

// 对话框操作
const openAddDialog = () => {
  formStore.resetForm()
  currentFormMode.value = 'add'
  showDialog.value = true
}

const openEditDialog = async (material: MaterialType) => {
  formStore.resetForm()

  // 如果有category，先获取参数
  if (material.category) {
    await materialStore.fetchCategoryParams(material.category)
  }

  formStore.fillForm(material)
  currentFormMode.value = 'edit'
  showDialog.value = true
}

const closeDialog = () => {
  showDialog.value = false
}

// 保存物料
const saveMaterial = async () => {
  try {
    if (currentFormMode.value === 'add') {
      await materialStore.createMaterial(formStore.form)
      ElMessage.success('添加物料成功')
    } else {
      if (!formStore.form.id) return
      await materialStore.updateMaterial(formStore.form.id, formStore.form)
      ElMessage.success('更新物料成功')
    }
    closeDialog()
  } catch (error: any) {
    const errorMsg = materialStore.handleApiError(error, '保存物料失败')
    ElMessage.error(errorMsg)
  }
}

// 删除物料
const confirmDelete = (material: MaterialType) => {
  ElMessageBox.confirm(
    `确定要删除物料 "${material.name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await materialStore.deleteMaterial(material.id)
      ElMessage.success('删除物料成功')
    } catch (error: any) {
      const errorMsg = materialStore.handleApiError(error, '删除物料失败')
      ElMessage.error(errorMsg)
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 导入物料
const beforeImport = (file: File) => {
  const validExtensions = ['.xlsx', '.xls', '.csv']
  const fileName = file.name
  const extension = fileName.slice(fileName.lastIndexOf('.'))

  if (!validExtensions.includes(extension)) {
    ElMessage.error('仅支持Excel或CSV文件导入')
    return false
  }

  return true
}

const handleImport = async (options: any) => {
  try {
    await materialStore.importMaterial(options.file)
    ElMessage.success('导入物料成功')
  } catch (error: any) {
    const errorMsg = materialStore.handleApiError(error, '导入失败')
    ElMessage.error(errorMsg)
  }
}

// 页面初始化
onMounted(async () => {
  await materialStore.initialize()
})

const MaterialFormDialog = defineAsyncComponent(() => import('../../../components/basedata/MaterialFormDialog.vue'))
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.material-container {
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 12px;
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
    margin-top: 24px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
