<template>
  <div class="material-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">材质管理</h2>
          <div class="search-actions">
            <el-input v-model="searchQuery" placeholder="搜索材质名称/代码" clearable @input="handleSearch">
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="openAddDialog">
              <el-icon>
                <Plus />
              </el-icon> 新增材质
            </el-button>
          </div>
        </div>
      </template>
      <el-table :data="materialTypes" v-loading="loading" border stripe style="width: 100%">
        <el-table-column prop="name" label="材质名称" min-width="120" />
        <el-table-column prop="code" label="材质代码" min-width="100" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openEditDialog(row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button size="small" type="danger" @click="confirmDelete(row)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination 
          v-model="currentPage"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" :total="total"
          @size-change="handleSizeChange" @current-change="handleCurrentChange" background />
      </div>
    </el-card>
    <el-dialog v-model="showDialog" :title="dialogTitle" width="500px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" label-position="left">
        <el-form-item label="材质名称" prop="name">
          <el-input v-model="form.name" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="材质代码" prop="code">
          <el-input v-model="form.code" maxlength="20" show-word-limit />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Plus, Edit, Delete } from '@element-plus/icons-vue';
import type { MaterialType } from '../../../types/common';
import api from '../../../api';

// 材质类型列表
const materialTypes = ref<MaterialType[]>([]);
const loading = ref(false);
const submitting = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const searchQuery = ref('');
const showDialog = ref(false);
const dialogTitle = ref('新增材质');
const isEdit = ref(false);
const form = ref<Partial<MaterialType>>({ name: '', code: '', description: '' });
const formRef = ref();
const rules = {
  name: [{ required: true, message: '请输入材质名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入材质代码', trigger: 'blur' }],
};

const fetchMaterialTypes = async () => {
  loading.value = true;
  try {
    const response = await api.get('/material-types/', { params: { page: currentPage.value, page_size: pageSize.value, search: searchQuery.value } });
    materialTypes.value = response.data.results || response.data;
    total.value = response.data.count || materialTypes.value.length;
  } catch (error) {
    ElMessage.error('获取材质列表失败');
  } finally {
    loading.value = false;
  }
};

const openAddDialog = () => {
  form.value = { name: '', code: '', description: '' };
  dialogTitle.value = '新增材质';
  isEdit.value = false;
  showDialog.value = true;
};
const openEditDialog = (row: MaterialType) => {
  form.value = { ...row };
  dialogTitle.value = '编辑材质';
  isEdit.value = true;
  showDialog.value = true;
};
const submitForm = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return;
    submitting.value = true;
    try {
      if (isEdit.value && form.value.id) {
        await api.put(`/material-types/${form.value.id}/`, form.value);
        ElMessage.success('更新材质成功');
      } else {
        await api.post('/material-types/', form.value);
        ElMessage.success('新增材质成功');
      }
      showDialog.value = false;
      fetchMaterialTypes();
    } catch (error) {
      ElMessage.error('保存材质失败');
    } finally {
      submitting.value = false;
    }
  });
};
const confirmDelete = (row: MaterialType) => {
  ElMessageBox.confirm(`确定要删除材质 "${row.name}" 吗？`, '删除确认', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    .then(async () => {
      try {
        await api.delete(`/material-types/${row.id}/`);
        ElMessage.success('删除材质成功');
        fetchMaterialTypes();
      } catch (error) {
        ElMessage.error('删除材质失败');
      }
    })
    .catch(() => {});
};
const handleSearch = () => {
  fetchMaterialTypes();
};
const handleSizeChange = (val: number) => {
  pageSize.value = val;
  fetchMaterialTypes();
};
const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  fetchMaterialTypes();
};
onMounted(() => {
  fetchMaterialTypes();
});
</script>
<style scoped>
.material-container { padding: 20px; }
.header-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { margin: 0; font-size: 18px; }
.search-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 24px; display: flex; justify-content: flex-end; }
</style>