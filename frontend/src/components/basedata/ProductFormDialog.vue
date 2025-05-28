<template>
  <el-dialog
    :model-value="props.visible"
    :title="props.title"
    width="500px"
    destroy-on-close
    @update:modelValue="emit('update:visible', $event)"
    @close="handleCloseDialogInternal"
  >
    <el-form ref="formRef" :model="formState" :rules="formRules" label-width="100px">
      <el-form-item label="产品代码" prop="code">
        <el-input v-model="formState.code" />
      </el-form-item>
      <el-form-item label="产品名称" prop="name">
        <el-input v-model="formState.name" />
      </el-form-item>
      <el-form-item label="产品类别" prop="category">
        <el-select v-model="formState.category" placeholder="请选择产品类别" @change="onCategoryChange" style="width: 100%" filterable>
          <el-option
            v-for="item in categoryStore.categories"
            :key="item.id"
            :label="`${item.code || ''}-${item.display_name || ''}`"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="单位" prop="unit">
        <el-select v-model="formState.unit" placeholder="请选择单位" @change="onUnitChange" style="width: 100%">
          <el-option
            v-for="item in productStore.units"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="规格" prop="specification">
        <el-input v-model="formState.specification" />
      </el-form-item>
      <el-form-item label="价格" prop="price">
        <el-input v-model.number="formState.price" type="number" :min="0" :step="0.01" placeholder="请输入价格" style="width: 100%; height: 32px;" @input="onPriceInputChange" />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="formState.description" type="textarea" :rows="3" />
      </el-form-item>

      <el-form-item label="" v-if="isEditModeComputed && localCategoryParams.length > 0">
        <el-checkbox v-model="localShouldUpdateCodeAndName">
          根据参数值自动更新产品代码和名称
        </el-checkbox>
      </el-form-item>

      <template v-if="localCategoryParams.length > 0">
        <div class="params-section">
          <h3>产品类参数</h3>
          <el-divider />
          <el-form-item
            v-for="param in localCategoryParams"
            :key="param.id"
            :label="param.name"
            :prop="'paramValues.' + param.id"
            :rules="{ required: true, message: `请输入${param.name}`, trigger: 'blur' }"
          >
            <el-input v-model="formState.paramValues[param.id]" @input="onParamValueChange" />
          </el-form-item>
        </div>
      </template>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleCloseDialogInternal">取消</el-button>
        <el-button type="primary" @click="handleSubmitForm" :loading="props.isSubmitting">
          确定
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue';
import { ElMessage } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { useProductStore } from '../../stores/product';
import { useCategoryStore } from '../../stores/categoryStore';
import type { Product, Unit, ProductParam, ProductParamValue, ProductCategory } from '../../types';
import api from '../../api';

// Props definition
const props = defineProps<{
  visible: boolean;
  title: string;
  productData?: Product | null;
  isSubmitting: boolean;
}>();

// Emits definition
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void;
  (e: 'save', productFormData: Partial<Product> & { paramValues: Record<number, string> }): void;
  (e: 'close'): void;
}>();

// Store instances
const productStore = useProductStore();
const categoryStore = useCategoryStore();

// Refs for form and internal state
const formRef = ref<FormInstance | null>(null);
const formState = ref<Partial<Product> & { paramValues: Record<number, string> }>({
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
const localCategoryParams = ref<ProductParam[]>([]);
const localShouldUpdateCodeAndName = ref(false);

const isEditModeComputed = computed(() => !!props.productData && !!props.productData.id);

const validatePrice = (rule: any, value: any, callback: any) => {
  const priceNum = Number(value);
  if (value === '' || value === null || value === undefined) {
    callback();
    return;
  }
  if (isNaN(priceNum)) {
    callback(new Error('请输入有效的数字'));
  } else if (priceNum < 0) {
    callback(new Error('价格不能小于0'));
  } else {
    formState.value.price = priceNum;
    callback();
  }
};

const formRules = ref<FormRules>({
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
    { validator: validatePrice, trigger: 'input' },
  ],
});

const internalResetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields();
  }
  formState.value = {
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
  localCategoryParams.value = [];
  localShouldUpdateCodeAndName.value = false;
};

const internalFillForm = (product: Product) => {
  formState.value = {
    id: product.id,
    code: product.code,
    name: product.name,
    category: product.category,
    category_name: product.category_name,
    specification: product.specification || '',
    description: product.description || '',
    unit: product.unit,
    unit_name: product.unit_name,
    price: product.price ? Number(product.price) : 0,
    paramValues: {},
  };
};

const internalFetchCategoryParams = async (categoryId: number) => {
  if (!categoryId) return;
  try {
    const response = await api.get(`/product-categories/${categoryId}/params/`, { 
      params: { 
        page_size: 100, 
        ordering: 'display_order' 
      } 
    });
    localCategoryParams.value = response.data?.results || response.data || [];
    const oldValues = { ...formState.value.paramValues };
    const newParamValues: Record<number, string> = {};
    localCategoryParams.value.forEach((param: ProductParam) => {
      newParamValues[param.id] = oldValues[param.id] || '';
    });
    formState.value.paramValues = newParamValues;
  } catch (error) {
    ElMessage.error('获取产品类参数项失败');
    localCategoryParams.value = [];
  }
};

const internalFetchProductParamValues = async (productId: number) => {
  if (!productId || !localCategoryParams.value || localCategoryParams.value.length === 0) {
    formState.value.paramValues = {};
    return;
  }
  try {
    const response = await api.get('/product-param-values/', { params: { product: productId, page_size: 500 } });
    let paramValuesData: ProductParamValue[] = response.data?.results || response.data || [];
    const newParamValues: Record<number, string> = {};
    localCategoryParams.value.forEach((catParam: ProductParam) => {
        const foundPv = paramValuesData.find(pv => pv.product === productId && pv.param === catParam.id);
        newParamValues[catParam.id] = foundPv ? foundPv.value : '';
    });
    formState.value.paramValues = newParamValues;
  } catch (error) {
    ElMessage.error('获取产品参数值失败');
    const newParamValuesOnError: Record<number, string> = {};
    localCategoryParams.value.forEach((param: ProductParam) => {
      newParamValuesOnError[param.id] = '';
    });
    formState.value.paramValues = newParamValuesOnError;
  }
};

const internalUpdateProductCodeAndName = () => {
  if (!formState.value.category) return;
  const category = categoryStore.categories.find(c => c.id === formState.value.category);
  if (!category) return;

  if (!isEditModeComputed.value || localShouldUpdateCodeAndName.value) {
    const hasAllParamValues = localCategoryParams.value.every((param: ProductParam) =>
      formState.value.paramValues[param.id] && String(formState.value.paramValues[param.id]).trim() !== ''
    );
    if (hasAllParamValues && localCategoryParams.value.length > 0) {
      const paramParts = localCategoryParams.value.map((param: ProductParam) => `${param.name}-${formState.value.paramValues[param.id]}`);
      const newCode = `${category.code}-${paramParts.join('-')}`;
      const newName = `${category.display_name}-${paramParts.join('-')}`;

      formState.value.code = newCode.substring(0, 100);
      formState.value.name = newName.substring(0, 100);

      if (newCode.length > 100) ElMessage.warning('产品代码已自动截断至100字符，请检查');
      if (newName.length > 100) ElMessage.warning('产品名称已自动截断至100字符，请检查');
    }
  }
};

const onParamValueChange = () => {
  internalUpdateProductCodeAndName();
};

const onCategoryChange = async (categoryId: number | undefined) => {
  if (!categoryId) {
    localCategoryParams.value = [];
    formState.value.paramValues = {};
    formState.value.unit = undefined;
    formState.value.unit_name = '';
    return;
  }
  const category = categoryStore.categories.find(c => c.id === categoryId);
  if (category) {
    if (productStore.units.length === 0) await productStore.fetchUnits();
    await nextTick();

    formState.value.unit = undefined;
    formState.value.unit_name = '';
    formState.value.specification = '';

    let unitIdToSet: number | undefined = undefined;
    const categoryUnitField = category.unit;

    if (categoryUnitField && typeof categoryUnitField === 'object' && categoryUnitField.id) {
        unitIdToSet = categoryUnitField.id;
    } else if (typeof categoryUnitField === 'number') {
        unitIdToSet = categoryUnitField;
    }

    if (unitIdToSet !== undefined) {
        const defaultUnit = productStore.units.find((u: Unit) => u.id === unitIdToSet);
        if (defaultUnit) {
            formState.value.unit = defaultUnit.id;
            formState.value.unit_name = defaultUnit.name;
        }
    } else {
        formState.value.unit = undefined;
        formState.value.unit_name = '';
    }

    await internalFetchCategoryParams(category.id);
    if (isEditModeComputed.value && formState.value.id) {
      await internalFetchProductParamValues(formState.value.id);
    } else {
      const newParamValuesForAdd: Record<number, string> = {};
      localCategoryParams.value.forEach((param: ProductParam) => {
        newParamValuesForAdd[param.id] = '';
      });
      formState.value.paramValues = newParamValuesForAdd;
    }
    internalUpdateProductCodeAndName();
  }
};

const onUnitChange = (unitId: number | undefined) => {
  const unit = productStore.units.find((u: Unit) => u.id === unitId);
  formState.value.unit_name = unit ? unit.name : '';
};

const onPriceInputChange = (value: string | number) => {
  if (value === '' || value === null || value === undefined) {
      formState.value.price = 0;
  } else {
      formState.value.price = Number(value);
  }
};

watch(() => props.visible, async (newVal) => {
  if (newVal) {
    internalResetForm();
    if (categoryStore.categories.length === 0) {
        await categoryStore.initialize();
    }
    if (productStore.units.length === 0) {
        await productStore.fetchUnits();
    }

    if (props.productData && props.productData.id) {
      internalFillForm(props.productData);
      localShouldUpdateCodeAndName.value = false;
      if (props.productData.category) {
        await internalFetchCategoryParams(props.productData.category);
        if(formState.value.id) {
            await internalFetchProductParamValues(formState.value.id);
        }
      }
    } else {
      localShouldUpdateCodeAndName.value = true;
      formState.value.paramValues = {};
    }
  }
});

const handleCloseDialogInternal = () => {
  emit('update:visible', false);
  emit('close');
};

const handleSubmitForm = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      const finalFormData = {
        ...formState.value,
        price: Number(formState.value.price) || 0
      };
      emit('save', finalFormData);
    } else {
      ElMessage.error('请检查表单输入项。');
    }
  });
};

</script>

<style scoped>
.params-section {
  margin-top: 10px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}
.params-section h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
}
.dialog-footer {
  text-align: right;
}
</style> 