import { reactive, watch } from 'vue'
import type { BomForm, Product } from '../types/common'

/**
 * BOM表单处理逻辑组合式函数
 */
export function useBomForm(productsList: Product[] = []) {
  // 表单对象
  const form = reactive<BomForm>({
    id: null,
    product: null,
    name: '',
    version: '',
    description: '',
    productObj: null
  })

  // 表单验证规则
  const rules = {
    product: [
      { required: true, message: '请选择产品', trigger: 'change' }
    ],
    name: [
      { required: true, message: '请输入BOM代码', trigger: 'blur' }
    ],
    version: [
      { required: true, message: '请选择版本', trigger: 'change' }
    ]
  }

  // 重置表单
  const resetForm = () => {
    form.id = null
    form.product = null
    form.name = ''
    form.version = ''
    form.description = ''
  }

  // 填充表单数据
  const fillForm = (bomData: any) => {
    form.id = bomData.id

    // 处理产品ID可能是字符串的情况
    form.product = typeof bomData.product === 'string' ? Number(bomData.product) : bomData.product

    form.name = bomData.name || ''
    form.version = bomData.version || ''
    form.description = bomData.description || ''

    // 确保加载数据后立即触发一次代码生成，特别是处理从API获取的数据
    if (form.product && form.version) {
      // 使用setTimeout确保产品和版本已正确设置
      setTimeout(() => {
        updateNameByProductAndVersion()
      }, 50)
    }
  }

  // 自动生成BOM名称和描述
  const updateNameByProductAndVersion = () => {
    console.log('尝试自动更新BOM名称和描述', form.product, form.version, productsList.length)
    // 优先用form.productObj
    let product = form.productObj
    if (!product && productsList.length > 0) {
      product = productsList.find(p => p.id === form.product)
    }
    console.log('找到产品:', product)
    if (product && form.version) {
      // 始终自动生成BOM名称，确保格式统一
      const oldName = form.name
      form.name = `${product.code}-${form.version}`
      console.log(`自动生成BOM代码: ${oldName} -> ${form.name}`)

      // 只有当描述为空时才自动生成描述
      if (!form.description || form.description === '') {
        const oldDesc = form.description
        form.description = `${product.name}-${form.version}`
        console.log(`自动生成描述: ${oldDesc} -> ${form.description}`)
      }
    } else {
      console.log('无法自动生成BOM代码和描述: 产品或版本未选择')
    }
  }

  // 监听产品和版本变化，自动生成名称和描述
  watch(() => form.product, (newVal, oldVal) => {
    // 只有当新值存在且与旧值不同时才更新
    if (newVal && newVal !== oldVal) {
      if (form.product) {
        updateNameByProductAndVersion()
      }
    }
  })

  watch(() => form.version, (newVal, oldVal) => {
    // 只有当新值存在且与旧值不同时才更新
    if (newVal && newVal !== oldVal) {
      if (form.version) {
        updateNameByProductAndVersion()
      }
    }
  })

  // 直接生成BOM名称和描述
  const generateWithProductAndVersion = (productId: number, versionStr: string) => {
    console.log(`直接生成使用产品ID=${productId}, 版本=${versionStr}`)
    // 找到产品
    const product = productsList.find(p => p.id === productId)
    console.log('找到产品:', product)

    if (product && versionStr) {
      // 设置产品和版本
      form.product = productId
      form.version = versionStr

      // 生成名称和描述
      form.name = `${product.code}-${versionStr}`
      if (!form.description || form.description === '') {
        form.description = `${product.name}-${versionStr}`
      }

      console.log('已生成BOM代码和描述:', form.name, form.description)
      return true
    }

    console.log('无法生成BOM代码和描述: 找不到产品或版本为空')
    return false
  }

  return {
    form,
    rules,
    resetForm,
    fillForm,
    updateNameByProductAndVersion,
    generateWithProductAndVersion
  }
}
