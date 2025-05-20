<template>
  <div class="product-param-values">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <h3>产品参数值</h3>
        </div>
      </template>
      
      <div v-loading="loading">
        <el-empty v-if="paramValues.length === 0" description="暂无参数值" />
        
        <el-table v-else :data="paramValues" border stripe>
          <el-table-column prop="param_name" label="参数名称" min-width="180" />
          <el-table-column prop="value" label="参数值" min-width="200" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts" name="ProductParamValues">
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
const paramValues = ref<{ id: number; param: number; param_name: string; value: string }[]>([]);

// 获取产品参数值
const fetchParamValues = async () => {
  if (!props.productId) return;
  
  loading.value = true;
  try {
    const response = await api.get('/product-param-values/', {
      params: { product: props.productId }
    });
    
    // 处理响应数据
    let data = [];
    if (response.data && response.data.results) {
      data = response.data.results;
    } else if (Array.isArray(response.data)) {
      data = response.data;
    }
    
    // 为了显示，我们需要将参数ID映射到参数名称
    // 可以直接使用后端返回的数据，或者进一步处理增强显示
    paramValues.value = data.map(item => ({
      id: item.id,
      param: item.param,
      param_name: item.param_name || '未知参数',
      value: item.value
    }));
  } catch (error) {
    console.error('获取产品参数值失败:', error);
    ElMessage.error('获取产品参数值失败');
  } finally {
    loading.value = false;
  }
};

// 监听产品ID变化，重新加载数据
watch(() => props.productId, (newValue) => {
  if (newValue) {
    fetchParamValues();
  } else {
    paramValues.value = [];
  }
});

// 初始加载
onMounted(() => {
  if (props.productId) {
    fetchParamValues();
  }
});
</script>

<style scoped>
.product-param-values {
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