<template>
  <div class="equipment-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">设备管理</h2>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 新增设备
          </el-button>
        </div>
      </template>

      <!-- 搜索区域 -->
      <div class="search-section">
        <el-form :inline="true" class="search-form" @submit.prevent="handleSearch">
          <el-form-item label="设备编号">
            <el-input v-model="searchForm.code" placeholder="请输入设备编号" clearable />
          </el-form-item>
          <el-form-item label="设备名称">
            <el-input v-model="searchForm.name" placeholder="请输入设备名称" clearable />
          </el-form-item>
          <el-form-item label="设备状态">
            <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
              <el-option label="正常" value="normal" />
              <el-option label="维修中" value="maintenance" />
              <el-option label="待检" value="inspection" />
              <el-option label="停用" value="disabled" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon> 查询
            </el-button>
            <el-button @click="resetSearchForm">
              <el-icon><Refresh /></el-icon> 重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 数据表格 -->
      <el-table
        v-loading="loading"
        :data="tableData"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="code" label="设备编号" min-width="120" />
        <el-table-column prop="name" label="设备名称" min-width="120" />
        <el-table-column prop="model" label="设备型号" min-width="120" />
        <el-table-column prop="location" label="设备位置" min-width="120" />
        <el-table-column prop="responsible_person" label="负责人" min-width="100" />
        <el-table-column label="设备状态" min-width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status_display || getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="下次维保日期" min-width="120">
          <template #default="scope">
            <span>{{ scope.row.next_maintenance_date || '暂未设置' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                编辑
              </el-button>
              <el-button type="success" size="small" @click="handleViewDetail(scope.row)">
                详情
              </el-button>
              <el-button type="info" size="small" @click="handleMaintenance(scope.row)">
                维保
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @update:current-page="currentPage = $event"
          @update:page-size="pageSize = $event"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 设备表单对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="dialogTitle"
        width="650px"
        destroy-on-close
      >
        <el-form
          ref="formRef"
          :model="equipmentForm"
          :rules="formRules"
          label-width="100px"
          label-position="right"
        >
          <el-form-item label="设备编号" prop="code">
            <el-input v-model="equipmentForm.code" placeholder="请输入设备编号" />
          </el-form-item>
          <el-form-item label="设备名称" prop="name">
            <el-input v-model="equipmentForm.name" placeholder="请输入设备名称" />
          </el-form-item>
          <el-form-item label="设备型号" prop="model">
            <el-input v-model="equipmentForm.model" placeholder="请输入设备型号" />
          </el-form-item>
          <el-form-item label="规格参数" prop="specification">
            <el-input
              v-model="equipmentForm.specification"
              type="textarea"
              rows="3"
              placeholder="请输入规格参数"
            />
          </el-form-item>
          <el-form-item label="生产厂商" prop="manufacturer">
            <el-input v-model="equipmentForm.manufacturer" placeholder="请输入生产厂商" />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="购买日期" prop="purchase_date">
                <el-date-picker
                  v-model="equipmentForm.purchase_date"
                  type="date"
                  placeholder="选择购买日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="购买价格" prop="purchase_price">
                <el-input-number
                  v-model="equipmentForm.purchase_price"
                  :min="0"
                  :precision="2"
                  style="width: 100%"
                  placeholder="请输入购买价格"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="安装日期" prop="installation_date">
                <el-date-picker
                  v-model="equipmentForm.installation_date"
                  type="date"
                  placeholder="选择安装日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="下次维保" prop="next_maintenance_date">
                <el-date-picker
                  v-model="equipmentForm.next_maintenance_date"
                  type="date"
                  placeholder="选择下次维保日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="设备位置" prop="location">
                <el-input v-model="equipmentForm.location" placeholder="请输入设备位置" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="负责人" prop="responsible_person">
                <el-input v-model="equipmentForm.responsible_person" placeholder="请输入负责人" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="设备状态" prop="status">
            <el-select v-model="equipmentForm.status" placeholder="请选择设备状态" style="width: 100%">
              <el-option label="正常" value="normal" />
              <el-option label="维修中" value="maintenance" />
              <el-option label="待检" value="inspection" />
              <el-option label="停用" value="disabled" />
            </el-select>
          </el-form-item>
          <el-form-item label="设备图片" prop="image">
            <el-upload
              class="equipment-image-uploader"
              :auto-upload="false"
              :show-file-list="true"
              :limit="1"
              accept="image/*"
              :on-change="handleImageChange"
              :on-remove="handleImageRemove"
            >
              <el-button type="primary">点击上传</el-button>
              <template #tip>
                <div class="el-upload__tip">只能上传 jpg/png 文件，且不超过 2MB</div>
              </template>
            </el-upload>
          </el-form-item>
          <el-form-item label="备注" prop="remark">
            <el-input
              v-model="equipmentForm.remark"
              type="textarea"
              rows="2"
              placeholder="请输入备注信息"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveEquipment" :loading="submitting">
            保存
          </el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Plus, Refresh } from '@element-plus/icons-vue';
import type { FormInstance, FormRules } from 'element-plus';
import { equipmentApi } from '../../api/equipment';
import type { Equipment, EquipmentForm, EquipmentStatus } from '../../types/index';
import { useRouter } from 'vue-router';

// 路由
const router = useRouter();

// 表格数据和加载状态
const tableData = ref<Equipment[]>([]);
const loading = ref(false);
const submitting = ref(false);

// 分页相关
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

// 搜索表单
const searchForm = reactive({
  code: '',
  name: '',
  status: '',
});

// 对话框显示控制和表单
const dialogVisible = ref(false);
const dialogTitle = ref('新增设备');
const formRef = ref<FormInstance>();
const initialEquipmentForm: EquipmentForm = {
  code: '',
  name: '',
  model: '',
  specification: '',
  manufacturer: '',
  purchase_date: '',
  purchase_price: undefined,
  installation_date: '',
  location: '',
  responsible_person: '',
  status: 'normal' as EquipmentStatus,
  next_maintenance_date: '',
  image: null,
  remark: '',
};
const equipmentForm = reactive<EquipmentForm>({ ...initialEquipmentForm });
const currentEquipmentId = ref<number | null>(null);

// 表单验证规则
const formRules = reactive<FormRules>({
  code: [
    { required: true, message: '请输入设备编号', trigger: 'blur' },
    { max: 50, message: '设备编号不能超过50个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入设备名称', trigger: 'blur' },
    { max: 100, message: '设备名称不能超过100个字符', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请输入设备型号', trigger: 'blur' },
    { max: 100, message: '设备型号不能超过100个字符', trigger: 'blur' }
  ]
});

// 获取设备列表
const fetchEquipments = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchForm.code || searchForm.name ? `${searchForm.code} ${searchForm.name}`.trim() : undefined,
      status: searchForm.status || undefined
    };
    const response = await equipmentApi.getEquipments(params);
    
    // 根据API的数据结构处理响应
    tableData.value = response.data;
    total.value = response.data.length;
  } catch (error) {
    console.error('获取设备列表失败:', error);
    ElMessage.error('获取设备列表失败');
  } finally {
    loading.value = false;
  }
};

// 搜索设备
const handleSearch = () => {
  currentPage.value = 1;
  fetchEquipments();
};

// 重置搜索表单
const resetSearchForm = () => {
  searchForm.code = '';
  searchForm.name = '';
  searchForm.status = '';
  currentPage.value = 1;
  fetchEquipments();
};

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size;
  fetchEquipments();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  fetchEquipments();
};

// 新增设备
const handleAdd = () => {
  dialogTitle.value = '新增设备';
  currentEquipmentId.value = null;
  Object.assign(equipmentForm, initialEquipmentForm);
  dialogVisible.value = true;
};

// 编辑设备
const handleEdit = (row: Equipment) => {
  dialogTitle.value = '编辑设备';
  currentEquipmentId.value = row.id;
  
  // 重置表单并填充数据
  Object.assign(equipmentForm, initialEquipmentForm);
  
  // 复制行数据到表单
  equipmentForm.code = row.code;
  equipmentForm.name = row.name;
  equipmentForm.model = row.model;
  equipmentForm.specification = row.specification || '';
  equipmentForm.manufacturer = row.manufacturer || '';
  equipmentForm.purchase_date = row.purchase_date || '';
  equipmentForm.purchase_price = row.purchase_price;
  equipmentForm.installation_date = row.installation_date || '';
  equipmentForm.location = row.location || '';
  equipmentForm.responsible_person = row.responsible_person || '';
  equipmentForm.status = row.status;
  equipmentForm.next_maintenance_date = row.next_maintenance_date || '';
  equipmentForm.image = null; // 编辑时不自动加载旧图片
  equipmentForm.remark = row.remark || '';
  
  dialogVisible.value = true;
};

// 查看设备详情
const handleViewDetail = (row: Equipment) => {
  router.push(`/equipment/detail/${row.id}`);
};

// 维保记录
const handleMaintenance = (row: Equipment) => {
  router.push(`/equipment/maintenance/${row.id}`);
};

// 删除设备
const handleDelete = (row: Equipment) => {
  ElMessageBox.confirm(
    `确定要删除设备"${row.name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await equipmentApi.deleteEquipment(row.id);
      ElMessage.success('删除成功');
      fetchEquipments();
    } catch (error) {
      console.error('删除设备失败:', error);
      ElMessage.error('删除设备失败');
    }
  }).catch(() => {
    // 取消删除
  });
};

// 图片处理
const handleImageChange = (file: any) => {
  equipmentForm.image = file.raw;
};

const handleImageRemove = () => {
  equipmentForm.image = null;
};

// 保存设备
const handleSaveEquipment = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return;
    
    submitting.value = true;
    
    try {
      // 创建FormData对象
      const formData = new FormData();
      
      // 添加表单字段
      formData.append('code', equipmentForm.code);
      formData.append('name', equipmentForm.name);
      formData.append('model', equipmentForm.model);
      if (equipmentForm.specification) formData.append('specification', equipmentForm.specification);
      if (equipmentForm.manufacturer) formData.append('manufacturer', equipmentForm.manufacturer);
      if (equipmentForm.purchase_date) formData.append('purchase_date', equipmentForm.purchase_date);
      if (equipmentForm.purchase_price !== undefined) formData.append('purchase_price', equipmentForm.purchase_price.toString());
      if (equipmentForm.installation_date) formData.append('installation_date', equipmentForm.installation_date);
      if (equipmentForm.location) formData.append('location', equipmentForm.location);
      if (equipmentForm.responsible_person) formData.append('responsible_person', equipmentForm.responsible_person);
      formData.append('status', equipmentForm.status);
      if (equipmentForm.next_maintenance_date) formData.append('next_maintenance_date', equipmentForm.next_maintenance_date);
      if (equipmentForm.image) formData.append('image', equipmentForm.image);
      if (equipmentForm.remark) formData.append('remark', equipmentForm.remark);
      
      // 根据是否有ID，决定是创建还是更新
      if (currentEquipmentId.value) {
        await equipmentApi.updateEquipment(currentEquipmentId.value, formData);
        ElMessage.success('更新设备成功');
      } else {
        await equipmentApi.createEquipment(formData);
        ElMessage.success('创建设备成功');
      }
      
      // 关闭对话框并刷新列表
      dialogVisible.value = false;
      fetchEquipments();
    } catch (error) {
      console.error('保存设备失败:', error);
      ElMessage.error('保存设备失败');
    } finally {
      submitting.value = false;
    }
  });
};

// 获取状态对应的Element UI标签类型
const getStatusType = (status: EquipmentStatus): string => {
  const statusMap: Record<EquipmentStatus, string> = {
    normal: 'success',
    maintenance: 'warning',
    inspection: 'info',
    disabled: 'danger'
  };
  return statusMap[status] || 'info';
};

// 获取状态对应的文本显示
const getStatusText = (status: EquipmentStatus): string => {
  const statusMap: Record<EquipmentStatus, string> = {
    normal: '正常',
    maintenance: '维修中',
    inspection: '待检',
    disabled: '停用'
  };
  return statusMap[status] || status;
};

// 页面初始化时加载数据
onMounted(() => {
  fetchEquipments();
});
</script>

<style lang="scss" scoped>
.equipment-container {
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .page-title {
    margin: 0;
    font-size: 18px;
  }
  
  .search-section {
    margin-bottom: 20px;
  }
  
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
  
  .equipment-image-uploader {
    width: 100%;
  }
}
</style> 