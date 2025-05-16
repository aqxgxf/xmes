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
        <el-table-column fixed="right" label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openEditDialog(row)">
              <el-icon>
                <Edit />
              </el-icon> 编辑
            </el-button>
            <el-button type="danger" size="small" @click="confirmDelete(row)">
              <el-icon>
                <Delete />
              </el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination :current-page="productStore.currentPage" :page-size="productStore.pageSize"
          @update:current-page="val => productStore.currentPage = val" 
          @update:page-size="val => productStore.pageSize = val"
          :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper"
          :total="productStore.totalProducts" @size-change="handleSizeChange" @current-change="handleCurrentChange"
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
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Plus, Edit, Delete, Download, Upload } from '@element-plus/icons-vue';
import type { FormInstance, FormRules, UploadInstance } from 'element-plus';
import { useProductStore } from '../../../stores/product';
import { useCategoryStore } from '../../../stores/categoryStore';
import { formatDateTime, generateExcelTemplate } from '../../../utils/helpers';
import type { Product, Unit, ProductParam, ProductParamValue } from '../../../types';
import type { ProductCategory } from '../../../types/common';
import api from '../../../api';
import axios from 'axios';

// Initialize stores
const productStore = useProductStore();
const categoryStore = useCategoryStore();

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
      if (form.value.code.length > 50) {
        form.value.code = form.value.code.substring(0, 50);
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

const submitForm = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (!valid) return;

    submitting.value = true;

    try {
      let productData: Product | null = null;

      // 创建临时产品数据对象，只包含必要字段，不包含参数值
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
        price: form.value.price ? Number(form.value.price) : 0  // 确保价格是数字类型
      };

      console.log('保存产品数据:', productFormData);

      if (isEdit.value && form.value.id) {
        // 更新现有产品
        productData = await productStore.updateProduct(form.value.id, productFormData);
        console.log('更新产品成功, 返回数据:', productData);
      } else {
        // 创建新产品
        productData = await productStore.createProduct(productFormData);
        console.log('创建产品成功, 返回数据:', productData);
      }

      // 保存参数值 - 确保有产品ID
      if (productData && productData.id) {
        console.log('开始保存参数值, 产品ID:', productData.id);

        try {
          // 构建参数值数组
          const paramValuesArray = Object.entries(form.value.paramValues).map(([paramId, value]) => ({
            product: productData.id,
            param: parseInt(paramId),
            value: value.toString()
          }));

          if (paramValuesArray.length > 0) {
            // 如果是编辑模式，先删除旧的参数值
            if (isEdit.value) {
              try {
                // 获取当前产品的所有参数值
                const response = await api.get('/product-param-values/', {
                  params: { product: productData.id }
                });

                // 如果有参数值，则删除它们
                if (response.data && response.data.results) {
                  const deletePromises = response.data.results.map((pv: ProductParamValue) =>
                    api.delete(`/product-param-values/${pv.id}/`)
                  );
                  await Promise.all(deletePromises);
                }
              } catch (error) {
                console.error('清除旧参数值失败:', error);
              }
            }

            let successCount = 0;

            // 批量保存所有参数值
            try {
              // 逐个保存参数值，确保每个请求都正确格式化
              for (const paramValue of paramValuesArray) {
                try {
                  console.log('保存参数值:', paramValue);
                  const response = await api.post('/product-param-values/', paramValue);

                  if (response.status === 201 || response.status === 200) {
                    successCount++;
                  }
                } catch (paramError: any) {
                  console.error('单个参数值保存失败:', paramError);
                  if (paramError.response) {
                    console.error('错误详情:', {
                      status: paramError.response.status,
                      data: paramError.response.data
                    });
                  }
                }
              }
            } catch (batchError) {
              console.error('批量保存参数值失败:', batchError);
            }

            if (successCount === paramValuesArray.length) {
              ElMessage.success('产品和参数值保存成功');
            } else if (successCount > 0) {
              ElMessage.warning(`产品保存成功，但只有 ${successCount}/${paramValuesArray.length} 个参数值保存成功`);
            } else {
              ElMessage.warning('产品保存成功，但参数值保存失败');
            }
          } else {
            ElMessage.success('产品保存成功');
          }
        } catch (paramError) {
          console.error('保存参数值失败:', paramError);
          ElMessage.warning('产品已保存，但参数值保存失败');
        }
      } else {
        console.error('未能获取有效的产品ID，无法保存参数值');
        ElMessage.warning('产品已保存，但无法保存参数值');
      }

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
    form.value.category_name = `${category.code}-${category.display_name}`;

    // 清空之前的参数值和产品代码、名称
    form.value.paramValues = {};

    // 如果产品类有单位，自动设置产品单位
    if (category.unit) {
      form.value.unit = category.unit;

      // 查找并设置单位名称
      const unit = productStore.units.find(u => u.id === category.unit);
      if (unit) {
        form.value.unit_name = unit.name;
      }
    }

    if (!isEdit.value) {
      // 如果是新增模式，清空代码和名称，等待参数填写后自动生成
      form.value.code = '';
      form.value.name = '';
    }

    // 加载该产品类的参数项
    await fetchCategoryParams(value);
  }
};

const handleUnitChange = (value: number) => {
  const unit = productStore.units.find(u => u.id === value) as Unit | undefined;
  if (unit) {
    form.value.unit_name = unit.name;
  }
};

const downloadTemplate = () => {
  const headers = ['code', 'name', 'category_code', 'specification', 'description', 'unit_code'];
  const exampleData = [
    ['P001', '产品A', 'CAT001', '规格1', '描述1', 'PCS'],
    ['P002', '产品B', 'CAT002', '规格2', '描述2', 'KG'],
  ];

  generateExcelTemplate(headers, exampleData, '产品导入模板', '产品导入模板.xlsx');
};

const beforeUpload = (file: File) => {
  const validExtensions = ['.xlsx', '.xls', '.csv'];
  const extension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

  if (!validExtensions.includes(extension)) {
    ElMessage.error('仅支持 .xlsx, .xls, .csv 文件格式');
    return false;
  }

  return true;
};

const handleUpload = async (option: any) => {
  const { file } = option;
  importResult.value = null;

  try {
    const response = await productStore.importProducts(file);

    if (response) {
      // 格式化导入结果
      importResult.value = {
        success: true,
        message: '导入完成',
        details: `总共${response.total || 0}行数据，成功${response.success || 0}行，失败${response.fail || 0}行，跳过${response.skipped || 0}行`,
        total: response.total || 0,
        successCount: response.success || 0,
        fail: response.fail || 0,
        skipped: response.skipped || 0,
        error_details: [],
        duplicate_details: []
      };

      // 处理错误信息
      if (response.fail_msgs && response.fail_msgs.length > 0) {
        if (importResult.value) {
          importResult.value.error_details = response.fail_msgs.map((msg: string) => {
            const matches = msg.match(/第(\d+)行: (.*)/);
            return {
              row: matches ? matches[1] : '-',
              message: matches ? matches[2] : msg
            };
          });
        }
      }

      // 处理重复数据
      if (response.duplicate_codes && response.duplicate_codes.length > 0) {
        if (importResult.value) {
          importResult.value.duplicate_details = response.duplicate_codes.map((code: string) => {
            const info = response.processed_data && response.processed_data[code]
              ? response.processed_data[code]
              : { row: '-' };
            return {
              code: code,
              row: info.row
            };
          });
        }
      }
    } else {
      importResult.value = {
        success: false,
        message: '导入失败',
        details: '服务器未返回有效响应',
        total: 0,
        successCount: 0,
        fail: 0,
        skipped: 0
      };
    }
  } catch (error: any) {
    console.error('Import failed:', error);

    importResult.value = {
      success: false,
      message: '导入失败',
      details: error.response?.data?.msg || error.message || '未知错误',
      total: 0,
      successCount: 0,
      fail: 0,
      skipped: 0
    };
  }
};

// 处理多选变化
const handleSelectionChange = (selection: Product[]) => {
  multipleSelection.value = selection;
  console.log('已选择产品:', selection.length);
};

// 批量删除产品
const confirmBatchDelete = () => {
  if (multipleSelection.value.length === 0) return;

  // 保存选中项的数量，避免异步操作过程中值被改变
  const selectedCount = multipleSelection.value.length;
  const selectedItems = [...multipleSelection.value];

  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedCount} 个产品吗？这个操作不可逆。`,
    '批量删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      submitting.value = true;
      try {
        // 先获取总数，用于计算页码调整
        const totalBeforeDelete = productStore.totalProducts;
        const totalPagesBefore = Math.ceil(totalBeforeDelete / productStore.pageSize);
        
        // 删除第一个项目时，store里的deleteProduct会处理页码和数据刷新
        if (selectedItems.length > 0) {
          await productStore.deleteProduct(selectedItems[0].id);
        }
        
        // 删除其余项目，但不自动刷新页面（避免多次刷新）
        if (selectedItems.length > 1) {
          const remainingDeletePromises = selectedItems.slice(1).map(product =>
            api.delete(`/products/${product.id}/`)
          );
          await Promise.all(remainingDeletePromises);
          
          // 计算删除后预计的总数和总页数
          const expectedRemainingItems = totalBeforeDelete - selectedCount;
          const expectedTotalPages = Math.ceil(expectedRemainingItems / productStore.pageSize);
          
          // 如果当前页超出了预计的总页数，调整到有效页码
          if (expectedTotalPages > 0 && productStore.currentPage > expectedTotalPages) {
            productStore.currentPage = expectedTotalPages;
          } else if (expectedTotalPages === 0) {
            productStore.currentPage = 1;
          }
          
          // 使用调整后的页码刷新数据
          await productStore.fetchProducts();
        }
        
        ElMessage.success(`成功删除 ${selectedCount} 个产品`);
        // 清空选择
        multipleSelection.value = [];
      } catch (error) {
        console.error('批量删除失败:', error);
        ElMessage.error('批量删除失败，请重试');
      } finally {
        submitting.value = false;
      }
    })
    .catch(() => {
      // 用户取消删除
    });
};
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.product-container {
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page-title {
    margin: 0;
    font-size: 18px;
  }

  .search-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }

  .upload-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .params-section {
    margin-top: 10px;
    border-top: 1px solid #ebeef5;
    padding-top: 10px;

    h3 {
      font-size: 14px;
      margin-bottom: 6px;
      color: #303133;
    }

    .el-form-item {
      margin-bottom: 8px !important;

      :deep(.el-form-item__content) {
        line-height: 24px !important;
      }

      :deep(.el-input),
      :deep(.el-select) {
        height: 24px !important;

        .el-input__inner {
          height: 24px !important;
          line-height: 24px !important;
        }
      }
    }
  }

  // 批量操作区域样式
  .batch-actions {
    margin-bottom: 16px;

    .batch-buttons {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
    }
  }

  .import-result {
    margin-top: 20px;
    padding: 20px;
    background-color: #fff;

    .import-stats {
      margin-top: 20px;
      margin-bottom: 20px;

      .stat-item {
        text-align: center;

        .stat-value {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 5px;
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
        }
      }

      .success {
        .stat-value {
          color: #67C23A;
        }
      }

      .warning {
        .stat-value {
          color: #E6A23C;
        }
      }

      .error {
        .stat-value {
          color: #F56C6C;
        }
      }
    }

    .error-details,
    .duplicate-details {
      margin-top: 20px;

      h4 {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
      }
    }
  }

  .el-dialog {
    padding: 12px 18px !important;

    .el-form {
      .el-form-item {
        margin-bottom: 10px !important;

        label {
          min-width: 80px !important;
          font-size: 13px;
        }

        .el-input,
        .el-select,
        .el-input-number {
          height: 30px !important;
          font-size: 13px;
        }

        .el-input__inner {
          height: 30px !important;
          line-height: 30px !important;
        }
      }
    }
  }

  .action-buttons {
    display: flex;
    flex-direction: row;
    gap: 6px;
    align-items: center;
    justify-content: flex-start;
    flex-wrap: nowrap;

    .el-button {
      white-space: nowrap;
      padding: 0 8px;
      font-size: 13px;
      height: 28px;
    }
  }
}
</style>
