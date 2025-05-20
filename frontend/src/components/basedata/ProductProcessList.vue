<template>
  <div class="product-process-list">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <h3>产品工艺流程</h3>
        </div>
      </template>
      
      <div v-loading="loading">
        <el-empty v-if="processCodes.length === 0" description="暂无工艺流程信息" />
        
        <el-table v-else :data="processCodes" border stripe>
          <el-table-column label="工艺流程名称" min-width="200">
            <template #default="{ row }">
              {{ row.process_code_name || row.product_name || '未命名' }}
            </template>
          </el-table-column>
          <el-table-column label="工艺流程代码" min-width="150">
            <template #default="{ row }">
              {{ row.process_code_text || row.process_code || '未知' }} ({{ row.process_code_version || row.version || '' }})
            </template>
          </el-table-column>
          <el-table-column prop="is_default" label="默认工艺" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_default ? 'success' : 'info'">
                {{ row.is_default ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" type="primary" @click="viewProcessDetails(row)">
                  <el-icon><Document /></el-icon> 查看明细
                </el-button>
                <el-button 
                  size="small" 
                  type="success" 
                  @click="setDefaultProcess(row)"
                  v-if="!row.is_default"
                >
                  <el-icon><Check /></el-icon> 设为默认
                </el-button>
                <el-button size="small" type="danger" @click="removeProcess(row)">
                  <el-icon><Delete /></el-icon> 移除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
    
    <!-- 工艺流程明细对话框 -->
    <el-dialog v-model="detailsVisible" title="工艺流程明细" width="900px" destroy-on-close>
      <div v-loading="detailsLoading">
        <el-table 
          v-if="processDetails.length > 0" 
          :data="processDetails" 
          border 
          stripe
        >
          <el-table-column prop="step_no" label="序号" width="80" />
          <el-table-column prop="step_name" label="工序" min-width="120" />
          <el-table-column prop="process_content" label="工序内容" min-width="250" />
          <el-table-column prop="machine_time" label="设备时间(分钟)" width="140" />
          <el-table-column prop="labor_time" label="人工时间(分钟)" width="140" />
        </el-table>
        <el-empty v-else description="暂无工艺流程明细" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="ProductProcessList">
import { ref, onMounted, watch, onUnmounted, defineEmits } from 'vue';
import api from '../../api';
import { ElMessage } from 'element-plus';
import { Document, Check, Delete } from '@element-plus/icons-vue';

// 定义组件事件
const emit = defineEmits(['remove-process', 'set-default']);

// 接收产品ID作为props
interface Props {
  productId: number;
}

const props = defineProps<Props>();

// 组件状态
const loading = ref(false);
const processCodes = ref<any[]>([]);
const detailsVisible = ref(false);
const detailsLoading = ref(false);
const processDetails = ref<any[]>([]);
const currentProcessCodeId = ref<number | null>(null);

// 获取产品相关的工艺流程
const fetchProductProcessCodes = async () => {
  if (!props.productId) return;
  
  loading.value = true;
  try {
    const response = await api.get('/product-process-codes/', {
      params: { product: props.productId }
    });
    
    // 处理响应数据
    if (response.data && response.data.results) {
      processCodes.value = response.data.results;
    } else if (Array.isArray(response.data)) {
      processCodes.value = response.data;
    } else {
      processCodes.value = [];
    }
    
    // 调试日志
    console.log('获取到产品工艺流程数据:', processCodes.value);
    if (processCodes.value.length > 0) {
      console.log('首条数据字段:', Object.keys(processCodes.value[0]));
      console.log('首条数据内容:', processCodes.value[0]);
    }
  } catch (error) {
    console.error('获取产品工艺流程失败:', error);
    ElMessage.error('获取产品工艺流程失败');
  } finally {
    loading.value = false;
  }
};

// 获取工艺流程明细
const fetchProcessDetails = async (processCodeId: number) => {
  if (!processCodeId) return;

  detailsLoading.value = true;
  currentProcessCodeId.value = processCodeId;

  try {
    // 从processCodes中找到对应的code和version
    const codeObj = processCodes.value.find(p => p.process_code === processCodeId || p.id === processCodeId);
    if (!codeObj || !codeObj.process_code_text || !codeObj.process_code_version) {
      ElMessage.error('找不到工艺流程代码的code/version');
      detailsLoading.value = false;
      return;
    }
    // 精确匹配
    const response = await api.get('/process-details/', {
      params: {
        process_code__code: codeObj.process_code_text,
        process_code__version: codeObj.process_code_version,
        page_size: 100
      }
    });
    let allDetails = [];
    if (response.data && response.data.results) {
      allDetails = response.data.results;
    } else if (Array.isArray(response.data)) {
      allDetails = response.data;
    }
    processDetails.value = allDetails;
    console.log(`获取到${allDetails.length}条工艺明细`);
    processDetails.value.sort((a, b) => a.step_no - b.step_no);
    console.log('当前工艺流程ID:', processCodeId);
    console.log('过滤后的工艺明细:', processDetails.value);
  } catch (error) {
    console.error('获取工艺流程明细失败:', error);
    ElMessage.error('获取工艺流程明细失败');
  } finally {
    detailsLoading.value = false;
  }
};

// 查看工艺流程明细
const viewProcessDetails = (processCode: any) => {
  detailsVisible.value = true;
  fetchProcessDetails(processCode.process_code);
  console.log('查看工艺流程明细:', processCode);
};

// 设置默认工艺流程
const setDefaultProcess = (row: any) => {
  emit('set-default', row.id);
};

// 移除工艺流程关联
const removeProcess = (row: any) => {
  emit('remove-process', row.id);
};

// 注册事件监听 - 用于刷新工艺流程列表
window.addEventListener('refresh-process', (event: CustomEvent) => {
  if (event.detail && event.detail.productId === props.productId) {
    fetchProductProcessCodes();
  }
});

// 监听产品ID变化，重新加载数据
watch(() => props.productId, (newValue) => {
  if (newValue) {
    fetchProductProcessCodes();
  } else {
    processCodes.value = [];
  }
});

// 初始加载
onMounted(() => {
  if (props.productId) {
    fetchProductProcessCodes();
  }
});

// 清理事件监听
onUnmounted(() => {
  window.removeEventListener('refresh-process', (event: CustomEvent) => {
    if (event.detail && event.detail.productId === props.productId) {
      fetchProductProcessCodes();
    }
  });
});
</script>

<style scoped>
.product-process-list {
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

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style> 