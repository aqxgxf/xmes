<template>
  <el-dialog v-model="dialogVisible" :title="formData.id ? '编辑工单' : '新增工单'" width="600px" @close="onClose"
    destroy-on-close>
    <div v-if="!isFormReady" class="loading-container">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span class="loading-text">加载中...</span>
    </div>
    <el-form v-else :model="formData" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="工单号" prop="workorder_no">
        <el-input v-model="formData.workorder_no" placeholder="请输入工单号" />
      </el-form-item>

      <el-form-item label="订单号" prop="order">
        <el-select v-model="formData.order" filterable placeholder="请选择订单" class="w-full">
          <el-option v-for="order in orders" :key="order.id" :label="order.order_number" :value="order.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="产品" prop="product">
        <el-select v-model="formData.product" filterable placeholder="请选择产品" class="w-full">
          <el-option v-for="product in products" :key="product.id" :label="`${product.code} - ${product.name}`"
            :value="product.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="数量" prop="quantity">
        <el-input-number v-model="formData.quantity" :min="0" class="w-full" />
      </el-form-item>

      <el-form-item label="工艺流程代码" prop="process_code">
        <el-select v-model="formData.process_code" filterable placeholder="请选择工艺流程" class="w-full">
          <el-option v-if="processCodes.length === 0" key="loading" label="加载工艺流程代码中..." value="" disabled />
          <template v-else>
            <el-option v-for="code in processCodes" :key="code.process_code ? code.process_code : code.id" :label="`${code.code || '未命名'} - ${code.version || '未指定'}`" :value="code.process_code ? code.process_code : code.id" />
          </template>
        </el-select>
      </el-form-item>

      <el-form-item label="计划开始" prop="plan_start">
        <el-date-picker v-model="formData.plan_start" type="datetime" class="w-full" />
      </el-form-item>

      <el-form-item label="计划结束" prop="plan_end">
        <el-date-picker v-model="formData.plan_end" type="datetime" class="w-full" />
      </el-form-item>

      <el-form-item label="状态" prop="status">
        <el-select v-model="formData.status" placeholder="请选择状态" class="w-full">
          <el-option v-for="option in statusOptions" :key="option.value" :label="option.label" :value="option.value" />
        </el-select>
      </el-form-item>

      <el-form-item label="备注" prop="remark">
        <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="onClose">取消</el-button>
      <el-button type="primary" :loading="localSubmitting" @click="onSave">保存工单</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useWorkOrderStore } from '../../stores/workOrderStore'
import type { FormInstance } from 'element-plus'
import type { WorkOrderForm } from '../../types/index'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

interface Product {
  id: number;
  code: string;
  name: string;
}

interface ProcessCode {
  id: number;
  code: string;
  version?: string;
  process_code: number;
}

interface Order {
  id: number;
  order_number: string;
}

// 直接接收所有单独的字段
const props = defineProps({
  visible: { type: Boolean, required: true },
  id: { type: Number, default: null },
  workorderNo: { type: String, default: '' },
  orderId: { type: Number, default: 0 },
  productId: { type: Number, default: 0 },
  quantity: { type: Number, default: 0 },
  processCodeId: { type: Number, default: 0 },
  planStart: { type: String, default: '' },
  planEnd: { type: String, default: '' },
  status: { type: String, default: 'draft' },
  remark: { type: String, default: '' },
  products: { type: Array as () => Product[], default: () => [] },
  processCodes: { type: Array as () => ProcessCode[], default: () => [] },
  orders: { type: Array as () => Order[], default: () => [] },
  submitting: { type: Boolean, default: false }
})

const emits = defineEmits(['update:visible', 'saved', 'update:submitting'])

// 表单准备状态
const isFormReady = ref(false)
// 添加一个标记，表示表单数据是否已经通过setFormData方法直接设置过
const isDataDirectlySet = ref(false)

// 本地dialogVisible用于控制对话框显示
const dialogVisible = ref(false)

// 监听props.visible的变化，同步到本地dialogVisible
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  console.log('对话框显示状态变化:', newVal)

  if (newVal) {
    // 对话框打开时初始化表单
    console.log('对话框打开，当前isDataDirectlySet状态:', isDataDirectlySet.value)
    if (!isDataDirectlySet.value) {
      // 延迟初始化，以确保props传递完成
      setTimeout(() => {
        console.log('使用props初始化表单数据:', {
          id: props.id,
          workorderNo: props.workorderNo,
          orderId: props.orderId,
          productId: props.productId,
          quantity: props.quantity,
          processCodeId: props.processCodeId
        })
        initFormData()
      }, 100)
    } else {
      console.log('跳过props初始化，使用直接设置的数据')
    }
  }
})

// 监听本地dialogVisible的变化，同步到父组件
watch(dialogVisible, (newVal) => {
  if (props.visible !== newVal) {
    emits('update:visible', newVal)
  }
})

// 创建表单数据引用
const formData = ref<WorkOrderForm>({
  workorder_no: '',
  order: 0,
  product: 0,
  quantity: 0,
  process_code: 0,
  plan_start: '',
  plan_end: '',
  status: 'draft',
  remark: ''
})

// 设置默认日期
const setDefaultDates = () => {
  const now = new Date()
  const futureDate = new Date()
  futureDate.setDate(now.getDate() + 30)

  formData.value.plan_start = now.toISOString()
  formData.value.plan_end = futureDate.toISOString()
}

// 从props初始化表单数据
const initFormData = () => {
  console.log('开始初始化表单数据，当前props:', {
    id: props.id,
    workorderNo: props.workorderNo,
    orderId: props.orderId,
    productId: props.productId,
    quantity: props.quantity,
    processCodeId: props.processCodeId,
    planStart: props.planStart,
    planEnd: props.planEnd,
    status: props.status,
    remark: props.remark
  })

  // 记录表单正在准备中
  isFormReady.value = false

  // 添加防御性检查，确保所有数据都是预期类型
  formData.value = {
    id: props.id !== undefined && props.id !== null ? Number(props.id) : undefined,
    workorder_no: props.workorderNo !== undefined ? props.workorderNo : '',
    order: props.orderId !== undefined && props.orderId !== null ? Number(props.orderId) : 0,
    product: props.productId !== undefined && props.productId !== null ? Number(props.productId) : 0,
    quantity: props.quantity !== undefined && props.quantity !== null ? Number(props.quantity) : 0,
    process_code: props.processCodeId !== undefined && props.processCodeId !== null ? Number(props.processCodeId) : 0,
    status: props.status !== undefined ? props.status : 'draft',
    remark: props.remark !== undefined ? props.remark : '',
    plan_start: '',
    plan_end: ''
  }

  // 处理日期
  if (props.planStart) {
    try {
      formData.value.plan_start = props.planStart
    } catch (error) {
      console.warn('处理计划开始日期出错，使用当前日期:', error)
      formData.value.plan_start = new Date().toISOString()
    }
  } else {
    formData.value.plan_start = new Date().toISOString()
  }

  if (props.planEnd) {
    try {
      formData.value.plan_end = props.planEnd
    } catch (error) {
      console.warn('处理计划结束日期出错，使用默认日期:', error)
      const futureDate = new Date()
      futureDate.setDate(futureDate.getDate() + 30)
      formData.value.plan_end = futureDate.toISOString()
    }
  } else {
    const futureDate = new Date()
    futureDate.setDate(futureDate.getDate() + 30)
    formData.value.plan_end = futureDate.toISOString()
  }

  console.log('表单数据初始化完成:', JSON.stringify(formData.value))

  // 延迟设置表单就绪状态，确保DOM已更新
  setTimeout(() => {
    isFormReady.value = true
  }, 100)
}

// 直接设置表单数据的方法，供父组件调用
const setFormData = (data: any) => {
  console.log('外部直接设置表单数据:', JSON.stringify(data))
  // 记录表单正在准备中
  isFormReady.value = false

  // 设置标记，表示数据已直接设置，避免被props初始化覆盖
  isDataDirectlySet.value = true

  // 防御性检查
  if (!data) {
    console.error('设置表单数据失败：数据为空')
    isFormReady.value = true
    return
  }

  // 设置基本数据
  formData.value = {
    id: data.id !== undefined && data.id !== null ? Number(data.id) : undefined,
    workorder_no: data.workorder_no !== undefined ? data.workorder_no : '',
    order: data.order !== undefined && data.order !== null ? Number(data.order) : 0,
    product: data.product !== undefined && data.product !== null ? Number(data.product) : 0,
    quantity: data.quantity !== undefined && data.quantity !== null ? Number(data.quantity) : 0,
    process_code: data.process_code !== undefined && data.process_code !== null ? Number(data.process_code) : 0,
    status: data.status !== undefined ? data.status : 'draft',
    remark: data.remark !== undefined ? data.remark : '',
    plan_start: data.plan_start !== undefined ? data.plan_start : new Date().toISOString(),
    plan_end: data.plan_end !== undefined ? data.plan_end : new Date().toISOString()
  }

  console.log('表单数据直接设置完成:', JSON.stringify(formData.value))

  // 延迟标记表单就绪
  setTimeout(() => {
    isFormReady.value = true
  }, 100)
}

// 暴露给父组件的方法
defineExpose({
  setFormData
})

// 获取store
const workOrderStore = useWorkOrderStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
// 本地保存loading状态
const localSubmitting = ref(false)

// 状态选项
const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'print', label: '待打印' },
  { value: 'released', label: '已下达' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]

// 重置表单
const reset = () => {
  formData.value = {
    workorder_no: '',
    order: 0,
    product: 0,
    quantity: 0,
    process_code: 0,
    plan_start: '',
    plan_end: '',
    status: 'draft',
    remark: ''
  }
  setDefaultDates()
  isDataDirectlySet.value = false
}

// 保存工单
const save = async () => {
  loading.value = true
  try {
    // 确保所有数值字段为数字类型
    const saveData: WorkOrderForm = {
      ...formData.value,
      order: Number(formData.value.order) || 0,
      product: Number(formData.value.product) || 0,
      quantity: Number(formData.value.quantity) || 0,
      process_code: Number(formData.value.process_code) || 0
    }

    console.log('准备保存工单数据:', JSON.stringify(saveData))

    let result
    if (saveData.id) {
      result = await workOrderStore.update(saveData.id, saveData)
      ElMessage.success('工单更新成功')
    } else {
      result = await workOrderStore.create(saveData)
      ElMessage.success('工单创建成功')
    }

    console.log('保存结果:', result)
    return true
  } catch (error: any) {
    console.error('保存工单失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
    return false
  } finally {
    loading.value = false
  }
}

const rules = {
  workorder_no: [{ required: true, message: '工单号必填', trigger: 'blur' }],
  order: [{ required: true, message: '订单号必选', trigger: 'change' }],
  product: [{ required: true, message: '产品必选', trigger: 'change' }],
  quantity: [{ required: true, message: '数量必填', trigger: 'blur' }],
  process_code: [{ required: true, message: '工艺流程必选', trigger: 'change' }],
  status: [{ required: true, message: '状态必选', trigger: 'change' }]
}

const onSave = async () => {
  if (!formRef.value) {
    console.error('表单引用未找到')
    ElMessage.error('表单引用错误，请刷新页面重试')
    return
  }

  try {
    // 表单验证
    const valid = await formRef.value.validate()
    if (!valid) {
      console.error('表单验证失败')
      return
    }

    // 通知父组件提交中状态变化
    emits('update:submitting', true)
    localSubmitting.value = true

    // 保存数据
    const success = await save()

    if (success) {
      // 触发保存成功事件
      emits('saved')
      dialogVisible.value = false
    }
  } catch (error) {
    console.error('表单验证或保存失败:', error)
    ElMessage.error('保存失败，请检查表单并重试')
  } finally {
    // 通知父组件提交结束
    emits('update:submitting', false)
    localSubmitting.value = false
  }
}

const onClose = () => {
  reset()
  dialogVisible.value = false
}

// 添加组件挂载时的初始化逻辑
onMounted(() => {
  // 如果对话框已打开，初始化表单
  if (props.visible && !isDataDirectlySet.value) {
    console.log('组件挂载时初始化表单')
    initFormData()
  }

  // 确保对话框状态同步
  dialogVisible.value = props.visible
})

// 监听processCodes属性变化，记录工艺流程代码数据
watch(() => props.processCodes, (newProcessCodes) => {
  console.log(`工艺流程代码数据更新，当前有${newProcessCodes?.length || 0}条数据`)
  if (newProcessCodes && newProcessCodes.length > 0) {
    console.log('工艺流程代码示例数据:', newProcessCodes.slice(0, 3))
  } else {
    console.warn('工艺流程代码数据为空')
  }
}, { immediate: true })

// 在isFormReady变为true时检查重要表单数据
watch(isFormReady, (newValue) => {
  if (newValue) {
    console.log('表单已就绪，重要数据状态:')
    console.log(`- 工艺流程代码: ${formData.value.process_code}`)
    console.log(`- 工艺流程代码列表长度: ${props.processCodes?.length || 0}`)
    console.log(`- 产品ID: ${formData.value.product}`)
    console.log(`- 产品列表长度: ${props.products?.length || 0}`)
  }
})
</script>

<style scoped>
.w-full {
  width: 100%;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.loading-container .el-icon {
  font-size: 32px;
  color: #409EFF;
  margin-bottom: 16px;
}

.loading-text {
  color: #606266;
  font-size: 14px;
}
</style>
