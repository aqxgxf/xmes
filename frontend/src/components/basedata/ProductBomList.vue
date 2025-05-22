<template>
  <div class="product-bom-list">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <h3>产品BOM</h3>
        </div>
      </template>
      
      <div v-loading="loading">
        <el-empty v-if="boms.length === 0" description="暂无BOM信息">
          <template #description>
            <div>
              <p>暂无BOM信息</p>
              <el-button size="small" type="primary" @click="createBom">创建BOM</el-button>
            </div>
          </template>
        </el-empty>
        
        <el-table v-else :data="boms" border stripe>
          <el-table-column prop="code" label="BOM编号" min-width="150" />
          <el-table-column prop="name" label="BOM名称" min-width="200" />
          <el-table-column prop="version" label="版本" width="100" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">
                {{ row.is_active ? '启用' : '未启用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="viewBomDetails(row)">查看明细</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
    
    <!-- BOM明细对话框 -->
    <el-dialog v-model="bomDetailsVisible" title="BOM明细" width="900px" destroy-on-close>
      <div v-loading="detailsLoading">
        <el-table v-if="bomDetails.length > 0" :data="bomDetails" border stripe>
          <el-table-column prop="material_code" label="物料编号" min-width="150" />
          <el-table-column prop="material_name" label="物料名称" min-width="200" />
          <el-table-column prop="quantity" label="数量" width="100" />
          <el-table-column prop="unit_name" label="单位" width="80" />
          <el-table-column prop="remarks" label="备注" min-width="150" />
        </el-table>
        <el-empty v-else description="暂无BOM明细" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="ProductBomList">
import { ref, onMounted, watch } from 'vue';
import api from '../../api';
import { ElMessage } from 'element-plus';

// 接收产品ID作为props
interface Props {
  productId: number;
}

const props = defineProps<Props>();

// 组件状态
const loading = ref(false);
const boms = ref<any[]>([]);
const bomDetailsVisible = ref(false);
const detailsLoading = ref(false);
const bomDetails = ref<any[]>([]);
const currentBomId = ref<number | null>(null);

// 获取产品相关的BOM
const fetchProductBoms = async () => {
  if (!props.productId) return;
  
  loading.value = true;
  try {
    const response = await api.get('/boms/', {
      params: { product: props.productId }
    });
    
    // 处理响应数据
    if (response.data && response.data.results) {
      boms.value = response.data.results;
    } else if (Array.isArray(response.data)) {
      boms.value = response.data;
    } else {
      boms.value = [];
    }
  } catch (error) {
    console.error('获取产品BOM失败:', error);
    ElMessage.error('获取产品BOM失败');
  } finally {
    loading.value = false;
  }
};

// 获取BOM明细
const fetchBomDetails = async (bomId: number) => {
  if (!bomId) return;
  
  detailsLoading.value = true;
  currentBomId.value = bomId;
  
  try {
    const response = await api.get('/bom-items/', {
      params: { bom: bomId }
    });
    
    // 处理响应数据
    if (response.data && response.data.results) {
      bomDetails.value = response.data.results;
    } else if (Array.isArray(response.data)) {
      bomDetails.value = response.data;
    } else {
      bomDetails.value = [];
    }
  } catch (error) {
    console.error('获取BOM明细失败:', error);
    ElMessage.error('获取BOM明细失败');
  } finally {
    detailsLoading.value = false;
  }
};

// 查看BOM明细
const viewBomDetails = (bom: any) => {
  bomDetailsVisible.value = true;
  fetchBomDetails(bom.id);
};

// 创建新BOM
const createBom = () => {
  // 通过路由导航或其他方式跳转到BOM创建页面
  // 在实际项目中，可能需要调整为弹出表单或跳转到BOM创建页面
  ElMessage.info('请前往BOM管理页面创建BOM');
  // 也可以实现直接创建BOM的功能，但需要用户输入更多信息
};

// 注册事件监听 - 用于刷新BOM列表
function handleRefreshBom(event: Event) {
  const customEvent = event as CustomEvent;
  if (customEvent.detail && customEvent.detail.productId === props.productId) {
    fetchProductBoms();
  }
}
window.addEventListener('refresh-bom', handleRefreshBom as EventListener);

// 监听产品ID变化，重新加载数据
watch(() => props.productId, (newValue) => {
  if (newValue) {
    fetchProductBoms();
  } else {
    boms.value = [];
  }
});

// 初始加载
onMounted(() => {
  if (props.productId) {
    fetchProductBoms();
  }
});

// 清理事件监听
onMounted(() => {
  window.removeEventListener('refresh-bom', handleRefreshBom as EventListener);
});
</script>

<style scoped>
.product-bom-list {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
}
</style> 