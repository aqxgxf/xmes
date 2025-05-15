<template>
  <div class="process-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工序管理</h2>
          <div class="search-actions">
            <el-input v-model="processStore.search" placeholder="搜索工序名称/代码" clearable @input="handleSearch">
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="openAddDialog">
              <el-icon>
                <Plus />
              </el-icon> 新增工序
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table :data="processStore.filteredProcesses" v-loading="processStore.loading" border stripe
        style="width: 100%">
        <el-table-column prop="code" label="工序代码" min-width="120" />
        <el-table-column prop="name" label="工序名称" min-width="180" />
        <el-table-column prop="description" label="工序描述" min-width="200" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column prop="updated_at" label="更新时间" min-width="160" />
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
        <el-pagination v-model:current-page="processStore.currentPage" v-model:page-size="processStore.pageSize"
          :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" :total="processStore.total"
          @size-change="processStore.handleSizeChange" @current-change="processStore.handleCurrentChange" background />
      </div>
    </el-card>

    <!-- 新增工序对话框 -->
    <process-form-dialog v-model:visible="showAddDialog" title="新增工序" :loading="processStore.submitting" :form="form"
      :rules="rules" @save="saveProcess" @close="closeAddDialog" />

    <!-- 编辑工序对话框 -->
    <process-form-dialog v-model:visible="showEditDialog" title="编辑工序" :loading="processStore.submitting" :form="form"
      :rules="rules" @save="updateProcess" @close="closeEditDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'
import { useProcessForm } from '../../../composables/useProcessForm'
import { useProcessStore } from '../../../stores/processStore'
import ProcessFormDialog from '../../../components/basedata/ProcessFormDialog.vue'
import type { Process } from '../../../types/common'

// 使用 Process Store
const processStore = useProcessStore()

// 使用表单组合式函数
const formStore = useProcessForm()
const { form, rules, resetForm } = formStore

// 对话框状态
const showAddDialog = ref(false)
const showEditDialog = ref(false)

// 搜索处理
const handleSearch = () => {
  processStore.currentPage = 1
  if (processStore.search === '') {
    processStore.fetchProcesses()
  }
}

// 对话框操作
const openAddDialog = () => {
  resetForm()
  showAddDialog.value = true
}

const closeAddDialog = () => {
  showAddDialog.value = false
}

const openEditDialog = (row: Process) => {
  resetForm()
  form.id = row.id
  form.code = row.code
  form.name = row.name
  form.description = row.description || ''
  showEditDialog.value = true
}

const closeEditDialog = () => {
  showEditDialog.value = false
}

// 保存工序
const saveProcess = async () => {
  try {
    await processStore.createProcess({
      ...form,
      id: null
    })
    ElMessage.success('添加工序成功')
    closeAddDialog()
  } catch (error: any) {
    const errorMsg = processStore.handleApiError(error, '添加工序失败')
    ElMessage.error(errorMsg)
  }
}

const updateProcess = async () => {
  if (!form.id) return

  try {
    await processStore.updateProcess(form.id, {
      ...form,
      id: form.id
    })
    ElMessage.success('更新工序成功')
    closeEditDialog()
  } catch (error: any) {
    const errorMsg = processStore.handleApiError(error, '更新工序失败')
    ElMessage.error(errorMsg)
  }
}

// 删除工序
const confirmDelete = (row: Process) => {
  ElMessageBox.confirm(
    `确定要删除工序 "${row.name}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await processStore.deleteProcess(row.id)
      ElMessage.success('删除工序成功')
    } catch (error: any) {
      const errorMsg = processStore.handleApiError(error, '删除工序失败')
      ElMessage.error(errorMsg)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 页面初始化
onMounted(() => {
  processStore.initialize()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.process-container {
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

  .pagination-container {
    margin-top: 24px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
