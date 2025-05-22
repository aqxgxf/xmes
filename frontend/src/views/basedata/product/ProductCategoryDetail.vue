<template>
  <div class="product-category-detail">
    <div class="page-header">
      <h2>{{ category ? category.display_name : '加载中...' }}</h2>
      <el-button-group>
        <el-button type="primary" @click="goBack">返回</el-button>
      </el-button-group>
    </div>
    
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基本信息" name="basic">
        <div v-if="category" class="category-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="名称">{{ category.display_name }}</el-descriptions-item>
            <el-descriptions-item label="代码">{{ category.code || '-' }}</el-descriptions-item>
            <el-descriptions-item label="公司">{{ category.company_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="单位">{{ category.unit_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(category.created_at) }}</el-descriptions-item>
          </el-descriptions>
          <el-button type="primary" style="margin-top: 20px;" @click="goToMaterialRule">
            编辑BOM物料规则
          </el-button>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElLoading } from 'element-plus';
import dayjs from 'dayjs';
import api from '../../../api';

const route = useRoute();
const router = useRouter();

const categoryId = Number(route.params.id);
const category = ref<any>(null);
const activeTab = ref('basic');

const fetchCategory = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '加载中...'
  });
  
  try {
    const response = await api.get(`/product-categories/${categoryId}/`);
    category.value = response.data;
  } catch (error) {
    console.error('获取产品类失败:', error);
  } finally {
    loading.close();
  }
};

onMounted(() => {
  fetchCategory();
});

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-';
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss');
};

const goBack = () => {
  router.push('/product-categories');
};

const goToMaterialRule = () => {
  router.push({ path: '/category-material-rule', query: { category_id: categoryId } });
};
</script>

<style scoped>
.product-category-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.category-info {
  margin-bottom: 20px;
}
</style> 