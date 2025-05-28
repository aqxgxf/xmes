/**
 * 表单验证规则工具
 */
import type { FormItemRule } from 'element-plus'

type ValidatorFn = (rule: any, value: any, callback: Function) => void

// 必填项验证
export const requiredRule = (message: string = '此项为必填项'): FormItemRule => ({
  required: true,
  message,
  trigger: 'blur'
})

// 自定义验证器
export const createValidator = (validator: ValidatorFn, trigger: string = 'blur'): FormItemRule => ({
  validator,
  trigger
})

// 手机号验证
export const phoneValidator: ValidatorFn = (rule, value, callback) => {
  if (!value || value === '') {
    callback()
    return
  }
  
  // 中国大陆手机号格式
  const phoneRegex = /^1[3-9]\d{9}$/
  
  if (!phoneRegex.test(value)) {
    callback(new Error('请输入有效的手机号码'))
  } else {
    callback()
  }
}

// 电子邮箱验证
export const emailValidator: ValidatorFn = (rule, value, callback) => {
  if (!value || value === '') {
    callback()
    return
  }
  
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/
  
  if (!emailRegex.test(value)) {
    callback(new Error('请输入有效的电子邮箱地址'))
  } else {
    callback()
  }
}

// 数字范围验证
export const numberRangeValidator = (min: number, max: number): ValidatorFn => {
  return (rule, value, callback) => {
    if (!value && value !== 0) {
      callback()
      return
    }
    
    const num = Number(value)
    
    if (isNaN(num)) {
      callback(new Error('请输入有效的数字'))
      return
    }
    
    if (num < min || num > max) {
      callback(new Error(`请输入 ${min} 至 ${max} 之间的数字`))
    } else {
      callback()
    }
  }
}

// 字符串长度验证
export const stringLengthValidator = (min: number, max: number): ValidatorFn => {
  return (rule, value, callback) => {
    if (!value || value === '') {
      callback()
      return
    }
    
    if (value.length < min || value.length > max) {
      callback(new Error(`长度应在 ${min} 至 ${max} 个字符之间`))
    } else {
      callback()
    }
  }
}

// 密码强度验证
export const passwordStrengthValidator: ValidatorFn = (rule, value, callback) => {
  if (!value || value === '') {
    callback()
    return
  }
  
  // 密码至少包含 8 个字符，至少 1 个大写字母，1 个小写字母和 1 个数字
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/
  
  if (!passwordRegex.test(value)) {
    callback(new Error('密码至少8个字符，需包含大小写字母和数字'))
  } else {
    callback()
  }
}

// 客户代码验证（用于Company、Customer等）
export const companyCodeValidator: ValidatorFn = (rule, value, callback) => {
  if (!value || value === '') {
    callback()
    return
  }
  
  // 客户代码格式：字母、数字、下划线，长度为3-20
  const codeRegex = /^[a-zA-Z0-9_]{3,20}$/
  
  if (!codeRegex.test(value)) {
    callback(new Error('客户代码只能包含字母、数字和下划线，长度为3-20个字符'))
  } else {
    callback()
  }
}

// 产品代码验证（用于Product、Material等）
export const productCodeValidator: ValidatorFn = (rule, value, callback) => {
  if (!value || value === '') {
    callback()
    return
  }
  
  // 产品代码格式：字母、数字、下划线、连字符，长度为3-50
  const codeRegex = /^[a-zA-Z0-9_-]{3,50}$/
  
  if (!codeRegex.test(value)) {
    callback(new Error('产品代码只能包含字母、数字、下划线和连字符，长度为3-50个字符'))
  } else {
    callback()
  }
}

// 正数验证
export const positiveNumberValidator: ValidatorFn = (rule, value, callback) => {
  if (!value && value !== 0) {
    callback()
    return
  }
  
  const num = Number(value)
  
  if (isNaN(num)) {
    callback(new Error('请输入有效的数字'))
    return
  }
  
  if (num <= 0) {
    callback(new Error('请输入大于0的数字'))
  } else {
    callback()
  }
}

// 日期验证（确保日期不早于今天）
export const futureDateValidator: ValidatorFn = (rule, value, callback) => {
  if (!value) {
    callback()
    return
  }
  
  const inputDate = new Date(value)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  if (isNaN(inputDate.getTime())) {
    callback(new Error('请输入有效的日期'))
    return
  }
  
  if (inputDate < today) {
    callback(new Error('日期不能早于今天'))
  } else {
    callback()
  }
}

// 通用验证规则集
export const validationRules = {
  required: requiredRule,
  phone: createValidator(phoneValidator),
  email: createValidator(emailValidator),
  numberRange: (min: number, max: number) => createValidator(numberRangeValidator(min, max)),
  stringLength: (min: number, max: number) => createValidator(stringLengthValidator(min, max)),
  password: createValidator(passwordStrengthValidator),
  companyCode: createValidator(companyCodeValidator),
  productCode: createValidator(productCodeValidator),
  positiveNumber: createValidator(positiveNumberValidator),
  futureDate: createValidator(futureDateValidator)
} 