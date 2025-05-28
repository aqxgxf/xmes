<template>
  <div class="dashboard-bg">
    <!-- 欢迎头部在最上方，宽度与下方一致 -->
    <div class="welcome-header unified-width">
      <div class="welcome-title">
        欢迎使用 <img src="/logo.svg" class="inline-logo" /> XMes 智能制造执行系统
      </div>
      <div class="welcome-desc">高效 · 智能 · 可靠的生产管理平台</div>
    </div>
    <div class="dashboard-container unified-width">
      <div class="dashboard-cards-group">
        <el-row v-for="(row, rowIdx) in statRows" :key="rowIdx" :gutter="32" justify="center" class="dashboard-cards">
          <el-col v-for="(item, idx) in row" :key="idx" :span="4">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-icon" :style="{background: item.bg}">
                <el-icon :size="28"><component :is="item.icon" /></el-icon>
              </div>
              <div class="stat-title">{{ item.title }}</div>
              <div class="stat-value">{{ item.value }}</div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      <el-row :gutter="32" class="dashboard-charts">
        <el-col :span="12">
          <el-card shadow="hover" class="chart-card">
            <div class="chart-title">近7天订单金额趋势</div>
            <v-chart v-if="chartReady" ref="el => chartRefs.value[0] = el" :option="orderAmountTrendOption" autoresize style="height: 320px" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover" class="chart-card">
            <div class="chart-title">近7天工单数量趋势</div>
            <v-chart v-if="chartReady" ref="el => chartRefs.value[1] = el" :option="workOrderTrendOption" autoresize style="height: 320px" />
          </el-card>
        </el-col>
      </el-row>
      <el-row :gutter="32" class="dashboard-charts">
        <el-col :span="12">
          <el-card shadow="hover" class="chart-card">
            <div class="chart-title">订单状态分布</div>
            <v-chart v-if="chartReady" ref="el => chartRefs.value[2] = el" :option="orderStatusPieOption" autoresize style="height: 320px" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover" class="chart-card">
            <div class="chart-title">工单状态分布</div>
            <v-chart v-if="chartReady" ref="el => chartRefs.value[3] = el" :option="workOrderStatusPieOption" autoresize style="height: 320px" />
          </el-card>
        </el-col>
      </el-row>
      <div style="width:100%;display:flex;justify-content:center;margin:32px 0 0 0;">
        <el-button type="danger" @click="logout" class="logout-btn">退出登录</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useSalesStore } from '../stores/sales'
import { useWorkOrderStore } from '../stores/workOrderStore'
import { useProductStore } from '../stores/product'
import { useMaterialStore } from '../stores/materialStore'
import { useCompanyStore } from '../stores/companyStore'
import { useUserStore } from '../stores/user'
import { useCategoryStore } from '../stores/categoryStore'
import { useProcessStore } from '../stores/processStore'
import { useProcessCodeStore } from '../stores/processCodeStore'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { UserFilled, ShoppingCart, DataLine, HomeFilled, Tools } from '@element-plus/icons-vue'

const router = useRouter()

// 各store
const salesStore = useSalesStore()
const workOrderStore = useWorkOrderStore()
const productStore = useProductStore()
const materialStore = useMaterialStore()
const companyStore = useCompanyStore()
const userStore = useUserStore()
const categoryStore = useCategoryStore()
const processStore = useProcessStore()
const processCodeStore = useProcessCodeStore()

// Set to store IDs of orders without a linked work order
const ordersWithoutWorkOrderIdSet = ref(new Set<number>());

// Function to fetch IDs of orders without work orders
async function fetchOrdersWithoutWorkOrderIds() {
  try {
    const response = await axios.get('/api/orders-without-workorder/');
    const orders = response.data.results || response.data || []; // Adjust based on actual API response structure
    if (Array.isArray(orders)) {
      orders.forEach((order: any) => {
        if (order && typeof order.id === 'number') {
          ordersWithoutWorkOrderIdSet.value.add(order.id);
        }
      });
    }
    // console.log('[DEBUG] Fetched ordersWithoutWorkOrderIdSet:', ordersWithoutWorkOrderIdSet.value);
  } catch (error) {
    console.error('Failed to fetch orders without work order IDs:', error);
    // Handle error appropriately, maybe set a flag or log
  }
}

// 统计数据
const currentLocalDate = new Date();
const today = `${currentLocalDate.getFullYear()}-${(currentLocalDate.getMonth() + 1).toString().padStart(2, '0')}-${currentLocalDate.getDate().toString().padStart(2, '0')}`;
// console.log("[DEBUG] Today string:", today); // DEBUG

const todayOrderAmount = computed(() => 
  salesStore.salesOrders
    .filter(o => {
      // console.log("[DEBUG] Processing order for todayOrderAmount:", o); // DEBUG
      if (!o.order_date) {
        // console.log("[DEBUG] order_date is missing"); // DEBUG
        return false;
      }
      const orderDateObj = new Date(o.order_date);
      if (isNaN(orderDateObj.getTime())) {
        // console.warn(`[DEBUG] Invalid order_date encountered: ${o.order_date}`); // DEBUG
        return false;
      }

      const year = orderDateObj.getFullYear();
      const month = (orderDateObj.getMonth() + 1).toString().padStart(2, '0');
      const day = orderDateObj.getDate().toString().padStart(2, '0');
      const orderDateString = `${year}-${month}-${day}`;
      // console.log(`[DEBUG] order_date: ${o.order_date}, parsed orderDateString: ${orderDateString}, today: ${today}, isMatch: ${orderDateString === today}`); // DEBUG
      
      return orderDateString === today;
    })
    .reduce((sum, o) => {
      // console.log(`[DEBUG] Adding to todayOrderAmount: order_id=${o.id}, total_amount=${o.total_amount}`); // DEBUG
      return sum + (parseFloat(String(o.total_amount)) || 0); // Ensure numeric addition
    }, 0)
);
const totalOrderAmount = computed(() => 
  salesStore.salesOrders.reduce((sum, o) => {
    // console.log(`[DEBUG] Adding to totalOrderAmount: order_id=${o.id}, total_amount=${o.total_amount}`); // DEBUG
    return sum + (parseFloat(String(o.total_amount)) || 0); // Ensure numeric addition
  }, 0)
);
const todayWorkOrderCount = computed(() => workOrderStore.list.filter(w => (w.created_at || '').slice(0, 10) === today).length)
const totalWorkOrderCount = computed(() => workOrderStore.list.length)
const totalProductCount = computed(() => productStore.products.length)
const totalMaterialCount = computed(() => materialStore.materials.length)
const totalCustomerCount = computed(() => companyStore.companies.length)
const totalCategoryCount = computed(() => categoryStore.categories.length)
const totalProcessCount = computed(() => processStore.processes.length)
const totalProcessCodeCount = computed(() => processCodeStore.processCodes.length)

// 卡片数据结构
const statList = computed(() => [
  { title: '今日订单金额', value: `￥${todayOrderAmount.value.toFixed(2)}`, icon: ShoppingCart, bg: 'linear-gradient(135deg,#e0e7ff,#c7d2fe)' },
  { title: '订单总金额', value: `￥${totalOrderAmount.value.toFixed(2)}`, icon: DataLine, bg: 'linear-gradient(135deg,#fceabb,#f8b500)' },
  { title: '今日工单数', value: todayWorkOrderCount.value, icon: Tools, bg: 'linear-gradient(135deg,#d1fae5,#6ee7b7)' },
  { title: '工单总数', value: totalWorkOrderCount.value, icon: Tools, bg: 'linear-gradient(135deg,#fbc2eb,#a6c1ee)' },
  { title: '产品总数', value: totalProductCount.value, icon: HomeFilled, bg: 'linear-gradient(135deg,#f9d423,#ff4e50)' },
  { title: '物料总数', value: totalMaterialCount.value, icon: DataLine, bg: 'linear-gradient(135deg,#a1c4fd,#c2e9fb)' },
  { title: '客户总数', value: totalCustomerCount.value, icon: UserFilled, bg: 'linear-gradient(135deg,#fbc2eb,#f8b500)' },
  { title: '产品类别数', value: totalCategoryCount.value, icon: HomeFilled, bg: 'linear-gradient(135deg,#a1c4fd,#fbc2eb)' },
  { title: '工序总数', value: totalProcessCount.value, icon: Tools, bg: 'linear-gradient(135deg,#fceabb,#a1c4fd)' },
  { title: '工艺流程总数', value: totalProcessCodeCount.value, icon: DataLine, bg: 'linear-gradient(135deg,#fbc2eb,#a6c1ee)' },
])

// 统计卡片分组，每行6个
const statRows = computed(() => {
  const perRow = 5
  const arr = []
  for (let i = 0; i < statList.value.length; i += perRow) {
    arr.push(statList.value.slice(i, i + perRow))
  }
  return arr
})

// 订单状态分布
const orderStatusPieOption = computed(() => {
  const statusMap: Record<string, number> = {}
  salesStore.salesOrders.forEach(o => {
    let statusKey = '其他'; // Default status

    const orderQty = parseFloat(String(o.quantity));
    const deliveredQty = parseFloat(String(o.actual_quantity));

    if (!isNaN(orderQty) && !isNaN(deliveredQty) && deliveredQty >= orderQty) {
      statusKey = '已交付';
    } else {
      // Check against the set of orders without work orders
      if (ordersWithoutWorkOrderIdSet.value.has(o.id)) {
        statusKey = '未下工单';
      } else {
        // If not in the set and not delivered, assume it has a work order
        statusKey = '已下工单';
      }
    }
    
    // Fallback for statuses that might not fit the above logic cleanly, e.g. 'cancelled' from o.status
    // This ensures statuses like 'cancelled' from o.status can still be categorized if they don't meet other criteria.
    if (o.status && (o.status === 'cancelled' || o.status === 'draft') && statusKey !== '未下工单' && statusKey !== '已交付') {
        // if o.status is draft and it was determined as '已下工单' by not being in the set, correct it to '未下工单'
        if (o.status === 'draft') statusKey = '未下工单';
        // if o.status is cancelled, it should be '其他' or its specific display name if not already delivered.
        else if (o.status === 'cancelled' && statusKey !== '已交付') statusKey = o.status_display || o.status || '其他';
    } else if (statusKey === '其他' && o.status_display) {
        statusKey = o.status_display;
    } else if (statusKey === '其他' && o.status) {
        statusKey = o.status;
    }

    statusMap[statusKey] = (statusMap[statusKey] || 0) + 1
  })
  return {
    tooltip: { trigger: 'item' },
    legend: { top: 'bottom' },
    series: [
      {
        name: '订单状态',
        type: 'pie',
        radius: '60%',
        data: Object.entries(statusMap).map(([name, value]) => ({ name, value }))
      }
    ]
  }
})
// 工单状态分布
const WORK_ORDER_STATUS_MAP: Record<string, string> = {
  'draft': '草稿',
  'print': '待打印',
  'released': '已下达',
  'in_progress': '生产中',
  'completed': '已完成',
  'cancelled': '已取消'
  // Add other frontend-specific statuses if they exist and need mapping
};

const workOrderStatusPieOption = computed(() => {
  const statusMap: Record<string, number> = {}
  workOrderStore.list.forEach(w => {
    const chineseStatus = WORK_ORDER_STATUS_MAP[w.status?.toLowerCase() || ''] || w.status || '未知';
    statusMap[chineseStatus] = (statusMap[chineseStatus] || 0) + 1
  })
  return {
    tooltip: { trigger: 'item' },
    legend: { top: 'bottom' },
    series: [
      {
        name: '工单状态',
        type: 'pie',
        radius: '60%',
        data: Object.entries(statusMap).map(([name, value]) => ({ name, value }))
      }
    ]
  }
})
// 近7天订单金额趋势
const orderAmountTrendOption = computed(() => {
  const days: string[] = []
  const data: number[] = []
  
  // 获取最近7天的日期和数据
  for (let i = 6; i >= 0; i--) {
    const d = new Date(Date.now() - i * 24 * 3600 * 1000)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const ds = `${year}-${month}-${day}`
    days.push(ds)
    
    // 计算每天的订单金额总和
    let dailyAmount = 0
    salesStore.salesOrders.forEach(order => {
      if (!order.order_date) return
      
      // 转换订单日期为标准格式
      const orderDate = new Date(order.order_date)
      const orderYear = orderDate.getFullYear()
      const orderMonth = String(orderDate.getMonth() + 1).padStart(2, '0')
      const orderDay = String(orderDate.getDate()).padStart(2, '0')
      const orderDateStr = `${orderYear}-${orderMonth}-${orderDay}`
      
      // 如果日期匹配，累加金额
      if (orderDateStr === ds) {
        const amount = parseFloat(String(order.total_amount || 0))
        if (!isNaN(amount)) {
          dailyAmount += amount
        }
      }
    })
    
    data.push(dailyAmount)
  }
  
  console.log('订单金额趋势数据:', { days, data })
  
  return {
    tooltip: { 
      trigger: 'axis',
      formatter: function(params: any[]) {
        if (!params || params.length === 0) return ''
        
        const param = params[0]
        const date = param.name
        const value = typeof param.value === 'number' ? param.value : 0
        
        return `${date}<br/>${param.seriesName}: ¥${value.toFixed(2)}`
      },
      axisPointer: {
        animation: false
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: { 
      type: 'category', 
      data: days,
      axisLabel: {
        formatter: function(value: string) {
          return value.substring(5) // 只显示月-日
        }
      }
    },
    yAxis: { 
      type: 'value',
      axisLabel: {
        formatter: function(value: number) {
          return '¥' + value.toFixed(2)
        }
      }
    },
    series: [{ 
      name: '订单金额', 
      type: 'line', 
      data: data,
      symbolSize: 8,
      itemStyle: {
        color: '#3578e5'
      },
      lineStyle: {
        width: 2
      },
      label: {
        show: true,
        position: 'top',
        formatter: function(params: any) {
          const value = typeof params.value === 'number' ? params.value : 0
          return '¥' + value.toFixed(2)
        }
      }
    }]
  }
})
// 近7天工单数量趋势
const workOrderTrendOption = computed(() => {
  const days: string[] = []
  const data: number[] = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(Date.now() - i * 24 * 3600 * 1000)
    const ds = d.toISOString().slice(0, 10)
    days.push(ds)
    data.push(workOrderStore.list.filter(w => (w.created_at || '').slice(0, 10) === ds).length)
  }
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: days },
    yAxis: { type: 'value' },
    series: [{ name: '工单数', type: 'line', data }]
  }
})

const chartReady = ref(false)
const chartRefs = ref<any[]>([])

onMounted(async () => {
  await Promise.all([
    salesStore.fetchSalesOrders({ page: 1, page_size: 999 }),
    workOrderStore.fetchList({ page: 1, page_size: 999 }),
    productStore.fetchProducts({ page: 1, pageSize: 999 }),
    materialStore.fetchMaterials({ page: 1, page_size: 999 }),
    companyStore.fetchCompanies(),
    userStore.getLoginStatus(),
    categoryStore.fetchCategories({ page: 1, page_size: 999 }),
    processStore.fetchProcesses(),
    processCodeStore.fetchProcessCodes(),
    fetchOrdersWithoutWorkOrderIds()
  ])
  console.log("[DEBUG] Fetched salesStore.salesOrders:", JSON.parse(JSON.stringify(salesStore.salesOrders))); // DEBUG
  await nextTick()
  chartReady.value = true
  await nextTick()
  chartRefs.value.forEach(ref => ref && ref.resize && ref.resize())
})
const logout = () => {
  document.cookie = 'sessionid=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/'
  router.push('/login')
}
</script>

<style scoped>
.dashboard-bg {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #e3eefe 0%, #f7faff 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  overflow-x: auto;
}
.unified-width {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}
.welcome-header {
  margin: 36px auto 0 auto;
  padding: 40px 0 32px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* 去掉背景色、圆角、阴影，让头部融入背景 */
  background: none;
  border-radius: 0;
  box-shadow: none;
}
.welcome-logo {
  width: 80px;
  height: 80px;
  margin-bottom: 18px;
}
.inline-logo {
  width: 80px;
  height: 80px;
  vertical-align: middle;
  margin: 0 4px;
}
.welcome-title {
  font-size: 2.8rem;
  font-weight: bold;
  color: #3578e5;
  margin-bottom: 12px;
  letter-spacing: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.welcome-desc {
  font-size: 1.25rem;
  color: #888;
  margin-bottom: 0;
}
.dashboard-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  box-sizing: border-box;
}
.dashboard-cards-group {
  width: 100%;
  margin-bottom: 36px;
}
.dashboard-cards {
  margin-bottom: 18px;
  width: 100%;
  justify-content: center;
}
.stat-card {
  text-align: center;
  min-height: 140px;
  font-size: 18px;
  border-radius: 16px;
  box-shadow: 0 2px 12px 0 rgba(80,140,230,0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 22px 0 16px 0;
  background: #fff;
  transition: transform 0.3s ease-out;
}
.stat-card:hover {
  transform: translateY(-5px);
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 8px auto;
  box-shadow: 0 2px 8px 0 rgba(80,140,230,0.10);
}
.stat-icon .el-icon {
  color: #ffffff;
}
.stat-title {
  color: #888;
  font-size: 16px;
  margin-bottom: 6px;
  margin-top: 2px;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #2d8cf0;
}
.dashboard-charts {
  margin-bottom: 32px;
  width: 100%;
  justify-content: center;
}
.chart-card {
  min-height: 360px;
  border-radius: 16px;
  box-shadow: 0 2px 12px 0 rgba(80,140,230,0.08);
}
.chart-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
}
.logout-btn {
  font-size: 1.1rem;
  padding: 0 32px;
  border-radius: 8px;
  height: 44px;
  box-shadow: 0 2px 8px 0 rgba(255,0,0,0.08);
}
</style>

