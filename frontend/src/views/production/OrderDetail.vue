<template>
  <BasePage
    title="生产订单详情"
    :subtitle="'订单编号: ' + (currentOrder?.order_number || '')"
    :loading="productionStore.isLoading"
    :error="productionStore.error ?? undefined"
  >
    <template #page-actions>
      <el-button @click="goBack">
        <el-icon><Back /></el-icon> 返回
      </el-button>
      <el-button type="primary" @click="handleEdit" :disabled="!currentOrder">
        <el-icon><Edit /></el-icon> 编辑
      </el-button>
      <el-button type="danger" @click="handleDelete" :disabled="!currentOrder">
        <el-icon><Delete /></el-icon> 删除
      </el-button>
    </template>
    
    <DetailView
      title="基本信息"
      :data="currentOrder ?? undefined"
      :loading="productionStore.isLoading"
      :error="productionStore.error ?? undefined"
      :column="2"
    >
      <el-descriptions-item label="订单编号">{{ currentOrder?.order_number }}</el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ formatDateTime(currentOrder?.created_at) }}</el-descriptions-item>
      <el-descriptions-item label="产品名称">{{ currentOrder?.product_name }}</el-descriptions-item>
      <el-descriptions-item label="客户名称">{{ currentOrder?.customer_name }}</el-descriptions-item>
      <el-descriptions-item label="数量">{{ currentOrder?.quantity }}</el-descriptions-item>
      <el-descriptions-item label="交付日期">{{ formatDate(currentOrder?.delivery_date) }}</el-descriptions-item>
      <el-descriptions-item label="状态" :span="2">
        <el-tag :type="productionStore.getStatusType(currentOrder?.status || '')">
          {{ productionStore.getStatusLabel(currentOrder?.status || '') }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="备注" :span="2">
        {{ currentOrder?.notes || '无' }}
      </el-descriptions-item>
      
      <template #extra>
        <div v-if="currentOrder?.materials?.length" class="materials-section">
          <h3>原材料清单</h3>
          <el-table :data="currentOrder.materials" border stripe style="width: 100%">
            <el-table-column prop="material_name" label="材料名称" />
            <el-table-column prop="specification" label="规格" />
            <el-table-column prop="quantity" label="数量" width="100" align="right" />
            <el-table-column prop="unit" label="单位" width="80" />
          </el-table>
        </div>
        
        <div v-if="currentOrder?.production_logs?.length" class="logs-section">
          <h3>生产记录</h3>
          <el-timeline>
            <el-timeline-item
              v-for="log in currentOrder.production_logs"
              :key="log.id"
              :timestamp="formatDateTime(log.created_at)"
              :type="getTimelineItemType(log.type)"
            >
              <h4>{{ log.title }}</h4>
              <p>{{ log.content }}</p>
              <p v-if="log.operator">操作人: {{ log.operator }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </template>
    </DetailView>
  </BasePage>
  
  <!-- Delete confirmation dialog -->
  <el-dialog
    v-model="deleteDialogVisible"
    title="确认删除"
    width="400px"
  >
    <p>确定要删除这个生产订单吗？此操作不可撤销。</p>
    <template #footer>
      <el-button @click="deleteDialogVisible = false">取消</el-button>
      <el-button type="danger" :loading="deleting" @click="confirmDelete">确认删除</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Back, Edit, Delete } from '@element-plus/icons-vue'
import BasePage from '../../components/layout/BasePage.vue'
import DetailView from '../../components/common/DetailView.vue'
import { useProductionStore } from '../../stores/production'
import type { ProductionOrder } from '../../stores/production'
import notification from '../../utils/notification'
import { formatDate, formatDateTime } from '../../utils/dateFormatter'

const route = useRoute()
const router = useRouter()
const productionStore = useProductionStore()

// Local state
const deleteDialogVisible = ref(false)
const deleting = ref(false)

// Get current order from store
const currentOrder = computed(() => productionStore.currentOrder)

// Get order ID from route
const orderId = computed(() => {
  const id = route.params.id
  return typeof id === 'string' ? parseInt(id, 10) : 0
})

// Load order details on mount
onMounted(async () => {
  if (orderId.value) {
    try {
      await productionStore.fetchOrderDetail(orderId.value)
      
      // 如果订单不存在
      if (!productionStore.currentOrder && !productionStore.isLoading) {
        notification.error('找不到该订单')
        router.push('/production/orders')
      }
    } catch (error) {
      notification.error('加载订单数据失败')
      console.error('Failed to load order:', error)
    }
  }
})

// Navigation
function goBack() {
  router.push('/production/orders')
}

// Edit order
function handleEdit() {
  if (currentOrder.value) {
    router.push(`/production/orders/${orderId.value}/edit`)
  }
}

// Delete order
function handleDelete() {
  deleteDialogVisible.value = true
}

// Confirm delete
async function confirmDelete() {
  if (!orderId.value) return
  
  deleting.value = true
  
  try {
    await productionStore.deleteOrder(orderId.value)
    notification.success('生产订单已成功删除')
    router.push('/production/orders')
  } catch (error) {
    console.error('Delete error:', error)
    notification.error('删除失败，请重试')
  } finally {
    deleting.value = false
    deleteDialogVisible.value = false
  }
}

// Helper functions
function getTimelineItemType(logType?: string) {
  if (!logType) return 'primary'
  
  const typeMap: Record<string, string> = {
    'info': 'primary',
    'warning': 'warning',
    'error': 'danger',
    'success': 'success'
  }
  
  return typeMap[logType] || 'primary'
}
</script>

<style scoped>
.materials-section,
.logs-section {
  margin-top: 24px;
}

.materials-section h3,
.logs-section h3 {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}
</style> 