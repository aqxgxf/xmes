import { reactive, ref, watchEffect } from 'vue'
import type { UploadUserFile, FormInstance } from 'element-plus'
import type { ProcessCodeForm, Product, ProductCategory } from '../types/common'
import { useProcessCodeStore } from '../stores/processCodeStore'
/**
 * 工艺流程代码表单处理逻辑组合式函数
 */
export function useProcessCodeForm() {
  // 表单对象
  const form = reactive<ProcessCodeForm>({
    id: null,
    code: '',
    description: '',
    version: '',
    process_pdf: '',
    category: null
  })

  // 表单验证规则
  const rules = {
    code: [
      { required: true, message: '请输入工艺流程代码', trigger: ['blur', 'change'] },
      { max: 50, message: '最大长度不能超过50个字符', trigger: ['blur', 'change'] }
    ],
    version: [
      { required: true, message: '请选择版本', trigger: ['blur', 'change'] }
    ],
    category: [
      { required: true, message: '请选择产品类', trigger: ['blur', 'change'] }
    ]
  }

  // PDF文件列表
  const pdfFileList = ref<UploadUserFile[]>([])

  // 获取产品类列表（从store获取，保证响应式）
  const processCodeStore = useProcessCodeStore()
  const categories = processCodeStore.categories

  // 重置表单
  const resetForm = () => {
    form.id = null
    form.code = ''
    form.description = ''
    form.version = ''
    form.process_pdf = ''
    form.category = null
    pdfFileList.value = []
  }

  // 自动更新code和description（基于产品类和版本）
  const updateCodeByProductAndVersion = (categories: ProductCategory[] = []) => {
    if (form.category && form.version) {
      // 根据产品类生成代码
      const category = categories.find(c => c.id === form.category)
      if (category) {
        form.code = category.code + '-' + form.version
        if (form.description === '' && form.code !== '') {
          form.description = category?.code + '-' + category?.display_name + '-' + form.version
        }
      }
    } else {
      form.code = ''
    }
  }

  // 根据产品类更新代码
  const updateCodeByCategory = (categoryId: number, categories: ProductCategory[], version: string = '') => {
    form.category = categoryId
    
    if (version) {
      form.version = version
    }
    
    if (form.category && form.version) {
      const category = categories.find(c => c.id === form.category)
      if (category) {
        form.code = category.code + '-' + form.version
        if (form.description === '' && form.code !== '') {
          form.description = category?.code + '-' + category?.display_name + '-' + form.version
        }
      }
    }
  }

  // 新增：处理产品类变更
  function handleCategoryChange(categoryId: number) {
    form.category = categoryId
    updateCodeByProductAndVersion(categories)
  }

  // 新增：处理版本号变更
  function handleVersionChange(version: string) {
    form.version = version
    updateCodeByProductAndVersion(categories)
  }

  const formRef = ref<FormInstance>()

  // 新增：表单校验方法
  async function validateForm() {
    if (!formRef.value) return false
    let valid = false
    try {
      valid = await formRef.value.validate()
    } catch (err) {
      // 旧逻辑，保留
      if (err && typeof err === 'object') {
        try {
          console.error('表单校验错误详情(JSON):', JSON.stringify(err, null, 2))
        } catch (e) {}
        console.error('表单校验错误详情(原始):', err)
        if (err instanceof Object) {
          Object.entries(err).forEach(([field, errors]) => {
            console.error(`字段【${field}】校验未通过:`, errors)
          })
        }
      }
    }
    if (!valid && formRef.value && Array.isArray(formRef.value.fields)) {
      formRef.value.fields.forEach((field: any) => {
        if (field && field.prop) {
          console.error(
            `字段【${field.prop}】校验状态:`,
            field.validateState,
            '错误信息:',
            field.validateMessage
          )
        }
      })
    }
    if (!valid && formRef.value) {
      // 输出整个formRef.value对象
      console.error('formRef.value内容:', formRef.value)
      // 尝试递归输出所有属性
      const refObj = formRef.value as Record<string, any>;
      for (const key in refObj) {
        if (Object.prototype.hasOwnProperty.call(refObj, key)) {
          console.error(`formRef.value[${key}]:`, refObj[key])
        }
      }
    }
    return valid
  }

  // 格式化表单数据，供保存/提交使用
  function prepareFormData() {
    const data = { ...form }
    const formData = new FormData()
    // 普通字段
    const dataObj = data as Record<string, any>;
    for (const key in dataObj) {
      if (dataObj[key] !== undefined && dataObj[key] !== null) {
        formData.append(key, dataObj[key])
      }
    }
    // 处理 PDF 文件（如果有）
    if (pdfFileList.value.length > 0 && pdfFileList.value[0].raw) {
      formData.set('process_pdf', pdfFileList.value[0].raw)
    }
    return formData
  }

  // 编辑时填充表单
  function fillForm(data: Partial<ProcessCodeForm>) {
    form.id = data.id ?? null
    form.code = data.code ?? ''
    form.description = data.description ?? ''
    form.version = data.version ?? ''
    form.process_pdf = data.process_pdf ?? ''
    form.category = data.category ?? null
    // 如果有文件，自动填充 pdfFileList
    if (data.process_pdf && typeof data.process_pdf === 'string') {
      pdfFileList.value = [{
        name: '工艺PDF',
        url: data.process_pdf,
        status: 'done'
      } as any]
    } else {
      pdfFileList.value = []
    }
  }

  return {
    form,
    rules,
    pdfFileList,
    resetForm,
    updateCodeByProductAndVersion,
    updateCodeByCategory,
    handleCategoryChange,
    handleVersionChange,
    formRef,
    validateForm,
    prepareFormData,
    fillForm
  }
}
