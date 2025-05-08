<template>
  <BasePage
    title="生产订单管理"
    subtitle="查看和管理所有生产订单"
    :loading="productionStore.isLoading"
    :error="productionStore.error ?? undefined"
    has-table
  >
    <template #page-actions>
      <el-button type="primary" @click="handleCreateOrder">
        <el-icon><Plus /></el-icon> 新建订单
      </el-button>
    </template>
    
    <!-- Filter Form -->
    <div class="filter-form">
      <el-form :inline="true" :model="filters" class="filter-container">
        <!-- 订单状态过滤器 -->
        <el-form-item label="订单状态">
          <el-select
            v-model="filters.status"
            placeholder="选择状态"
            clearable
            style="width: 180px"
          >
            <el-option
              v-for="(value, key) in PRODUCTION_ORDER_STATUS"
              :key="key"
              :label="value.label"
              :value="key"
            />
          </el-select>
        </el-form-item>
        
        <!-- 日期范围过滤器 -->
        <el-form-item label="创建日期">
          <el-date-picker
            v-model="filters.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        
        <!-- 客户过滤器 -->
        <el-form-item label="客户">
          <el-select
            v-model="filters.customer_id"
            placeholder="选择客户"
            clearable
            style="width: 220px"
          >
            <el-option
              v-for="customer in basedataStore.customers"
              :key="customer.id"
              :label="customer.name"
              :value="customer.id"
            />
          </el-select>
        </el-form-item>
        
        <!-- 过期状态过滤器 -->
        <el-form-item label="交付状态">
          <el-select
            v-model="filters.delivery_status"
            placeholder="交付状态"
            clearable
            style="width: 160px"
          >
            <el-option label="已过期" value="expired" />
            <el-option label="未过期" value="not_expired" />
          </el-select>
        </el-form-item>
        
        <div class="filter-actions">
          <el-button type="primary" @click="handleFilterApply" :loading="productionStore.isLoading">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          
          <el-button @click="handleFilterReset" :disabled="productionStore.isLoading">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
          
          <el-button 
            :disabled="!selectedRows.length || productionStore.isLoading"
            @click="handleBatchDelete"
            type="danger"
          >
            <el-icon><Delete /></el-icon> 批量删除
          </el-button>
        </div>
      </el-form>
    </div>
    
    <DataTable
      :data="productionStore.productionOrders"
      :loading="productionStore.isLoading"
      :total="productionStore.totalCount"
      selectable
      show-index
      show-actions
      show-toolbar
      show-search
      search-placeholder="搜索订单编号或客户"
      :initial-page-size="pageSize"
      :initial-current-page="currentPage"
      @selection-change="handleSelectionChange"
      @page-change="handlePageChange"
      @size-change="handleSizeChange"
      @search="handleSearch"
      @sort-change="handleSortChange"
    >
      <!-- Table columns -->
      <el-table-column prop="order_number" label="订单编号" sortable width="140" />
      <el-table-column prop="product_name" label="产品名称" min-width="120" />
      <el-table-column prop="customer_name" label="客户名称" min-width="120" />
      <el-table-column prop="quantity" label="数量" width="100" align="right" sortable />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="productionStore.getStatusType(row.status)">
            {{ productionStore.getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" sortable />
      <el-table-column prop="delivery_date" label="交付日期" width="120" sortable />
      
      <!-- Row actions -->
      <template #row-actions="{ row }">
        <el-button-group>
          <el-button size="small" @click="handleViewOrder(row)">
            <el-icon><View /></el-icon>
          </el-button>
          <el-button size="small" type="primary" @click="handleEditOrder(row)">
            <el-icon><Edit /></el-icon>
          </el-button>
          <el-button size="small" type="danger" @click="handleDeleteOrder(row)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </el-button-group>
      </template>
    </DataTable>
  </BasePage>
  
  <!-- Create/Edit Dialog -->
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑生产订单' : '创建生产订单'"
    width="650px"
    @closed="resetForm"
  >
    <OrderForm
      v-model="orderForm"
      :loading="submitting"
      :products="basedataStore.products"
      :customers="basedataStore.customers"
      @submit="submitOrder"
    />
  </el-dialog>
  
  <!-- Delete confirmation dialog -->
  <el-dialog
    v-model="deleteDialogVisible"
    title="确认删除"
    width="400px"
  >
    <p>确定要删除这个生产订单吗？此操作不可撤销。</p>
    <template #footer>
      <el-button @click="deleteDialogVisible = false">取消</el-button>
      <el-button type="danger" :loading="deleting" @click="confirmDeleteOrder">确认删除</el-button>
    </template>
  </el-dialog>
  
  <!-- Batch Delete confirmation dialog -->
  <el-dialog
    v-model="batchDeleteDialogVisible"
    title="确认批量删除"
    width="400px"
  >
    <p>确定要删除选中的所有生产订单吗？此操作不可撤销。</p>
    <template #footer>
      <el-button @click="batchDeleteDialogVisible = false">取消</el-button>
      <el-button type="danger" :loading="batchDeleting" @click="confirmBatchDelete">确认删除</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Edit, Delete, View, Search, Refresh } from '@element-plus/icons-vue'
import BasePage from '../../components/layout/BasePage.vue'
import DataTable from '../../components/common/DataTable.vue'
import OrderForm from '../../components/production/OrderForm.vue'
import { useProductionStore, PRODUCTION_ORDER_STATUS } from '../../stores/production'
import type { ProductionOrder } from '../../stores/production'
import { useBasedataStore } from '../../stores/basedata'
import type { PaginationParams } from '../../types/common'
import notification from '../../utils/notification'
import { formatDate, formatDateTime, isExpired } from '../../utils/dateFormatter'
import { withApiErrorHandling } from '../../utils/apiErrorHandler'

const router = useRouter()
const productionStore = useProductionStore()
const basedataStore = useBasedataStore()

// Pagination
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const sortBy = ref('')
const sortOrder = ref('')

// Filters
const filters = reactive({
  status: '',
  date_range: [] as string[],
  customer_id: '',
  delivery_status: ''
})

// Dialog visibility
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const batchDeleteDialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const batchDeleting = ref(false)
const selectedOrderId = ref(0)

// Selected rows
const selectedRows = ref<ProductionOrder[]>([])

// Form data
const orderForm = reactive<{
  id: number | null;
  product_id: string | number;
  customer_id: string | number;
  quantity: number;
  delivery_date: string | Date;
  notes: string;
}>({
  id: null,
  product_id: '',
  customer_id: '',
  quantity: 1,
  delivery_date: '',
  notes: ''
})

// Load data on component mount
onMounted(async () => {
  try {
    // Load base data first
    await basedataStore.fetchAllBasedata()
    
    // Then load production orders
    await fetchOrders()
  } catch (error) {
    console.error('Failed to load data:', error)
    notification.error('加载数据失败')
  }
})

// Watch for changes in pagination parameters
watch([currentPage, pageSize, searchQuery, sortBy, sortOrder], () => {
  fetchOrders()
})

// Fetch production orders with enhanced error handling
const fetchOrders = withApiErrorHandling(async () => {
  const params: PaginationParams = {
    page: currentPage.value,
    page_size: pageSize.value
  }
  
  if (searchQuery.value) {
    params.search = searchQuery.value
  }
  
  if (sortBy.value && sortOrder.value) {
    params.ordering = sortOrder.value === 'descending' ? `-${sortBy.value}` : sortBy.value
  }
  
  // 添加过滤参数
  if (filters.status) {
    params.status = filters.status
  }
  
  if (filters.customer_id) {
    params.customer_id = filters.customer_id
  }
  
  if (filters.date_range && filters.date_range.length === 2) {
    params.created_after = filters.date_range[0]
    params.created_before = filters.date_range[1]
  }
  
  // 根据交付日期过滤
  if (filters.delivery_status) {
    const today = formatDate(new Date())
    if (filters.delivery_status === 'expired') {
      params.delivery_before = today
    } else if (filters.delivery_status === 'not_expired') {
      params.delivery_after = today
    }
  }
  
  return await productionStore.fetchProductionOrders(params)
}, {
  defaultMessage: '获取订单数据失败',
  rethrowError: false
})

// Handle events
function handleCreateOrder() {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

function handleEditOrder(row: ProductionOrder) {
  isEdit.value = true
  Object.assign(orderForm, {
    id: row.id,
    product_id: row.product_id,
    customer_id: row.customer_id,
    quantity: row.quantity,
    delivery_date: row.delivery_date,
    notes: row.notes || ''
  })
  dialogVisible.value = true
}

function handleViewOrder(row: ProductionOrder) {
  router.push(`/production/orders/${row.id}`)
}

async function handleDeleteOrder(row: ProductionOrder) {
  selectedOrderId.value = row.id
  deleteDialogVisible.value = true
}

function handleSelectionChange(rows: ProductionOrder[]) {
  selectedRows.value = rows
}

function handlePageChange(page: number) {
  currentPage.value = page
}

function handleSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1 // 重置到第一页
}

function handleSearch(query: string) {
  searchQuery.value = query
  currentPage.value = 1 // 重置到第一页
}

// Form submission
async function submitOrder() {
  submitting.value = true
  
  try {
    if (isEdit.value && orderForm.id) {
      const orderData = {
        id: orderForm.id,
        product_id: Number(orderForm.product_id),
        customer_id: Number(orderForm.customer_id),
        quantity: orderForm.quantity,
        delivery_date: orderForm.delivery_date,
        notes: orderForm.notes
      }
      await productionStore.updateOrder(orderForm.id, orderData)
      notification.success('生产订单更新成功')
    } else {
      const orderData = {
        product_id: Number(orderForm.product_id),
        customer_id: Number(orderForm.customer_id),
        quantity: orderForm.quantity,
        delivery_date: orderForm.delivery_date,
        notes: orderForm.notes,
        status: 'draft'
      }
      await productionStore.createOrder(orderData)
      notification.success('生产订单创建成功')
    }
    
    dialogVisible.value = false
    fetchOrders()
  } catch (error) {
    console.error('Order submission error:', error)
    notification.error('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

// Delete order
async function confirmDeleteOrder() {
  deleting.value = true
  
  try {
    await productionStore.deleteOrder(selectedOrderId.value)
    notification.success('生产订单已删除')
    deleteDialogVisible.value = false
    fetchOrders()
  } catch (error) {
    console.error('Delete error:', error)
    notification.error('删除失败，请重试')
  } finally {
    deleting.value = false
  }
}

// Reset form fields
function resetForm() {
  orderForm.id = null
  orderForm.product_id = ''
  orderForm.customer_id = ''
  orderForm.quantity = 1
  orderForm.delivery_date = ''
  orderForm.notes = ''
}

// 批量删除相关函数
function handleBatchDelete() {
  if (selectedRows.value.length === 0) return
  batchDeleteDialogVisible.value = true
}

async function confirmBatchDelete() {
  batchDeleting.value = true
  try {
    // 依次删除选中的订单
    for (const order of selectedRows.value) {
      await productionStore.deleteOrder(order.id)
    }
    notification.success(`成功删除 ${selectedRows.value.length} 个订单`)
    selectedRows.value = []
    batchDeleteDialogVisible.value = false
    await fetchOrders()
  } catch (error) {
    notification.error('批量删除失败')
    console.error('Batch delete error:', error)
  } finally {
    batchDeleting.value = false
  }
}

// 过滤器相关函数
function handleFilterApply() {
  currentPage.value = 1 // 重置到第一页
  fetchOrders()
}

function handleFilterReset() {
  // 重置所有过滤器
  filters.status = ''
  filters.date_range = []
  filters.customer_id = ''
  filters.delivery_status = ''
  
  // 重新获取数据
  currentPage.value = 1
  fetchOrders()
}

// 表格排序处理
function handleSortChange(column: { prop: string, order: string }) {
  if (column) {
    sortBy.value = column.prop
    sortOrder.value = column.order
  } else {
    sortBy.value = ''
    sortOrder.value = ''
  }
  fetchOrders()
}
</script>

<style scoped>
.filter-form {
  margin-bottom: 16px;
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
}

.filter-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.filter-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

:deep(.el-form-item) {
  margin-bottom: 10px;
  margin-right: 16px;
}

@media (max-width: 768px) {
  .filter-container {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-actions {
    margin-left: 0;
    margin-top: 12px;
    width: 100%;
    justify-content: flex-end;
  }
  
  :deep(.el-form-item) {
    margin-right: 0;
    width: 100%;
  }
}
</style> 