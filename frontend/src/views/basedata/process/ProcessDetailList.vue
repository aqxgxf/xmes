<template>
  <div class="process-detail-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工艺流程明细</h2>
          <div class="actions">
            <el-button type="primary" @click="$router.push('/process-codes')">
              <el-icon>
                <Back />
              </el-icon> 返回工艺流程列表
            </el-button>
            <el-button type="success" @click="openAddDetailDialog" v-if="processDetailStore.processCode.id">
              <el-icon>
                <Plus />
              </el-icon> 添加工序
            </el-button>
          </div>
        </div>
      </template>

      <!-- 工艺流程代码信息 -->
      <el-descriptions :column="3" border v-if="processDetailStore.processCode.id" class="process-code-info">
        <el-descriptions-item label="工艺流程代码">{{ processDetailStore.processCode.code }}</el-descriptions-item>
        <el-descriptions-item label="说明">{{ processDetailStore.processCode.description }}</el-descriptions-item>
        <el-descriptions-item label="版本">{{ processDetailStore.processCode.version }}</el-descriptions-item>
      </el-descriptions>

      <!-- 工艺流程明细表格 -->
      <div class="table-container">
        <el-table :data="processDetailStore.sortedProcessDetails" v-loading="processDetailStore.loading" border stripe
          style="width: 100%">
          <el-table-column prop="step_no" label="步骤" width="80" />
          <el-table-column prop="step_name" label="工序" min-width="150" />
          <el-table-column prop="machine_time" label="设备时间(分钟)" min-width="120" />
          <el-table-column prop="labor_time" label="人工时间(分钟)" min-width="120" />
          <el-table-column prop="required_equipment" label="所需设备" min-width="150" />
          <el-table-column prop="remark" label="备注" min-width="200" />
          <el-table-column label="操作" fixed="right" min-width="160">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" type="primary" @click="openEditDetailDialog(row)">
                  <el-icon>
                    <Edit />
                  </el-icon> 编辑
                </el-button>
                <el-button size="small" type="danger" @click="confirmDeleteDetail(row)">
                  <el-icon>
                    <Delete />
                  </el-icon> 删除
                </el-button>
              </div>
            </template>
          </el-table-column>

          <template #empty>
            <div class="empty-data-container">
              <el-empty description="暂无工艺流程明细数据" :image-size="100">
                <el-button type="primary" @click="openAddDetailDialog" v-if="processDetailStore.processCode.id">
                  <el-icon>
                    <Plus />
                  </el-icon> 添加第一道工序
                </el-button>
              </el-empty>
            </div>
          </template>
        </el-table>
      </div>
    </el-card>

    <!-- 工艺流程明细表单对话框 -->
    <process-detail-form-dialog v-model:visible="showDetailDialog"
      :title="currentFormMode === 'add' ? '添加工艺流程明细' : '编辑工艺流程明细'" :loading="processDetailStore.submitting"
      :form="formStore.form" :rules="formStore.rules" :processes="processDetailStore.processes" @save="saveDetail"
      @close="closeDetailDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Back } from '@element-plus/icons-vue'
import { useProcessDetailStore } from '../../../stores/processDetailStore'
import { useProcessDetailForm } from '../../../composables/useProcessDetailForm'
import ProcessDetailFormDialog from '../../../components/basedata/ProcessDetailFormDialog.vue'
import type { ProcessDetail } from '../../../types/common'

// 获取路由参数
const route = useRoute()
const router = useRouter()
const codeId = route.params.id ? Number(route.params.id) : null

// 使用Store
const processDetailStore = useProcessDetailStore()

// 使用表单逻辑组合式函数
const formStore = useProcessDetailForm(codeId || 0)

// 对话框状态
const showDetailDialog = ref(false)
const currentFormMode = ref<'add' | 'edit'>('add')

// 添加工艺流程明细
const openAddDetailDialog = () => {
  formStore.resetForm()
  currentFormMode.value = 'add'
  showDetailDialog.value = true
}

// 编辑工艺流程明细
const openEditDetailDialog = (detail: ProcessDetail) => {
  formStore.fillForm(detail)
  currentFormMode.value = 'edit'
  showDetailDialog.value = true
}

// 关闭对话框
const closeDetailDialog = () => {
  showDetailDialog.value = false
}

// 保存工艺流程明细
const saveDetail = async () => {
  try {
    if (currentFormMode.value === 'add') {
      await processDetailStore.createProcessDetail(formStore.form as unknown as ProcessDetail)
      ElMessage.success('添加工艺流程明细成功')
    } else {
      if (!formStore.form.id) return
      await processDetailStore.updateProcessDetail(formStore.form.id, formStore.form as unknown as ProcessDetail)
      ElMessage.success('更新工艺流程明细成功')
    }

    closeDetailDialog()
  } catch (error: any) {
    const errorMsg = processDetailStore.handleApiError(error, '保存工艺流程明细失败')
    ElMessage.error(errorMsg)
  }
}

// 删除工艺流程明细
const confirmDeleteDetail = (detail: ProcessDetail) => {
  ElMessageBox.confirm(
    `确定要删除该工艺流程明细吗？此操作不可恢复。`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  ).then(async () => {
    try {
      if (!detail.id) return
      await processDetailStore.deleteProcessDetail(detail.id)
      ElMessage.success('删除工艺流程明细成功')
    } catch (error: any) {
      const errorMsg = processDetailStore.handleApiError(error, '删除工艺流程明细失败')
      ElMessage.error(errorMsg)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 检查是否有有效的codeId
onMounted(() => {
  if (!codeId || isNaN(codeId)) {
    ElMessage.error('无效的工艺流程代码ID')
    router.push('/process-codes')
    return
  }

  processDetailStore.initialize(codeId)
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.process-detail-container {
  .process-code-info {
    margin-bottom: 20px;
  }

  .table-container {
    margin-top: 20px;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }

  .actions {
    display: flex;
    gap: 10px;
  }

  .empty-data-container {
    padding: 30px 0;

    :deep(.el-empty__description) {
      margin-top: 10px;
      margin-bottom: 20px;
    }
  }
}
</style>
