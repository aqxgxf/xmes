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
            <el-descriptions-item label="材质">
              {{ materialName }}
            </el-descriptions-item>
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

      <!-- 新增附件管理标签页 -->
      <el-tab-pane label="附件管理" name="attachments">
         <div v-if="product">
            <el-upload
              class="upload-demo"
              :http-request="handleFileUpload"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :on-remove="handleFileRemove"
              :before-upload="beforeUpload"
              :file-list="fileList"
              multiple
              ref="uploadRef"
            >
              <el-button type="primary"><el-icon><Upload /></el-icon> 上传附件</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持多文件上传，单个文件不超过10MB
                </div>
              </template>
            </el-upload>

            <!-- 附件列表 -->
            <el-table :data="fileList" stripe style="width: 100%; margin-top: 20px;">
              <el-table-column prop="name" label="文件名" />
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="downloadFile(row)">下载</el-button>
                  <el-button link type="danger" size="small" @click="deleteFile(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
         </div>
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
import { Plus, Upload } from '@element-plus/icons-vue';
import type { UploadRawFile, UploadFile, UploadFiles } from 'element-plus';
import dayjs from 'dayjs';
import api from '../../../api';
import { useCategoryMaterialRuleStore } from '../../../stores/categoryMaterialRuleStore';
import { useCategoryStore } from '../../../stores/categoryStore';
import { useMaterialStore } from '../../../stores/materialStore';
import type { MaterialType } from '../../../types/common';
import type { CategoryMaterialRule, Product } from '../../../types';
import type { ProductAttachment } from '../../../types/common';
import { applyMaterialRules, createProductProcess } from '../../../utils/productHelper';

// 使用defineAsyncComponent异步导入组件
const ProductParamValues = defineAsyncComponent(() => import('../../../components/basedata/ProductParamValues.vue'));
const ProductBomList = defineAsyncComponent(() => import('../../../components/basedata/ProductBomList.vue'));
const ProductProcessList = defineAsyncComponent(() => import('../../../components/basedata/ProductProcessList.vue'));

const route = useRoute();
const router = useRouter();
const categoryStore = useCategoryStore();
const materialStore = useMaterialStore();

const productId = Number(route.params.id);
const product = ref<(Product & { attachments?: ProductAttachment[] }) | null>(null);
const activeTab = ref('basic');
const ruleStore = useCategoryMaterialRuleStore();
const applying = ref(false);
const rulesLoading = ref(false);
const materialRules = ref<CategoryMaterialRule[]>([]);
const ruleDialogVisible = ref(false);
const materials = materialStore.materials;

// 附件相关状态和方法
const fileList = ref<UploadFiles>([]);
const uploadRef = ref();

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

    // 确保materialStore已初始化
    if (materials.length === 0) {
      await materialStore.fetchMaterials();
    }

    // 获取附件列表并填充fileList
    if (product.value?.attachments) {
      console.log('后端返回的附件数据:', product.value.attachments);
      fileList.value = product.value.attachments.map((attachment: ProductAttachment) => ({
        name: attachment.filename,
        url: attachment.file,
        status: 'success',
        uid: attachment.id,
      })) as UploadFiles;
      console.log('转换后用于前端的fileList:', fileList.value);
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
  fetchProduct();
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

      fetchProduct();

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
  fetchProduct();
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
      is_default: true
    });
    
    if (response && response.data) {
      ElMessage.success('工艺流程关联成功');
      // 刷新工艺流程列表
      const processEvent = new CustomEvent('refresh-process', { detail: { productId } });
      window.dispatchEvent(processEvent);
      
      // 自动跳转到工艺流程标签
      activeTab.value = 'process';

      fetchProduct();

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

const materialName = computed(() => {
  // 通过产品的 category 字段查找产品类对象
  let categoryId = product.value?.category
  if (categoryId && typeof categoryId === 'object' && (categoryId as any).id !== undefined) categoryId = (categoryId as any).id
  const category = categoryStore.categories.find(c => c.id === categoryId)
  // category.material_type 是 MaterialType
  return category && category.material_type ? category.material_type.name : '-'
});

// ======== 附件相关方法 (从之前生成的代码中合并) ========

// 文件上传前的校验
const beforeUpload = (file: UploadRawFile) => {
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB');
    return false;
  }
  return true;
};

// 自定义文件上传
const handleFileUpload = async (options: any) => {
  if (productId === null) {
    ElMessage.error('产品ID无效，无法上传附件');
    options.onError('产品ID无效');
    return;
  }

  const formData = new FormData();
  formData.append('file', options.file);
  formData.append('product', productId.toString());

  let loadingInstance: any;
  try {
    loadingInstance = ElLoading.service({ fullscreen: true, text: '上传中...' });
    const response = await api.post('/product-attachments/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    options.onSuccess(response.data);
  } catch (error: any) {
    ElMessage.error('附件上传失败: ' + (error.response?.data?.detail || error.message));
    options.onError(error);
  } finally {
    if (loadingInstance) {
      loadingInstance.close();
    }
  }
};

// 文件上传成功回调
const handleUploadSuccess = (response: any, file: UploadFile) => {
  ElMessage.success(`${file.name} 上传成功`);
  if (response && response.id) {
    const index = fileList.value.findIndex(item => item.uid === file.uid);
    if(index !== -1) {
      fileList.value[index].uid = response.id;
      fileList.value[index].url = response.file;
      fileList.value[index].name = response.filename;
      fileList.value[index].status = 'success';
    } else {
      fileList.value.push({
        name: response.filename,
        url: response.file,
        status: 'success',
        uid: response.id,
      });
    }
  } else {
    fetchProduct();
  }
};

// 文件上传失败回调
const handleUploadError = (error: any, file: UploadFile) => {
  ElMessage.error(`${file.name} 上传失败`);
  fileList.value = fileList.value.filter(item => item.uid !== file.uid);
};

// 文件移除回调 (手动删除)
const handleFileRemove = async (uploadFile: UploadFile) => {
  await deleteFile(uploadFile);
};

// 下载文件
const downloadFile = (file: UploadFile) => {
  if (file.url) {
    window.open(file.url);
  } else {
    ElMessage.warning('文件URL无效，无法下载');
  }
};

// 删除文件
const deleteFile = async (file: UploadFile) => {
  if (!file.uid) {
    ElMessage.error('文件ID无效，无法删除');
    return;
  }

  ElMessageBox.confirm(
    `确定要删除附件 "${file.name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
  .then(async () => {
    let loadingInstance: any;
    try {
      loadingInstance = ElLoading.service({ fullscreen: true, text: '删除中...' });
      await api.delete(`/product-attachments/${file.uid}/`);
      ElMessage.success(`${file.name} 删除成功`);
      fileList.value = fileList.value.filter(item => item.uid !== file.uid);
    } catch (error: any) {
      ElMessage.error('附件删除失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      if (loadingInstance) {
        loadingInstance.close();
      }
    }
  })
  .catch(() => {
    // 用户取消删除
  });
};

// ======== 结束附件相关方法 ========

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

/* 附件管理区域的样式 */
.upload-demo {
  margin-top: 20px;
}
</style>