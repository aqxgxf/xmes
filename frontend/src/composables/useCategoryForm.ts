import { reactive } from 'vue'
import type { ProductCategoryForm } from '../types/common'

/**
 * 产品类表单处理逻辑组合式函数
 */
export function useCategoryForm() {
  // 表单对象
  const form = reactive<ProductCategoryForm>({
    id: null,
    code: '',
    display_name: '',
    company: null,
    unit: null,
    material: null,
    material_type: null,
    drawing_pdf_url: '',
    process_pdf_url: ''
  })

  // 表单验证规则
  const rules = {
    code: [
      { required: true, message: '请输入产品类编码', trigger: 'blur' },
      { max: 20, message: '最大长度不能超过20', trigger: 'blur' }
    ],
    display_name: [
      { required: true, message: '请输入产品类名称', trigger: 'blur' },
      { max: 40, message: '最大长度不能超过40', trigger: 'blur' }
    ],
    company: [
      { required: true, message: '请选择所属公司', trigger: 'change' }
    ]
  }

  // 重置表单
  const resetForm = () => {
    form.id = null
    form.code = ''
    form.display_name = ''
    form.company = null
    form.unit = null
    form.material = null
    form.material_type = null
    form.drawing_pdf = undefined
    form.process_pdf = undefined
    form.drawing_pdf_url = ''
    form.process_pdf_url = ''
  }

  // 填充表单数据
  const fillForm = (categoryData: ProductCategoryForm) => {
    form.id = categoryData.id;
    form.code = categoryData.code || '';
    form.display_name = categoryData.display_name || '';
    form.company = categoryData.company ?? null;
    form.unit = categoryData.unit ?? null;
    form.material = categoryData.material ?? null;
    form.material_type = categoryData.material_type ?? null;
    form.drawing_pdf_url = typeof categoryData.drawing_pdf_url === 'string' ? categoryData.drawing_pdf_url : (typeof categoryData.drawing_pdf === 'string' ? categoryData.drawing_pdf : '');
    form.process_pdf_url = typeof categoryData.process_pdf_url === 'string' ? categoryData.process_pdf_url : (typeof categoryData.process_pdf === 'string' ? categoryData.process_pdf : '');
    form.drawing_pdf = undefined;
    form.process_pdf = undefined;
  }

  return {
    form,
    rules,
    resetForm,
    fillForm
  }
}
