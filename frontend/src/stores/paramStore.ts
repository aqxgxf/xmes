import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'

export interface CategoryParam {
  id: number;
  name: string;
  category: number;
  display_order?: number;
}

export interface ParamForm {
  id: number | null;
  name: string;
  category: number | null;
  display_order?: number;
}

interface PaginatedParamsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: CategoryParam[];
}

export const useParamStore = defineStore('param', () => {
  // State
  const params = ref<CategoryParam[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const search = ref('')
  const selectedCategory = ref<number | null>(null)

  // Computed
  // const filteredParams = computed(() => {
  //   if (!search.value) return params.value
  //   
  //   return params.value.filter(param => 
  //     param.name.toLowerCase().includes(search.value.toLowerCase())
  //   )
  // })

  // Actions
  const fetchParams = async () => {
    console.log('[paramStore.ts] fetchParams action CALLED. Current selectedCategory in store for API call:', selectedCategory.value);
    if (!selectedCategory.value) {
      console.log('[paramStore.ts] fetchParams: selectedCategory is null or undefined, clearing params and returning.');
      params.value = []
      total.value = 0
      return
    }
    
    loading.value = true
    error.value = null
    
    try {
      const queryParams: Record<string, string | number | undefined> = {
        category: selectedCategory.value,
        page: currentPage.value,
        page_size: pageSize.value,
        search: search.value || undefined,
        ordering: 'display_order',
      }
      Object.keys(queryParams).forEach(key => queryParams[key] === undefined && delete queryParams[key]);

      const response = await api.get<PaginatedParamsResponse>('/category-params/', {
        params: queryParams,
      })
      if (response.data && typeof response.data.count === 'number' && Array.isArray(response.data.results)) {
        params.value = response.data.results
        total.value = response.data.count
      } else {
        if (Array.isArray(response.data)) {
          params.value = response.data;
          total.value = response.data.length;
        } else {
          console.warn('Unexpected data structure for params:', response.data);
          params.value = [];
          total.value = 0;
          error.value = '获取参数项数据结构不正确';
        }
      }
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || '获取参数项失败'
      params.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  // Helper function for standardized API error extraction
  const handleApiError = (err: any, defaultMessage: string): string => {
    if (err.response?.data) {
      const data = err.response.data;
      if (typeof data === 'string' && data.length < 200) return data; // Avoid overly long string errors
      if (data.detail) return data.detail;
      if (data.message) return data.message;
      if (typeof data === 'object') {
        const firstKey = Object.keys(data)[0];
        if (firstKey && Array.isArray(data[firstKey]) && data[firstKey].length > 0) {
          return data[firstKey][0];
        }
        // Fallback for non-array errors or other structures
        try {
            const prettyError = JSON.stringify(data);
            if (prettyError.length < 300) return prettyError;
        } catch (e) { /* ignore stringify error */ }
      }
    }
    if (err.message) return err.message;
    return defaultMessage;
  };

  const createParam = async (paramData: ParamForm) => {
    loading.value = true
    error.value = null
    
    try {
      await api.post('/category-params/', paramData)
      await fetchParams()
      return { success: true, data: paramData }
    } catch (err: any) {
      console.error('创建参数项失败:', err)
      const specificError = handleApiError(err, '创建参数项失败');
      error.value = specificError;
      ElMessage.error(specificError || '创建参数项时发生未知错误');
      return { success: false, error: specificError };
    } finally {
      loading.value = false
    }
  }

  const updateParam = async (id: number, paramData: ParamForm) => {
    loading.value = true
    error.value = null
    
    try {
      await api.put(`/category-params/${id}/`, paramData)
      await fetchParams()
      return { success: true, data: paramData }
    } catch (err: any) {
      console.error('更新参数项失败:', err)
      const specificError = handleApiError(err, '更新参数项失败');
      error.value = specificError;
      ElMessage.error(specificError || '更新参数项时发生未知错误');
      return { success: false, error: specificError };
    } finally {
      loading.value = false
    }
  }

  const deleteParam = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      await api.delete(`/category-params/${id}/`)
      
      if (params.value.length === 1 && currentPage.value > 1 && total.value > 1) {
        currentPage.value--
      }
      
      await fetchParams()
      return { success: true }
    } catch (err: any) {
      console.error('删除参数项失败:', err)
      const specificError = handleApiError(err, '删除参数项失败');
      error.value = specificError;
      ElMessage.error(specificError || '删除参数项时发生未知错误');
      return { success: false, error: specificError };
    } finally {
      loading.value = false
    }
  }

  function setCategory(categoryId: number | null) {
    // 记录 action 被调用时的状态
    console.log(`[paramStore.ts] setCategory action called with new categoryId: ${categoryId}. Current store selectedCategory (before explicit set): ${selectedCategory.value}`);

    // 显式更新 store 中的 selectedCategory 值
    selectedCategory.value = categoryId;

    // 重置分页和搜索条件
    currentPage.value = 1;
    search.value = '';

    console.log(`[paramStore.ts] Category has been set to: ${selectedCategory.value}. Resetting page and search. Now calling fetchParams...`);
    // 调用 fetchParams 来获取新选定类别的数据
    fetchParams();
  }

  const setPage = (page: number) => {
    currentPage.value = page
    fetchParams()
  }

  const setPageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    fetchParams()
  }

  const setSearch = (term: string) => {
    search.value = term
    currentPage.value = 1
    fetchParams()
  }

  const updateParamsOrder = async (categoryId: number, orderedParams: Array<{ id: number | null; display_order: number }>) => {
    if (!categoryId) {
      ElMessage.error('产品类ID缺失，无法保存参数顺序。');
      throw new Error('产品类ID缺失');
    }
    loading.value = true;
    error.value = null;
    try {
      await api.post('/category-params/bulk-update-order/', { 
        category_id: categoryId,
        params: orderedParams 
      });
      await fetchParams(); 
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || '保存参数顺序失败';
      ElMessage.error(error.value || '保存参数顺序时发生未知错误');
      throw e;
    } finally {
      loading.value = false;
    }
  }

  return {
    // State
    params,
    total,
    loading,
    error,
    currentPage,
    pageSize,
    search,
    selectedCategory,
    
    // Computed
    // filteredParams,
    
    // Actions
    fetchParams,
    createParam,
    updateParam,
    deleteParam,
    updateParamsOrder,
    setCategory,
    setPage,
    setPageSize,
    setSearch
  }
}) 