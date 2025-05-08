<template>
  <BasePage
    title="编辑生产订单"
    :subtitle="'订单编号: ' + (currentOrder?.order_number || '')"
    :loading="productionStore.isLoading"
    :error="productionStore.error ?? undefined"
  >
    <template #page-actions>
      <el-button @click="goBack">
        <el-icon><Back /></el-icon> 返回
      </el-button>
      <el-button type="primary" @click="handleSave" :disabled="!currentOrder || saving">
        <el-icon><Check /></el-icon> 保存
      </el-button>
    </template>
    
    <el-card v-if="currentOrder">
      <OrderForm
        v-model="orderForm"
        :loading="saving"
        :products="basedataStore.products"
        :customers="basedataStore.customers"
        @submit="saveOrder"
      />
    </el-card>
    
    <el-empty v-else-if="!productionStore.isLoading" description="未找到订单数据" />
  </BasePage>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Back, Check } from '@element-plus/icons-vue'
import BasePage from '../../components/layout/BasePage.vue'
import OrderForm from '../../components/production/OrderForm.vue'
import { useProductionStore } from '../../stores/production'
import type { ProductionOrder } from '../../stores/production'
import { useBasedataStore } from '../../stores/basedata'
import type { OrderFormData } from '../../components/production/OrderForm.vue'
import notification from '../../utils/notification'
import { formatDate } from '../../utils/dateFormatter'

const route = useRoute()
const router = useRouter()
const productionStore = useProductionStore()
const basedataStore = useBasedataStore()

// Local state
const saving = ref(false)

// Get current order from store
const currentOrder = computed(() => productionStore.currentOrder)

// Order form data
const orderForm = reactive<OrderFormData>({
  id: null,
  product_id: '',
  customer_id: '',
  quantity: 1,
  delivery_date: '',
  notes: ''
})

// Get order ID from route
const orderId = computed(() => {
  const id = route.params.id
  return typeof id === 'string' ? parseInt(id, 10) : 0
})

// Load order details and base data on mount
onMounted(async () => {
  try {
    // 加载基础数据
    await basedataStore.fetchAllBasedata()
    
    // 加载订单详情
    if (orderId.value) {
      await productionStore.fetchOrderDetail(orderId.value)
    }
    
    // 如果订单不存在，显示错误
    if (!productionStore.currentOrder && !productionStore.isLoading) {
      notification.error('未找到订单数据')
      router.push('/production/orders')
    }
  } catch (error) {
    console.error('Failed to load data:', error)
    notification.error('数据加载失败')
  }
})

// Watch for current order changes to update form
watch(currentOrder, (order) => {
  if (order) {
    // 复制订单数据到表单
    orderForm.id = order.id
    orderForm.product_id = order.product_id
    orderForm.customer_id = order.customer_id
    orderForm.quantity = order.quantity
    orderForm.delivery_date = formatDate(order.delivery_date)
    orderForm.notes = order.notes || ''
  }
}, { immediate: true })

// Navigation
function goBack() {
  router.push(`/production/orders/${orderId.value}`)
}

// Save button click handler
function handleSave() {
  if (!currentOrder.value) return
  saveOrder()
}

// Save order to backend
async function saveOrder() {
  if (!orderId.value || !orderForm.id) return
  
  saving.value = true
  
  try {
    const orderData = {
      id: orderForm.id,
      product_id: Number(orderForm.product_id),
      customer_id: Number(orderForm.customer_id),
      quantity: orderForm.quantity,
      delivery_date: orderForm.delivery_date,
      notes: orderForm.notes
    }
    
    await productionStore.updateOrder(orderId.value, orderData)
    notification.success('生产订单更新成功')
    router.push(`/production/orders/${orderId.value}`)
  } catch (error) {
    console.error('Update error:', error)
    notification.error(typeof error === 'string' ? error : '更新失败，请重试')
  } finally {
    saving.value = false
  }
}
</script> 