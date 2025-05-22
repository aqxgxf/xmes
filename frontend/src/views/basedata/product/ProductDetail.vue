<template>
  <div class="product-detail">
    <div class="page-header">
      <h2>{{ product?.name || '加载中...' }}</h2>
      <el-button-group>
        <el-button type="primary" @click="goBack">返回</el-button>
        <el-button 
          type="success" 
          @click="handleApplyMaterialRules" 
          :loading="applying"
        >
          生成BOM物料
        </el-button>
        <el-button 
          type="warning" 
          @click="handleCreateProductProcess" 
          :loading="processingWorkflow"
        >
          创建工艺流程
        </el-button>
        <el-button 
          type="info" 
          @click="showProcessCodeDialog" 
          :loading="processingWorkflow"
        >
          关联已有工艺流程
        </el-button>
      </el-button-group>
    </div>
    
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基本信息" name="basic">
        <div v-if="product" class="product-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="产品名称">{{ product?.name }}</el-descriptions-item>
            <el-descriptions-item label="产品代码">{{ product?.code || '-' }}</el-descriptions-item>
            <el-descriptions-item label="产品类别">{{ getCategoryName }}</el-descriptions-item>
            <el-descriptions-item label="单位">{{ product?.unit_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="描述">{{ product?.description || '-' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(product?.created_at) }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="参数值" name="params">
        <product-param-values :product-id="productId" v-if="product" />
      </el-tab-pane>
      
      <el-tab-pane label="BOM" name="bom">
        <product-bom-list :product-id="productId" v-if="product" />
      </el-tab-pane>
      
      <el-tab-pane label="工艺流程" name="process">
        <div class="process-actions" v-if="product">
          <el-button type="primary" size="small" @click="showProcessCodeDialog">
            <el-icon><Plus /></el-icon> 关联工艺流程
          </el-button>
        </div>
        <product-process-list 
          :product-id="productId" 
          v-if="product"
          @remove-process="handleRemoveProcess"
          @set-default="handleSetDefaultProcess" 
        />
      </el-tab-pane>
    </el-tabs>
    
    <!-- 物料规则选择对话框 -->
    <el-dialog
      v-model="ruleDialogVisible"
      title="选择BOM物料规则"
      width="500px"
    >
      <p>请选择要应用的物料规则：</p>
      <el-table
        v-loading="rulesLoading"
        :data="materialRules"
        style="width: 100%"
        @row-click="handleRuleSelect"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="source_category_name" label="产品类" />
        <el-table-column prop="target_category_name" label="物料产品类" />
      </el-table>
    </el-dialog>
    
    <!-- 工艺流程选择对话框 -->
    <el-dialog
      v-model="processDialogVisible"
      title="选择工艺流程"
      width="500px"
    >
      <p>请选择要关联的工艺流程：</p>
      <el-table
        v-loading="processCodes.loading"
        :data="processCodes.data"
        style="width: 100%"
        @row-click="handleProcessCodeSelect"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="code" label="工艺编号" />
        <el-table-column prop="name" label="工艺名称" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, defineAsyncComponent } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElLoading, ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import dayjs from 'dayjs';
import api from '../../../api';
import { useCategoryMaterialRuleStore } from '../../../stores/categoryMaterialRuleStore';
import { useCategoryStore } from '../../../stores/categoryStore';
import type { CategoryMaterialRule, Product } from '../../../types';
import { applyMaterialRules, createProductProcess } from '../../../utils/productHelper';

// 使用defineAsyncComponent异步导入组件
const ProductParamValues = defineAsyncComponent(() => import('../../../components/basedata/ProductParamValues.vue'));
const ProductBomList = defineAsyncComponent(() => import('../../../components/basedata/ProductBomList.vue'));
const ProductProcessList = defineAsyncComponent(() => import('../../../components/basedata/ProductProcessList.vue'));

const route = useRoute();
const router = useRouter();
const categoryStore = useCategoryStore();

const productId = Number(route.params.id);
const product = ref<Product | null>(null);
const activeTab = ref('basic');
const ruleStore = useCategoryMaterialRuleStore();
const applying = ref(false);
const rulesLoading = ref(false);
const materialRules = ref<CategoryMaterialRule[]>([]);
const ruleDialogVisible = ref(false);

// 计算属性 - 获取产品类别完整名称
const getCategoryName = computed(() => {
  if (!product.value || !product.value.category) return '-';
  
  // 如果产品对象中已有category_name，直接使用
  if (product.value.category_name) return product.value.category_name;
  
  // 否则从categoryStore中查找
  const category = categoryStore.categories.find(c => c.id === product.value?.category);
  if (category) {
    return `${category.code}-${category.display_name}`;
  }
  
  return '-';
});

// 工艺流程相关
const processDialogVisible = ref(false);
const processingWorkflow = ref(false);
const processCodes = ref({
  loading: false,
  data: []
});

// 修复：定义 showProcessCodeDialog，handleRemoveProcess，handleSetDefaultProcess
const showProcessCodeDialog = async () => {
  processingWorkflow.value = true;
  try {
    await fetchProcessCodes();
    processDialogVisible.value = true;
  } catch (error) {
    ElMessage.error('获取工艺流程失败');
  } finally {
    processingWorkflow.value = false;
  }
};

const handleRemoveProcess = async (processId: number) => {
  try {
    await ElMessageBox.confirm('确定要移除该工艺流程关联吗？', '提示', { type: 'warning' });
    await api.delete(`/product-process-codes/${processId}/`);
    ElMessage.success('工艺流程关联已移除');
    // 刷新工艺流程列表
    const processEvent = new CustomEvent('refresh-process', { detail: { productId } });
    window.dispatchEvent(processEvent);
  } catch (error) {
    // 用户取消或删除失败
  }
};

const handleSetDefaultProcess = async (productProcessId: number) => {
  try {
    await api.patch(`/product-process-codes/${productProcessId}/`, { is_default: true });
    ElMessage.success('已设为默认工艺流程');
    const processEvent = new CustomEvent('refresh-process', { detail: { productId } });
    window.dispatchEvent(processEvent);
  } catch (error) {
    ElMessage.error('设置默认工艺流程失败');
  }
};

const fetchProduct = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '加载中...'
  });
  
  try {
    const response = await api.get(`/products/${productId}/`);
    product.value = response.data;
    
    // 确保categoryStore已初始化
    if (categoryStore.categories.length === 0) {
      await categoryStore.initialize();
    }
  } catch (error) {
    console.error('获取产品失败:', error);
    ElMessage.error('获取产品失败');
  } finally {
    loading.close();
  }
};

onMounted(() => {
  fetchProduct();
});

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-';
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss');
};

const goBack = () => {
  router.push('/products');
};

// 加载物料规则
const fetchMaterialRules = async () => {
  if (!product.value || !product.value.category) {
    ElMessage.warning('产品数据不完整，无法获取物料规则');
    return [];
  }
  
  rulesLoading.value = true;
  try {
    const params = { source_category: product.value.category };
    await ruleStore.fetchRules(params);
    materialRules.value = ruleStore.rules;
    return materialRules.value;
  } catch (error) {
    console.error('获取物料规则失败:', error);
    ElMessage.error('获取物料规则失败');
    return [];
  } finally {
    rulesLoading.value = false;
  }
};

// 应用物料规则
const handleApplyMaterialRules = async () => {
  if (!product.value || !product.value.id) return;
  await applyMaterialRules(product.value.id);
};

// 选择物料规则
const handleRuleSelect = async (row: CategoryMaterialRule) => {
  ruleDialogVisible.value = false;
  await generateMaterial(row.id);
};

// 生成物料
const generateMaterial = async (ruleId: number) => {
  applying.value = true;
  try {
    const result = await ruleStore.generateMaterial(ruleId, productId);
    console.log('generateMaterial result:', result);
    if (result) {
      ElMessage.success(`成功${result.material_created ? '创建' : '使用'}物料：${result.material.name}`);
      // 检查是否有现有BOM
      let bomId = null;
      if (result.bom) {
        bomId = result.bom.id;
        console.log('已存在BOM:', result.bom);
      } else {
        if (!product.value?.code) {
          ElMessage.warning('产品代码不存在，无法创建BOM');
          return;
        }
        const bomData = {
          product: productId,
          name: `${product.value?.code}-A`,
          version: 'A',
          description: `${product.value?.name}的默认BOM`
        };
        const bomResponse = await api.post('/boms/', bomData);
        bomId = bomResponse.data.id;
        console.log('新建BOM:', bomResponse.data);
      }
      // 自动生成BOM明细（如BOM和物料都存在，先查重再写入）
      if (bomId && result.material && result.material.id) {
        try {
          // 查重
          const bomItemsResp = await api.get('/bom-items/', { params: { bom: bomId, material: result.material.id } });
          const bomItems = bomItemsResp.data.results || bomItemsResp.data || [];
          console.log('BOM明细查重结果:', bomItems);
          if (!Array.isArray(bomItems) || bomItems.length === 0) {
            const bomItemData = {
              bom: bomId,
              material: result.material.id,
              quantity: 1,
              remark: '自动生成'
            };
            const bomItemResp = await api.post('/bom-items/', bomItemData);
            console.log('新建BOM明细:', bomItemResp.data);
          } else {
            console.log('BOM明细已存在，未重复创建');
          }
        } catch (itemError) {
          console.error('自动生成BOM明细失败:', (itemError as any)?.response?.data || itemError);
        }
      } else {
        console.warn('BOM或物料ID缺失，无法生成BOM明细', bomId, result.material);
      }
      // 切换到BOM标签并刷新
      activeTab.value = 'bom';
      const bomEvent = new CustomEvent('refresh-bom', { detail: { productId } });
      window.dispatchEvent(bomEvent);
    }
  } catch (error) {
    console.error('生成物料失败:', error);
    ElMessage.error('生成物料失败，请重试');
  } finally {
    applying.value = false;
  }
};

// 获取可用的工艺流程
const fetchProcessCodes = async () => {
  processCodes.value.loading = true;
  try {
    const response = await api.get('/process-codes/', {
      params: { page_size: 999 }
    });
    processCodes.value.data = response.data.results || response.data;
    return processCodes.value.data;
  } catch (error) {
    console.error('获取工艺流程失败:', error);
    ElMessage.error('获取工艺流程失败');
    return [];
  } finally {
    processCodes.value.loading = false;
  }
};

// 自动生成工艺流程
const handleCreateProductProcess = async () => {
  if (!product.value || !product.value.id) return;
  await createProductProcess(product.value.id);
};

// 选择工艺流程
const handleProcessCodeSelect = async (row: any) => {
  processDialogVisible.value = false;
  await linkProcessCode(row.id);
};

// 关联工艺流程
const linkProcessCode = async (processCodeId: number) => {
  processingWorkflow.value = true;
  try {
    const response = await api.post('/product-process-codes/', {
      product: productId,
      process_code: processCodeId,
      is_default: true // 设为默认工艺流程
    });
    
    if (response && response.data) {
      ElMessage.success('工艺流程关联成功');
      // 刷新工艺流程列表
      const processEvent = new CustomEvent('refresh-process', { detail: { productId } });
      window.dispatchEvent(processEvent);
      
      // 自动跳转到工艺流程标签
      activeTab.value = 'process';
    } else {
      ElMessage.warning('工艺流程关联失败，未返回有效数据');
    }
  } catch (error) {
    console.error('关联工艺流程失败:', error);
    ElMessage.error('关联工艺流程失败，请重试');
  } finally {
    processingWorkflow.value = false;
  }
};
</script>

<style scoped>
.product-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.product-info {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.process-actions {
  margin-bottom: 10px;
}
</style>