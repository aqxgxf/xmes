<template>
  <div class="process-code-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工艺流程代码管理</h2>
          <div class="search-actions">
            <el-input v-model="processCodeStore.search" placeholder="搜索代码/说明/版本" clearable @input="handleSearchInput" @clear="handleSearchClear">
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
        <el-table-column prop="created_at" label="创建时间" min-width="160" :formatter="formatDateTime" />
        <el-table-column prop="updated_at" label="更新时间" min-width="160" :formatter="formatDateTime" />
        <el-table-column prop="process_pdf" label="工艺文件">
          <template #default="{ row }">
            <el-link v-if="row.process_pdf" :href="getCorrectPdfViewerUrl(row.process_pdf)"
              target="_blank" type="primary">
              <el-icon>
                <Document />
              </el-icon> 查看
            </el-link>
            <span v-else>-</span>
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
      :form="formStore.form" :rules="formStore.rules" :categories="processCodeStore.categories" :pdf-files="formStore.pdfFileList.value" @save="handleSaveProcessCode"
      @close="closeAddDialog" @category-change="formStore.handleCategoryChange" @version-change="formStore.handleVersionChange"
      :form-ref="formStore.formRef" />

    <!-- 编辑工艺流程代码对话框 -->
    <process-code-form-dialog :visible="showEditDialog" @update:visible="showEditDialog = $event" title="编辑工艺流程代码" :loading="processCodeStore.submitting"
      :form="formStore.form" :rules="formStore.rules" :categories="processCodeStore.categories" :pdf-files="formStore.pdfFileList.value"
      @save="handleUpdateProcessCode" @close="closeEditDialog" @category-change="formStore.handleCategoryChange"
      @version-change="formStore.handleVersionChange" @opened="onEditDialogOpened" :form-ref="formStore.formRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
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
import { getCorrectPdfViewerUrl } from '../../../utils/pdfHelpers'

// 使用 Store
const processCodeStore = useProcessCodeStore()

// 使用表单逻辑组合式函数
const formStore = useProcessCodeForm()

// 对话框状态
const showAddDialog = ref(false)
const showEditDialog = ref(false)

// 使用路由
const router = useRouter()

// 搜索处理
const handleSearchInput = (value: string) => {
  processCodeStore.currentPage = 1
  processCodeStore.fetchProcessCodes()
}

const handleSearchClear = () => {
  processCodeStore.search = ''
  processCodeStore.currentPage = 1
  processCodeStore.fetchProcessCodes()
}

// 对话框操作
const openAddDialog = async () => {
  console.log('openAddDialog called')
  formStore.resetForm()
  if (processCodeStore.categories.length === 0) {
    await processCodeStore.fetchCategories()
  }
  showAddDialog.value = true
  console.log('showAddDialog.value set to', showAddDialog.value)
  await nextTick()
  console.log('After nextTick')
}

const closeAddDialog = () => {
  showAddDialog.value = false
  formStore.resetForm()
}

const openEditDialog = async (row: ProcessCode) => {
  console.log('[openEditDialog] 点击编辑，row:', row)
  formStore.resetForm()
  try {
    // 通过store获取完整的工艺流程代码数据（包括关联关系）
    const processCodeDetails = await processCodeStore.getProcessCodeDetails(Number(row.id))
    console.log('[openEditDialog] 获取到的工艺流程代码完整数据:', processCodeDetails)
    // 使用 formStore 的 fillForm 方法填充表单，确保传递的是一个新对象
    formStore.fillForm({ ...processCodeDetails })
    console.log('[openEditDialog] 填充后formStore.form:', JSON.parse(JSON.stringify(formStore.form)))
    if (processCodeStore.categories.length === 0) {
      await processCodeStore.fetchCategories()
    }
    showEditDialog.value = true // 数据填充后再显示弹窗
    console.log('[openEditDialog] showEditDialog.value =', showEditDialog.value)
  } catch (error) {
    console.error('打开编辑对话框失败:', error)
    ElMessage.error('获取工艺流程代码数据失败')
  }
}

const onEditDialogOpened = async () => {
  // 确保产品类数据已加载完成（在 initialize 或 fetchProcessCodes 中处理）
  if (processCodeStore.categories.length === 0) {
    await processCodeStore.fetchCategories()
  }
}

const closeEditDialog = () => {
  showEditDialog.value = false
  formStore.resetForm()
}

// 保存工艺流程代码
const handleSaveProcessCode = async () => {
  console.log('handleSaveProcessCode called')
  // 验证表单
  console.log('before validateForm', formStore)
  const valid = await formStore.validateForm()
  console.log('after validateForm, valid:', valid)
  if (!valid) {
    console.log('表单校验未通过，当前表单内容:', JSON.parse(JSON.stringify(formStore.form)))
    return
  }

  try {
    // 使用 formStore 的 prepareFormData 方法准备数据
    const formData = formStore.prepareFormData()
    console.log('准备提交的formData:', formData)
    await processCodeStore.createProcessCode(formData)
    ElMessage.success('新增工艺流程代码成功')
    closeAddDialog()
  } catch (error: any) {
    console.error('保存工艺流程代码异常:', error)
    const errorMsg = processCodeStore.handleApiError(error, '保存工艺流程代码失败')
    ElMessage.error(errorMsg)
  }
}

// 更新工艺流程代码
const handleUpdateProcessCode = async () => {
  if (!formStore.form.id) return

  // 验证表单
  const valid = await formStore.validateForm()
  if (!valid) return

  try {
    // 使用 formStore 的 prepareFormData 方法准备数据
    const formData = formStore.prepareFormData()
    await processCodeStore.updateProcessCode(formStore.form.id, formData)
    ElMessage.success('更新工艺流程代码成功')
    closeEditDialog()
  } catch (error: any) {
    const errorMsg = processCodeStore.handleApiError(error, '更新工艺流程代码失败')
    ElMessage.error(errorMsg)
  }
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
      await processCodeStore.deleteProcessCode(Number(row.id))
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

// 本地实现 formatDateTime
function formatDateTime(row: any, column: any, cellValue: string) {
  if (!cellValue) return '-';
  return String(cellValue).replace('T', ' ').slice(0, 19);
}
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
