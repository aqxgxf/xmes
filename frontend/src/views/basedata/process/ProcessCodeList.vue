<template>
  <div class="process-code-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工艺流程代码管理</h2>
          <div class="search-actions">
            <el-input v-model="processCodeStore.search" placeholder="搜索代码/说明/版本" clearable @input="handleSearch">
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="openAddDialog">
              <el-icon>
                <Plus />
              </el-icon> 新增工艺流程代码
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table :data="processCodeStore.filteredProcessCodes" v-loading="processCodeStore.loading" border stripe
        style="width: 100%">
        <el-table-column prop="code" label="工艺流程代码" min-width="180" />
        <el-table-column prop="description" label="说明" min-width="200" />
        <el-table-column prop="version" label="版本" min-width="80" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column prop="updated_at" label="更新时间" min-width="160" />
        <el-table-column label="工艺PDF" width="120" align="center">
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
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" @click="openEditDialog(row)">
                <el-icon>
                  <Edit />
                </el-icon> 编辑
              </el-button>
              <el-button size="small" type="success" @click="viewDetails(row)">
                <el-icon>
                  <View />
                </el-icon> 工序明细
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
          :current-page="processCodeStore.currentPage" 
          :page-size="processCodeStore.pageSize"
          :page-sizes="[10, 20, 50, 100]" 
          layout="total, sizes, prev, pager, next, jumper"
          :total="processCodeStore.total" 
          @size-change="processCodeStore.handleSizeChange"
          @current-change="processCodeStore.handleCurrentChange"
          background 
        />
      </div>
    </el-card>

    <!-- 新增工艺流程代码对话框 -->
    <process-code-form-dialog :visible="showAddDialog" @update:visible="showAddDialog = $event" title="新增工艺流程代码" :loading="processCodeStore.submitting"
      :form="form" :rules="rules" :categories="processCodeStore.categories" :pdf-files="pdfFileList" @save="saveProcessCode"
      @close="closeAddDialog" @category-change="handleCategoryChange" @version-change="handleVersionChange"
      @update:pdf-files="handlePdfFilesUpdate" />

    <!-- 编辑工艺流程代码对话框 -->
    <process-code-form-dialog :visible="showEditDialog" @update:visible="showEditDialog = $event" title="编辑工艺流程代码" :loading="processCodeStore.submitting"
      :form="form" :rules="rules" :categories="processCodeStore.categories" :pdf-files="pdfFileList"
      @save="updateProcessCode" @close="closeEditDialog" @category-change="handleCategoryChange"
      @version-change="handleVersionChange" @opened="onEditDialogOpened" @update:pdf-files="handlePdfFilesUpdate" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, Document, View } from '@element-plus/icons-vue'
import { useProcessCodeForm } from '../../../composables/useProcessCodeForm'
import { useProcessCodeStore } from '../../../stores/processCodeStore'
import api from '../../../api'
// @ts-ignore - Vue SFC没有默认导出，但在Vue项目中可以正常使用
import ProcessCodeFormDialog from '../../../components/basedata/ProcessCodeFormDialog.vue'
import type { ProcessCode } from '../../../types/common'
import type { UploadUserFile } from 'element-plus'
import { useRouter } from 'vue-router'

// 使用 Store
const processCodeStore = useProcessCodeStore()

// 使用表单逻辑组合式函数
const formStore = useProcessCodeForm()
const { form, rules, pdfFileList, resetForm, updateCodeByProductAndVersion } = formStore

// 对话框状态
const showAddDialog = ref(false)
const showEditDialog = ref(false)

// 使用路由
const router = useRouter()

// 搜索处理
const handleSearch = () => {
  processCodeStore.currentPage = 1
  if (processCodeStore.search === '') {
    processCodeStore.fetchProcessCodes()
  }
}

// 处理产品类和版本变更，更新代码
const handleCategoryChange = (categoryId: number) => {
  // 使用产品类和版本更新代码
  updateCodeByProductAndVersion(processCodeStore.categories)
}

const handleVersionChange = () => {
  updateCodeByProductAndVersion(processCodeStore.categories)
}

// 处理PDF文件列表更新
const handlePdfFilesUpdate = (files: UploadUserFile[]) => {
  pdfFileList.value = files
}

// 对话框操作
const openAddDialog = () => {
  resetForm()
  showAddDialog.value = true
}

const closeAddDialog = () => {
  showAddDialog.value = false
}

const openEditDialog = async (row: ProcessCode) => {
  resetForm()

  try {
    // 通过store获取完整的工艺流程代码数据（包括关联关系）
    const processCodeDetails = await processCodeStore.getProcessCodeDetails(row.id)
    console.log('获取到的工艺流程代码完整数据:', processCodeDetails)
    
    // 设置表单数据
    form.id = processCodeDetails.id
    form.code = processCodeDetails.code
    form.description = processCodeDetails.description
    form.version = processCodeDetails.version
    form.process_pdf = processCodeDetails.process_pdf

    // 设置产品类别
    if (processCodeDetails.category) {
      form.category = Number(processCodeDetails.category)
    } else {
      form.category = null
    }
    
    showEditDialog.value = true
  } catch (error) {
    console.error('打开编辑对话框失败:', error)
    ElMessage.error('获取工艺流程代码数据失败')
  }
}

const onEditDialogOpened = async () => {
  // 确保产品类和产品数据已加载完成
  if (processCodeStore.categories.length === 0) {
    await processCodeStore.fetchCategories()
  }
  
  // 调试
  console.log('当前表单数据:', form)
  console.log('可用产品类别:', processCodeStore.categories)
  
  // 更新代码
  updateCodeByProductAndVersion(processCodeStore.categories)
}

const closeEditDialog = () => {
  showEditDialog.value = false
}

// 保存工艺流程代码
const saveProcessCode = async () => {
  try {
    // 确保表单数据类型一致
    form.category = form.category ? Number(form.category) : null
    
    const formData = prepareFormData()
    await processCodeStore.createProcessCode(formData)
    ElMessage.success('新增工艺流程代码成功')
    closeAddDialog()
  } catch (error: any) {
    const errorMsg = processCodeStore.handleApiError(error, '保存工艺流程代码失败')
    ElMessage.error(errorMsg)
  }
}

const updateProcessCode = async () => {
  if (!form.id) return

  try {
    // 确保表单数据类型一致
    form.category = form.category ? Number(form.category) : null
    
    const formData = prepareFormData()
    await processCodeStore.updateProcessCode(form.id, formData)
    ElMessage.success('更新工艺流程代码成功')
    closeEditDialog()
  } catch (error: any) {
    const errorMsg = processCodeStore.handleApiError(error, '更新工艺流程代码失败')
    ElMessage.error(errorMsg)
  }
}

// 准备表单数据
const prepareFormData = () => {
  const formData = new FormData()
  formData.append('code', form.code)
  formData.append('description', form.description)
  formData.append('version', form.version)

  if (form.category) {
    formData.append('category', String(form.category))
  }

  if (pdfFileList.value.length > 0 && pdfFileList.value[0].raw) {
    formData.append('process_pdf', pdfFileList.value[0].raw)
  }

  return formData
}

// 删除工艺流程代码
const confirmDelete = (row: ProcessCode) => {
  ElMessageBox.confirm(
    `确定要删除工艺流程代码 "${row.code}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await processCodeStore.deleteProcessCode(row.id)
      ElMessage.success('删除工艺流程代码成功')
    } catch (error: any) {
      const errorMsg = processCodeStore.handleApiError(error, '删除工艺流程代码失败')
      ElMessage.error(errorMsg)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 查看工艺流程明细
const viewDetails = (row: ProcessCode) => {
  router.push(`/process-details/${row.id}`)
}

// 页面初始化
onMounted(() => {
  processCodeStore.initialize()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.process-code-container {
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

  .action-buttons {
    display: flex;
    gap: 8px;
  }

  .no-file {
    color: var(--el-text-color-secondary);
  }

  .pagination-container {
    margin-top: 24px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>

<script lang="ts">
export default {
  name: 'ProcessCodeList'
}
</script>
