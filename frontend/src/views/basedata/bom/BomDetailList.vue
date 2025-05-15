<template>
  <div class="bom-detail-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">BOM明细管理</h2>
          <div class="search-actions">
            <el-select v-model="bomDetailStore.searchBom" filterable clearable placeholder="筛选BOM" class="bom-filter"
              @change="handleBomFilterChange">
              <el-option v-for="item in bomDetailStore.boms" :key="item.id"
                :label="`${item.name} (v${item.version}) ${item.product_name || ''}`" :value="item.id" />
            </el-select>
            <el-button type="primary" @click="openAddDialog">
              <el-icon>
                <Plus />
              </el-icon> 新增明细
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
      <el-table :data="bomDetailStore.bomDetails" v-loading="bomDetailStore.loading" border stripe style="width: 100%">
        <el-table-column prop="bom_name" label="BOM" min-width="160" />
        <el-table-column prop="material_name" label="物料" min-width="120" />
        <el-table-column prop="quantity" label="用量" min-width="100" align="center" />
        <el-table-column prop="remark" label="备注" min-width="200" />
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
        <el-pagination v-model:current-page="bomDetailStore.currentPage" v-model:page-size="bomDetailStore.pageSize"
          :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" :total="bomDetailStore.total"
          @size-change="bomDetailStore.handleSizeChange" @current-change="bomDetailStore.handleCurrentChange"
          background />
      </div>
    </el-card>

    <!-- BOM明细表单对话框 -->
    <bom-detail-form-dialog v-model:visible="showDialog" :title="currentFormMode === 'add' ? '新增BOM明细' : '编辑BOM明细'"
      :loading="bomDetailStore.submitting" :form="formStore.form" :rules="formStore.rules" :boms="bomDetailStore.boms"
      :materials="bomDetailStore.materials" @save="saveBomDetail" @close="closeDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Upload } from '@element-plus/icons-vue'
import { useBomDetailStore } from '../../../stores/bomDetailStore'
import { useBomDetailForm } from '../../../composables/useBomDetailForm'
import BomDetailFormDialog from '../../../components/basedata/BomDetailFormDialog.vue'
import type { BomDetail } from '../../../types/common'

// 获取Store
const bomDetailStore = useBomDetailStore()

// 使用表单逻辑组合式函数
const formStore = useBomDetailForm(bomDetailStore.searchBom)

// 对话框状态
const showDialog = ref(false)
const currentFormMode = ref<'add' | 'edit'>('add')

// 添加BOM明细
const openAddDialog = () => {
  formStore.resetForm(bomDetailStore.searchBom)
  currentFormMode.value = 'add'
  showDialog.value = true
}

// 编辑BOM明细
const openEditDialog = (detail: BomDetail) => {
  formStore.fillForm(detail)
  currentFormMode.value = 'edit'
  showDialog.value = true
}

// 关闭对话框
const closeDialog = () => {
  showDialog.value = false
}

// 保存BOM明细
const saveBomDetail = async () => {
  try {
    if (currentFormMode.value === 'add') {
      await bomDetailStore.createBomDetail(formStore.form)
      ElMessage.success('添加BOM明细成功')
    } else {
      if (!formStore.form.id) return
      await bomDetailStore.updateBomDetail(formStore.form.id, formStore.form)
      ElMessage.success('更新BOM明细成功')
    }

    closeDialog()
  } catch (error: any) {
    const errorMsg = bomDetailStore.handleApiError(error, '保存BOM明细失败')
    ElMessage.error(errorMsg)
  }
}

// 确认删除
const confirmDelete = (row: BomDetail) => {
  if (!row.id) return

  ElMessageBox.confirm(
    '确定要删除该BOM明细吗？此操作不可撤销。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await bomDetailStore.deleteBomDetail(row.id)
      ElMessage.success('删除BOM明细成功')
    } catch (error: any) {
      const errorMsg = bomDetailStore.handleApiError(error, '删除BOM明细失败')
      ElMessage.error(errorMsg)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 处理BOM筛选变化
const handleBomFilterChange = () => {
  bomDetailStore.setBomFilter(bomDetailStore.searchBom)
}

// 导入相关
const beforeImport = (file: File) => {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!["xlsx", "xls", "csv"].includes(ext!)) {
    ElMessage.error('仅支持Excel或CSV文件')
    return false
  }
  return true
}

const handleImport = async (option: any) => {
  const formData = new FormData()
  formData.append('file', option.file)

  try {
    await bomDetailStore.importBomDetails(formData)
    ElMessage.success('导入成功')
  } catch (error: any) {
    const errorMsg = bomDetailStore.handleApiError(error, '导入失败')
    ElMessage.error(errorMsg)
  }
}

// 页面初始化
onMounted(() => {
  bomDetailStore.initialize()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.bom-detail-container {
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

  // Filter dropdown in header
  .bom-filter {
    width: 320px;
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
}
</style>
