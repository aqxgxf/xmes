<template>
  <el-dialog v-model="visible" title="工单详情" width="700px" @close="onClose">
    <el-descriptions :column="2" border v-if="workOrder">
      <el-descriptions-item label="工单号">{{ workOrder.workorder_no }}</el-descriptions-item>
      <el-descriptions-item label="订单号">{{ workOrder.order }}</el-descriptions-item>
      <el-descriptions-item label="产品">{{ workOrder.product }}</el-descriptions-item>
      <el-descriptions-item label="数量">{{ workOrder.quantity }}</el-descriptions-item>
      <el-descriptions-item label="工艺流程">{{ workOrder.process_code }}</el-descriptions-item>
      <el-descriptions-item label="状态">{{ workOrder.status }}</el-descriptions-item>
      <el-descriptions-item label="计划开始">{{ workOrder.plan_start }}</el-descriptions-item>
      <el-descriptions-item label="计划结束">{{ workOrder.plan_end }}</el-descriptions-item>
      <el-descriptions-item label="备注">{{ workOrder.remark }}</el-descriptions-item>
    </el-descriptions>
    <div v-else style="text-align:center;padding:40px 0;">正在加载...</div>
    <template #footer>
      <el-button @click="onClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from 'vue'
import { useWorkOrderStore } from '../../stores/workOrderStore'

const props = defineProps<{ visible: boolean, workOrderId: number | null }>()
const emits = defineEmits(['update:visible'])
const workOrderStore = useWorkOrderStore()
const workOrder = ref<any>(null)

watch(() => props.workOrderId, async (id) => {
  if (id) {
    await workOrderStore.fetchOne(id)
    workOrder.value = workOrderStore.current
  }
}, { immediate: true })

const onClose = () => emits('update:visible', false)
</script>
