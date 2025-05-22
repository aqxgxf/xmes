<template>
  <div class="product-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">产品管理</h2>
          <div class="search-actions">
            <el-input v-model="searchQuery" placeholder="搜索产品" clearable @keyup.enter="handleSearch">
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="openAddDialog">
              <el-icon>
                <Plus />
              </el-icon> 新增产品
            </el-button>
            <el-button type="success" @click="downloadTemplate">
              <el-icon>
                <Download />
              </el-icon> 下载模板
            </el-button>
            <el-button type="success" @click="uploadVisible = true">
              <el-icon>
                <Upload />
              </el-icon> 导入
            </el-button>
          </div>
        </div>
      </template>

      <!-- 批量操作区域 -->
      <div class="batch-actions" v-if="multipleSelection.length > 0">
        <el-alert title="批量操作区域" type="info" :closable="false" show-icon>
          <div class="batch-buttons">
            <span>已选择 {{ multipleSelection.length }} 项</span>
            <el-button size="small" type="danger" @click="confirmBatchDelete">
              <el-icon>
                <Delete />
              </el-icon> 批量删除
            </el-button>
          </div>
        </el-alert>
      </div>

      <!-- 产品列表 -->
      <el-table :data="filteredProducts" v-loading="productStore.isLoading" border stripe style="width: 100%"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="code" label="产品代码" min-width="120" />
        <el-table-column prop="name" label="产品名称" min-width="150" />
        <el-table-column prop="category_name" label="产品类别" min-width="120">
          <template #default="{ row }">
            {{ row.category_name || (row.category ? categoryStore.getCategoryName(row.category) : '') }}
          </template>
        </el-table-column>
        <el-table-column prop="specification" label="规格" min-width="120" />
        <el-table-column prop="price" label="价格" min-width="100">
          <template #default="{ row }">
            {{ row.price === 0 ? '0' : (row.price !== null && row.price !== undefined ? Number(row.price).toFixed(2) :
              '0') }}
          </template>
        </el-table-column>
        <el-table-column prop="unit_name" label="单位" min-width="80" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="创建日期" min-width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="250">
          <template #default="{ row }">
            <el-button type="info" size="small" @click="goToDetail(row)">
              <el-icon><Document /></el-icon> 详情
            </el-button>
            <el-button type="primary" size="small" @click="openEditDialog(row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button type="danger" size="small" @click="confirmDelete(row)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          :current-page="productStore.currentPage"
          :page-size="productStore.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="productStore.totalProducts"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background />
      </div>
    </el-card>

    <!-- 新增/编辑产品对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="产品代码" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="产品名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="产品类别" prop="category">
          <el-select v-model="form.category" placeholder="请选择产品类别" @change="handleCategoryChange" style="width: 100%"
            filterable>
            <el-option v-for="item in categoryStore.categories" :key="item.id"
              :label="`${item.code || ''}-${item.display_name || ''}`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-select v-model="form.unit" placeholder="请选择单位" @change="handleUnitChange" style="width: 100%">
            <el-option v-for="item in productStore.units" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="规格" prop="specification">
          <el-input v-model="form.specification" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input v-model="form.price" type="number" :min="0" :step="0.01" placeholder="请输入价格"
            style="width: 100%; height: 32px;" @input="handlePriceChange" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>

        <!-- 编辑模式下的自动更新选项 -->
        <el-form-item label="" v-if="isEdit && categoryParams.length > 0">
          <el-checkbox v-model="shouldUpdateCodeAndName">
            根据参数值自动更新产品代码和名称
          </el-checkbox>
        </el-form-item>

        <!-- 动态参数项 -->
        <template v-if="categoryParams.length > 0">
          <div class="params-section">
            <h3>产品类参数</h3>
            <el-divider />
            <el-form-item v-for="param in categoryParams" :key="param.id" :label="param.name"
              :prop="'paramValues.' + param.id"
              :rules="{ required: true, message: `请输入${param.name}`, trigger: 'blur' }">
              <el-input v-model="form.paramValues[param.id]" @input="handleParamValueChange" />
            </el-form-item>
          </div>
        </template>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="uploadVisible" title="导入产品" width="600px">
      <el-upload ref="uploadRef" class="upload-container" action="#" :auto-upload="false" :show-file-list="true"
        :limit="1" :on-exceed="() => ElMessage.warning('一次只能上传一个文件')" :before-upload="beforeUpload"
        :http-request="handleUpload">
        <el-button type="primary">
          <el-icon>
            <Upload />
          </el-icon> 选择文件
        </el-button>
        <template #tip>
          <div class="el-upload__tip">
            只能上传xlsx/xls/csv文件，且不超过10MB
          </div>
        </template>
      </el-upload>

      <!-- 导入结果显示 -->
      <div v-if="importResult" class="import-result">
        <el-divider content-position="center">导入结果</el-divider>
        <el-alert :title="importResult.message" :type="importResult.success ? 'success' : 'warning'"
          :description="importResult.details" show-icon />

        <!-- 导入统计信息 -->
        <div class="import-stats">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ importResult.total }}</div>
                <div class="stat-label">总行数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item success">
                <div class="stat-value">{{ importResult.successCount }}</div>
                <div class="stat-label">成功</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item warning">
                <div class="stat-value">{{ importResult.skipped }}</div>
                <div class="stat-label">跳过</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item error">
                <div class="stat-value">{{ importResult.fail }}</div>
                <div class="stat-label">失败</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 详细错误信息 -->
        <div v-if="importResult.error_details && importResult.error_details.length > 0" class="error-details">
          <h4>错误详情：</h4>
          <el-collapse>
            <el-collapse-item title="查看错误详情" name="1">
              <el-table :data="importResult.error_details" border stripe max-height="250">
                <el-table-column prop="row" label="行号" width="80" />
                <el-table-column prop="message" label="错误信息" />
              </el-table>
            </el-collapse-item>
          </el-collapse>
        </div>

        <!-- 重复数据信息 -->
        <div v-if="importResult.duplicate_details && importResult.duplicate_details.length > 0"
          class="duplicate-details">
          <h4>重复数据详情：</h4>
          <el-collapse>
            <el-collapse-item title="查看重复数据" name="1">
              <el-table :data="importResult.duplicate_details" border stripe max-height="250">
                <el-table-column prop="code" label="产品代码" />
                <el-table-column prop="row" label="行号" width="80" />
              </el-table>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadVisible = false">关闭</el-button>
          <el-button v-if="!importResult" type="primary" @click="() => uploadRef?.submit()"
            :loading="productStore.isLoading">
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Plus, Edit, Delete, Download, Upload, Document } from '@element-plus/icons-vue';
import type { FormInstance, FormRules, UploadInstance } from 'element-plus';
import { useProductStore } from '../../../stores/product';
import { useCategoryStore } from '../../../stores/categoryStore';
import { useMaterialStore } from '../../../stores/materialStore'
import { useProductProcessCodeStore } from '../../../stores/productProcessCodeStore'
import { formatDateTime, generateExcelTemplate } from '../../../utils/helpers';
import type { Product, Unit, ProductParam, ProductParamValue } from '../../../types';
import type { ProductCategory } from '../../../types/common';
import api from '../../../api';
import axios from 'axios';
import { applyMaterialRules, createProductProcess, saveProductParamValues } from '../../../utils/productHelper';

// Initialize stores
const productStore = useProductStore();
const categoryStore = useCategoryStore();
const router = useRouter();

// Reactive state
const searchQuery = ref('');
const dialogVisible = ref(false);
const dialogTitle = ref('新增产品');
const isEdit = ref(false);
const submitting = ref(false);
const uploadVisible = ref(false);
const categoryParams = ref<ProductParam[]>([]);
const shouldUpdateCodeAndName = ref(false);
const multipleSelection = ref<Product[]>([]);
const form = ref<Partial<Product> & { paramValues: Record<number, string> }>({
  id: undefined,
  code: '',
  name: '',
  category: undefined,
  category_name: '',
  specification: '',
  description: '',
  unit: undefined,
  unit_name: '',
  price: 0,
  paramValues: {},
});

// 价格验证函数
const validatePrice = (rule: any, value: any, callback: any) => {
  // 转换为数字
  const priceNum = Number(value);
  
  // 检查是否为有效数字
  if (isNaN(priceNum)) {
    callback(new Error('请输入有效的数字'));
  } else if (priceNum < 0) {
    callback(new Error('价格不能小于0'));
  } else {
    // 确保form.value.price存储为数字类型
    form.value.price = priceNum;
    callback();
  }
};

// 处理价格输入变化
const handlePriceChange = (value: string) => {
  // 确保价格值为数字类型
  form.value.price = value === '' ? 0 : Number(value);
};

// 表单验证规则
const rules = ref<FormRules>({
  code: [
    { required: true, message: '请输入产品代码', trigger: 'blur' },
    { max: 50, message: '长度不能超过50个字符', trigger: 'blur' },
  ],
  name: [
    { required: true, message: '请输入产品名称', trigger: 'blur' },
    { max: 100, message: '长度不能超过100个字符', trigger: 'blur' },
  ],
  category: [
    { required: true, message: '请选择产品类别', trigger: 'change' },
  ],
  unit: [
    { required: true, message: '请选择单位', trigger: 'change' },
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    { validator: validatePrice, trigger: 'blur' },
  ],
});

// References
const formRef = ref<FormInstance>();
const uploadRef = ref<UploadInstance>();

// 导入相关状态
const importResult = ref<{
  success: boolean;
  message: string;
  details: string;
  total: number;
  successCount: number;
  fail: number;
  skipped: number;
  error_details?: { row: string; message: string }[];
  duplicate_details?: { code: string; row: string | number }[];
} | null>(null);

// Computed properties
const filteredProducts = computed(() => {
  if (!searchQuery.value) {
    return productStore.products;
  }

  const query = searchQuery.value.toLowerCase();
  return productStore.products.filter(product =>
    product.code.toLowerCase().includes(query) ||
    product.name.toLowerCase().includes(query) ||
    (product.category_name && product.category_name.toLowerCase().includes(query))
  );
});

// Initialize data
onMounted(async () => {
  await Promise.all([
    productStore.fetchProducts(),
    categoryStore.initialize(),
    productStore.fetchUnits()
  ]);
});

// 获取产品参数值
const fetchProductParamValues = async (productId: number) => {
  try {
    console.log(`开始获取产品ID=${productId}的参数值`);
    const response = await api.get('/product-param-values/', {
      params: { product: productId }
    });

    let paramValues: ProductParamValue[] = [];
    if (response.data && response.data.results) {
      paramValues = response.data.results;
      console.log(`获取到${paramValues.length}个参数值`);
    } else if (Array.isArray(response.data)) {
      paramValues = response.data;
      console.log(`获取到${paramValues.length}个参数值`);
    }

    // 清空当前参数值
    form.value.paramValues = {};

    // 打印参数列表和参数值列表，帮助调试
    console.log('产品类参数项列表:', categoryParams.value);
    console.log('产品参数值列表:', paramValues);

    // 额外的产品ID校验，确保只处理当前产品的参数值
    paramValues = paramValues.filter(pv => {
      const isCurrentProduct = pv.product === productId;
      if (!isCurrentProduct) {
        console.warn(`跳过不属于当前产品的参数值: product=${pv.product}, 期望=${productId}`);
      }
      return isCurrentProduct;
    });

    console.log(`过滤后剩余${paramValues.length}个参数值属于当前产品`);

    // 设置从API获取到的参数值
    if (paramValues.length > 0) {
      // 创建参数ID到值的映射，确保每个参数只设置一次（避免重复）
      const paramValueMap = new Map<number, string>();

      paramValues.forEach(pv => {
        // 确保参数ID存在
        if (pv.param) {
          // 只保留最后一个值（如果有重复）
          paramValueMap.set(pv.param, pv.value);
        }
      });

      // 将映射转换回表单值
      paramValueMap.forEach((value, paramId) => {
        // 检查此参数是否在当前产品类的参数列表中
        const paramExists = categoryParams.value.some(param => param.id === paramId);
        if (paramExists) {
          form.value.paramValues[paramId] = value;
          console.log(`设置参数值[${paramId}]=${value}`);
        } else {
          console.warn(`参数ID=${paramId}不在当前产品类的参数列表中，可能产品类发生了变更`);
        }
      });
    } else {
      console.log('未获取到参数值，表单参数值保持为空');
    }
  } catch (error: any) {
    console.error('获取产品参数值失败:', error);
    console.error('错误详情:', error.response?.data || error.message);
    ElMessage.error('获取产品参数值失败');
  }
};

// 获取产品类的参数项
const fetchCategoryParams = async (categoryId: number) => {
  if (!categoryId) return;

  try {
    console.log(`开始获取产品类ID=${categoryId}的参数项`);
    const response = await api.get(`/product-categories/${categoryId}/params/`, {
      params: { page_size: 100 }
    });

    if (response.data && response.data.results) {
      categoryParams.value = response.data.results;
    } else if (Array.isArray(response.data)) {
      categoryParams.value = response.data;
    } else {
      categoryParams.value = [];
    }

    console.log(`获取到${categoryParams.value.length}个参数项`);

    // 初始化参数值对象
    const oldValues = { ...form.value.paramValues }; // 保存原始参数值
    form.value.paramValues = {}; // 重置参数值对象

    // 重新初始化表单的参数值
    categoryParams.value.forEach(param => {
      // 如果有对应的旧值，则保留
      if (oldValues[param.id]) {
        form.value.paramValues[param.id] = oldValues[param.id];
        console.log(`保留原参数值[${param.id}]=${oldValues[param.id]}`);
      } else {
        form.value.paramValues[param.id] = '';
        console.log(`初始化新参数值[${param.id}]=''`);
      }
    });
  } catch (error: any) {
    console.error('获取产品类参数项失败:', error);
    console.error('错误详情:', error.response?.data || error.message);
    ElMessage.error('获取产品类参数项失败');
    categoryParams.value = [];
  }
};

// 监听参数值变化并更新产品代码和名称
const updateProductCodeAndName = () => {
  if (!form.value.category) return;

  const category = categoryStore.categories.find(c => c.id === form.value.category);
  if (!category) return;

  // 判断是否应该更新产品代码和名称
  // 在编辑模式下，只有当用户选择了"自动更新"选项时才更新
  if (!isEdit.value || shouldUpdateCodeAndName.value) {
    // 检查是否所有必填参数值都已填写
    const hasAllParamValues = categoryParams.value.every(param =>
      form.value.paramValues[param.id] && form.value.paramValues[param.id].trim() !== ''
    );

    if (hasAllParamValues && categoryParams.value.length > 0) {
      // 构建参数部分 - 使用参数全称
      const paramParts = categoryParams.value.map(param => {
        // 使用参数的完整名称作为参数项，与参数值用"-"连接
        return `${param.name}-${form.value.paramValues[param.id]}`;
      });

      // 更新产品代码：产品类代码-参数项-参数值
      form.value.code = `${category.code}-${paramParts.join('-')}`;

      // 更新产品名称：产品类名称-参数项-参数值
      form.value.name = `${category.display_name}-${paramParts.join('-')}`;

      // 如果产品代码过长，进行截断处理
      if (form.value.code.length > 100) {
        form.value.code = form.value.code.substring(0, 100);
        ElMessage.warning('产品代码已自动截断，请检查');
      }

      // 如果产品名称过长，进行截断处理
      if (form.value.name.length > 100) {
        form.value.name = form.value.name.substring(0, 100);
        ElMessage.warning('产品名称已自动截断，请检查');
      }
    }
  }
};

// 处理参数值变化
const handleParamValueChange = () => {
  updateProductCodeAndName();
};

// Methods
const handleSearch = () => {
  productStore.fetchProducts({ search: searchQuery.value });
};

const handleSizeChange = (val: number) => {
  productStore.pageSize = val;
  productStore.fetchProducts();
};

const handleCurrentChange = (val: number) => {
  productStore.currentPage = val;
  productStore.fetchProducts();
};

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields();
  }

  form.value = {
    id: undefined,
    code: '',
    name: '',
    category: undefined,
    category_name: '',
    specification: '',
    description: '',
    unit: undefined,
    unit_name: '',
    price: 0,
    paramValues: {},
  };

  // 清空参数项
  categoryParams.value = [];
};

const openAddDialog = () => {
  dialogTitle.value = '新增产品';
  isEdit.value = false;
  resetForm();
  dialogVisible.value = true;
};

const openEditDialog = async (row: Product) => {
  dialogTitle.value = '编辑产品';
  isEdit.value = true;
  shouldUpdateCodeAndName.value = true; // 默认不自动更新

  resetForm();

  console.log('开始编辑产品:', row);

  form.value = {
    id: row.id,
    code: row.code,
    name: row.name,
    category: row.category,
    category_name: row.category_name,
    specification: row.specification || '',
    description: row.description || '',
    unit: row.unit,
    unit_name: row.unit_name,
    price: row.price ? Number(row.price) : 0,  // 确保价格是数字类型
    paramValues: {},
  };

  // 获取产品类参数项
  if (row.category) {
    console.log('产品类ID:', row.category);
    await fetchCategoryParams(row.category);

    // 获取产品参数值
    if (row.id) {
      await fetchProductParamValues(row.id);
    } else {
      console.warn('产品ID不存在，无法获取参数值');
    }
  } else {
    console.warn('产品没有关联的产品类');
  }

  dialogVisible.value = true;
};

const confirmDelete = (row: Product) => {
  ElMessageBox.confirm(
    `确定要删除产品 "${row.name}" 吗？这个操作不可逆。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      await productStore.deleteProduct(row.id);
    })
    .catch(() => {
      // User cancelled
    });
};

// 处理表格多选
const handleSelectionChange = (selection: Product[]) => {
  multipleSelection.value = selection;
};

// 跳转到详情页
const goToDetail = (row: Product) => {
  router.push(`/products/${row.id}/detail`);
};

// 批量删除
const confirmBatchDelete = () => {
  if (multipleSelection.value.length === 0) return;
  ElMessageBox.confirm(
    `确定要删除选中的 ${multipleSelection.value.length} 个产品吗？这个操作不可逆。`,
    '批量删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      for (const product of multipleSelection.value) {
        await productStore.deleteProduct(product.id);
      }
      ElMessage.success('批量删除成功');
      multipleSelection.value = [];
      await productStore.fetchProducts();
    })
    .catch(() => {});
};

// 下载模板功能
const downloadTemplate = () => {
  const headers = ['code', 'name', 'category_code', 'specification', 'description', 'unit_code'];
  const exampleData = [
    ['P001', '产品A', 'CAT001', '规格1', '描述1', 'PCS'],
    ['P002', '产品B', 'CAT002', '规格2', '描述2', 'KG'],
  ];
  generateExcelTemplate(headers, exampleData, '产品导入模板', '产品导入模板.xlsx');
};

// 处理单位选择变化
const handleUnitChange = (value: number) => {
  const unit = productStore.units.find(u => u.id === value);
  if (unit) {
    form.value.unit_name = unit.name;
  }
};

const submitForm = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (!valid) return;

    submitting.value = true;

    try {
      let productData: Product | null = null;
      const productFormData = {
        id: form.value.id,
        code: form.value.code,
        name: form.value.name,
        category: form.value.category,
        category_name: form.value.category_name,
        specification: form.value.specification,
        description: form.value.description,
        unit: form.value.unit,
        unit_name: form.value.unit_name,
        price: form.value.price,
        paramValues: form.value.paramValues,
      };
      if (isEdit.value && form.value.id) {
        productData = await productStore.updateProduct(form.value.id, productFormData);
      } else {
        productData = await productStore.createProduct(productFormData);
        // 新增产品后，先保存参数值，再自动生成BOM物料和工艺流程
        if (productData && productData.id) {
          await saveProductParamValues(productData.id, form.value.paramValues);
          await applyMaterialRules(productData.id);
          await createProductProcess(productData.id);
        }
      }
      // 新增或编辑都保存参数值
      if (productData?.id) {
        await saveProductParamValues(productData.id, form.value.paramValues);
      }
      // ...后续自动生成BOM、工艺流程等

      // 关闭对话框并重新加载产品列表
      dialogVisible.value = false;
      await productStore.fetchProducts();
    } catch (error: any) {
      console.error('保存产品失败:', error);
      console.error('错误响应:', error.response?.data);
      ElMessage.error(`保存产品失败: ${error.response?.data?.detail || '未知错误'}`);
    } finally {
      submitting.value = false;
    }
  });
};

const handleCategoryChange = async (value: number) => {
  const category = categoryStore.categories.find(c => c.id === value) as ProductCategory | undefined;
  if (category) {
    // 更新表单中的单位和规格
    form.value.unit = undefined;
    form.value.unit_name = '';
    form.value.specification = '';

    // 获取产品类的默认单位和规格
    if (category.unit) {
      const defaultUnit = productStore.units.find(u => Number(u.id) === Number(category.unit));
      if (defaultUnit) {
        form.value.unit = defaultUnit.id;
        form.value.unit_name = defaultUnit.name;
      }
    }

    // 获取产品类的参数项
    await fetchCategoryParams(category.id);

    // 如果是编辑状态，且产品ID存在，则获取产品参数值
    if (isEdit.value && form.value.id) {
      await fetchProductParamValues(form.value.id);
    } else {
      // 新增状态下，清空参数值
      form.value.paramValues = {};
    }

    // 更新产品代码和名称
    updateProductCodeAndName();

    console.log('category.unit:', category.unit, typeof category.unit);
    console.log('productStore.units:', productStore.units.map(u => [u.id, typeof u.id]));
  }
};

// 上传相关方法
function beforeUpload(file: File) {
  // 这里可以做文件类型/大小校验，返回true允许上传
  const isExcel = file.type.includes('excel') || file.type.includes('spreadsheet') || file.name.endsWith('.csv');
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isExcel) {
    ElMessage.error('只能上传Excel或CSV文件');
    return false;
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB');
    return false;
  }
  return true;
}

async function handleUpload(option: any) {
  // 这里实现自定义上传逻辑
  // option.file: 当前文件
  // option.onSuccess, option.onError
  try {
    // 例如：调用api上传
    // await api.uploadProductFile(option.file)
    // option.onSuccess()
    ElMessage.success('上传成功（示例）');
    option.onSuccess();
  } catch (e) {
    ElMessage.error('上传失败');
    option.onError(e);
  }
}
</script>

<style scoped>
.product-container {
  padding: 20px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.search-actions {
  display: flex;
  align-items: center;
}

.search-actions el-input {
  width: 300px;
  margin-right: 10px;
}

.search-actions el-button {
  margin-left: 10px;
}

.batch-actions {
  margin-bottom: 20px;
}

.batch-buttons {
  display: flex;
  align-items: center;
}

.batch-buttons span {
  margin-right: 10px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  padding: 10px 20px;
}

.upload-container {
  display: flex;
  align-items: center;
}

.upload-container el-button {
  margin-right: 10px;
}

.import-result {
  margin-top: 20px;
}

.import-stats {
  margin-top: 10px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.error-details,
.duplicate-details {
  margin-top: 10px;
}

.el-collapse-item__header {
  font-weight: bold;
}

.params-section {
  margin-top: 10px;
}

.params-section h3 {
  margin: 0;
  font-size: 18px;
}

.params-section el-divider {
  margin: 10px 0;
}
</style>
