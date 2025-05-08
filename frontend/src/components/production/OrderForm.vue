<template>
  <FormContainer
    :model-value="modelValue"
    :rules="orderRules"
    :loading="loading"
    @submit="submitForm"
  >
    <el-form-item label="产品" prop="product_id">
      <el-select v-model="modelValue.product_id" placeholder="选择产品" style="width: 100%">
        <el-option
          v-for="product in products"
          :key="product.id"
          :label="product.name"
          :value="product.id"
        />
      </el-select>
    </el-form-item>
    
    <el-form-item label="客户" prop="customer_id">
      <el-select v-model="modelValue.customer_id" placeholder="选择客户" style="width: 100%">
        <el-option
          v-for="customer in customers"
          :key="customer.id"
          :label="customer.name"
          :value="customer.id"
        />
      </el-select>
    </el-form-item>
    
    <el-form-item label="数量" prop="quantity">
      <el-input-number v-model="modelValue.quantity" :min="1" style="width: 100%" />
    </el-form-item>
    
    <el-form-item label="交付日期" prop="delivery_date">
      <el-date-picker
        v-model="modelValue.delivery_date"
        type="date"
        placeholder="选择日期"
        style="width: 100%"
        value-format="YYYY-MM-DD"
      />
    </el-form-item>
    
    <el-form-item label="备注" prop="notes">
      <el-input
        v-model="modelValue.notes"
        type="textarea"
        placeholder="输入备注"
        :rows="3"
      />
    </el-form-item>
  </FormContainer>
</template>

<script lang="ts" setup>
import { defineProps, defineEmits, computed } from 'vue'
import FormContainer from '../common/FormContainer.vue'
import { validationRules } from '../../utils/validation'
import { formatDate } from '../../utils/dateFormatter'

// 定义生产订单接口
export interface OrderFormData {
  id: number | null;
  product_id: string | number;
  customer_id: string | number;
  quantity: number;
  delivery_date: string | Date;
  notes: string;
}

// 组件属性
const props = defineProps<{
  modelValue: OrderFormData;
  loading?: boolean;
  products: any[];
  customers: any[];
}>()

const emit = defineEmits<{
  (e: 'submit', form: OrderFormData): void;
}>()

// 表单验证规则
const orderRules = {
  product_id: [validationRules.required('请选择产品')],
  customer_id: [validationRules.required('请选择客户')],
  quantity: [
    validationRules.required('请输入数量'),
    validationRules.numberRange(1, 99999)
  ],
  delivery_date: [validationRules.required('请选择交付日期')]
}

// 表单提交
const submitForm = () => {
  // 确保日期格式正确
  const formData = {
    ...props.modelValue,
    delivery_date: formatDate(props.modelValue.delivery_date) || new Date().toISOString().split('T')[0]
  }
  
  emit('submit', formData)
}
</script> 