import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import axios from '../api'
import { ElMessage } from 'element-plus'
import type { CategoryMaterialRule, CategoryMaterialRuleForm, CategoryMaterialRuleParam } from '../types'

export const useCategoryMaterialRuleStore = defineStore('categoryMaterialRule', () => {
  const rules: Ref<CategoryMaterialRule[]> = ref([])
  const loading = ref(false)
  const total = ref(0)
  
  // 获取产品类BOM物料规则列表
  const fetchRules = async (params: any = {}) => {
    loading.value = true
    try {
      const response = await axios.get('/category-material-rules/', { params })
      rules.value = response.data.results || response.data
      total.value = response.data.count || response.data.length
    } catch (error: any) {
      handleApiError(error, '获取产品类BOM物料规则失败')
    } finally {
      loading.value = false
    }
  }
  
  // 通过ID获取规则详情
  const fetchRuleById = async (id: number) => {
    loading.value = true
    try {
      const response = await axios.get(`/category-material-rules/${id}/`)
      return response.data
    } catch (error: any) {
      handleApiError(error, '获取产品类BOM物料规则详情失败')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 创建产品类BOM物料规则
  const createRule = async (formData: CategoryMaterialRuleForm) => {
    loading.value = true
    try {
      const response = await axios.post('/category-material-rules/', formData)
      ElMessage.success('创建产品类BOM物料规则成功')
      return response.data
    } catch (error: any) {
      handleApiError(error, '创建产品类BOM物料规则失败')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 更新产品类BOM物料规则
  const updateRule = async (id: number, formData: CategoryMaterialRuleForm) => {
    loading.value = true
    try {
      const response = await axios.put(`/category-material-rules/${id}/`, formData)
      ElMessage.success('更新产品类BOM物料规则成功')
      return response.data
    } catch (error: any) {
      handleApiError(error, '更新产品类BOM物料规则失败')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 删除产品类BOM物料规则
  const deleteRule = async (id: number) => {
    loading.value = true
    try {
      await axios.delete(`/category-material-rules/${id}/`)
      ElMessage.success('删除产品类BOM物料规则成功')
      return true
    } catch (error: any) {
      handleApiError(error, '删除产品类BOM物料规则失败')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 获取规则参数表达式列表
  const fetchRuleParams = async (ruleId: number) => {
    loading.value = true
    try {
      const response = await axios.get('/category-material-rule-params/', {
        params: { rule: ruleId }
      })
      return response.data.results || response.data
    } catch (error: any) {
      handleApiError(error, '获取规则参数表达式失败')
      return []
    } finally {
      loading.value = false
    }
  }
  
  // 创建规则参数表达式
  const createRuleParam = async (formData: CategoryMaterialRuleParam) => {
    loading.value = true
    try {
      const response = await axios.post('/category-material-rule-params/', formData)
      ElMessage.success('创建规则参数表达式成功')
      return response.data
    } catch (error: any) {
      handleApiError(error, '创建规则参数表达式失败')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 更新规则参数表达式
  const updateRuleParam = async (id: number, formData: CategoryMaterialRuleParam) => {
    loading.value = true
    try {
      const response = await axios.put(`/category-material-rule-params/${id}/`, formData)
      ElMessage.success('更新规则参数表达式成功')
      return response.data
    } catch (error: any) {
      handleApiError(error, '更新规则参数表达式失败')
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 删除规则参数表达式
  const deleteRuleParam = async (id: number) => {
    loading.value = true
    try {
      await axios.delete(`/category-material-rule-params/${id}/`)
      ElMessage.success('删除规则参数表达式成功')
      return true
    } catch (error: any) {
      handleApiError(error, '删除规则参数表达式失败')
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 生成物料并添加到BOM
  const generateMaterial = async (ruleId: number, productId: number) => {
    loading.value = true
    try {
      const response = await axios.post('/category-material-rules/' + ruleId + '/generate_material/', {
        product_id: productId
      })
      
      if (response.data && response.data.message) {
        ElMessage.success('生成物料成功')
        return response.data
      } else {
        throw new Error(response.data?.error || '生成物料失败')
      }
    } catch (error: any) {
      console.error('生成物料失败:', error)
      ElMessage.error(`生成物料失败: ${error.response?.data?.error || error.message || '未知错误'}`)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // API错误处理
  const handleApiError = (error: any, defaultMessage: string) => {
    if (error.response && error.response.data) {
      if (typeof error.response.data === 'string') {
        ElMessage.error(error.response.data)
      } else if (error.response.data.detail) {
        ElMessage.error(error.response.data.detail)
      } else if (error.response.data.error) {
        ElMessage.error(error.response.data.error)
      } else if (error.response.data.non_field_errors) {
        ElMessage.error(error.response.data.non_field_errors.join(', '))
      } else {
        ElMessage.error(defaultMessage)
      }
    } else {
      ElMessage.error(defaultMessage)
    }
  }
  
  return {
    rules,
    loading,
    total,
    fetchRules,
    fetchRuleById,
    createRule,
    updateRule,
    deleteRule,
    fetchRuleParams,
    createRuleParam,
    updateRuleParam,
    deleteRuleParam,
    generateMaterial
  }
}) 