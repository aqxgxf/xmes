import { ref, reactive, watch } from 'vue'
import type { Param, MaterialForm, Category } from '../types/common'

/**
 * 物料表单处理逻辑组合式函数
 */
export function useMaterialForm() {
  // 表单对象
  const form = reactive<MaterialForm>({
    id: null,
    code: '',
    name: '',
    price: 0,
    category: null,
    unit: null,
    paramValues: {},
    drawing_pdf_url: undefined
  })

  // 表单验证规则
  const rules = {
    name: [
      { required: true, message: '请输入物料名称', trigger: 'blur' },
      { max: 100, message: '最大长度不能超过100', trigger: 'blur' }
    ],
    code: [
      { required: true, message: '请输入物料代码', trigger: 'blur' },
      { max: 100, message: '最大长度不能超过100', trigger: 'blur' }
    ],
    category: [
      { required: true, message: '请选择物料类别', trigger: 'change' }
    ],
    price: [
      { required: true, message: '请输入单价', trigger: 'blur' }
    ]
  }

  // 重置表单
  const resetForm = () => {
    form.id = null
    form.code = ''
    form.name = ''
    form.price = 0
    form.category = null
    form.unit = null
    form.paramValues = {}
    form.drawing_pdf = undefined
    form.drawing_pdf_url = undefined
  }

  // 填充表单数据
  const fillForm = (materialData: any) => {
    form.id = materialData.id
    form.code = materialData.code || ''
    form.name = materialData.name || ''
    form.price = materialData.price ? Number(materialData.price) : 0 // 转换为数字类型
    form.category = materialData.category
    form.unit = materialData.unit || null
    form.drawing_pdf_url = materialData.drawing_pdf_url

    // 填充参数值
    form.paramValues = {}
    if (materialData.param_values && materialData.param_values.length > 0) {
      materialData.param_values.forEach((pv: any) => {
        form.paramValues[pv.param] = pv.value
      })
    }
  }

  // 自动填充物料代码
  const autoFillMaterialCode = (categories: Category[] = [], params: Param[] = []) => {
    const cat = categories.find(c => c.id === form.category)
    if (!cat) return;

    // 以类别代码为基础
    let code = cat.code;

    // 如果有参数值，则添加完整参数名称+参数值
    if (Array.isArray(params) && params.length > 0) {
      const paramParts: string[] = [];
      params.forEach(param => {
        const value = form.paramValues[param.id];
        if (value && value.trim() !== '') {
          // 使用完整参数名称
          paramParts.push(`${param.name}${value}`);
        }
      });

      // 将参数部分用连字符拼接到代码后
      if (paramParts.length > 0) {
        code += '-' + paramParts.join('-');
      }
    }

    form.code = code
  }

  // 自动填充物料名称
  const autoFillMaterialName = (categories: Category[] = [], params: Param[] = []) => {
    const cat = categories.find(c => c.id === form.category)
    if (!cat) return;

    // 以类别名称为基础
    let name = cat.display_name;

    // 如果有参数值，则添加完整参数名称+参数值
    if (Array.isArray(params) && params.length > 0) {
      const paramParts: string[] = [];
      params.forEach(param => {
        const value = form.paramValues[param.id];
        if (value && value.trim() !== '') {
          // 使用完整参数名称
          paramParts.push(`${param.name}${value}`);
        }
      });

      // 将参数部分用连字符拼接到名称后
      if (paramParts.length > 0) {
        name += '-' + paramParts.join('-');
      }
    }

    form.name = name
  }

  return {
    form,
    rules,
    resetForm,
    fillForm,
    autoFillMaterialCode,
    autoFillMaterialName
  }
}
