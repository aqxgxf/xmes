import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../api';
import { ElMessage } from 'element-plus';
import type { ProductCategory } from '../types';

export const useCategoryStore = defineStore('category', () => {
  // State
  const categories = ref<ProductCategory[]>([]);
  const isLoading = ref<boolean>(false);
  const totalCategories = ref<number>(0);
  const currentPage = ref<number>(1);
  const pageSize = ref<number>(10);

  // Getters
  const getCategoryById = computed(() => {
    return (id: number) => categories.value.find(category => category.id === id);
  });

  // Actions
  async function fetchCategories(params?: { page?: number; pageSize?: number; search?: string }) {
    isLoading.value = true;
    try {
      const queryParams: any = {
        page: params?.page || currentPage.value,
        page_size: params?.pageSize || pageSize.value
      };

      if (params?.search) {
        queryParams.search = params.search;
      }

      const response = await api.get('/product-categories/', { params: queryParams });

      if (response.data && response.data.success === true) {
        // API format with success flag
        const responseData = response.data.data || {};
        if (responseData && Array.isArray(responseData.results)) {
          categories.value = responseData.results;
          totalCategories.value = responseData.count || 0;
        } else if (responseData && Array.isArray(responseData)) {
          categories.value = responseData;
          totalCategories.value = responseData.length;
        }
      } else if (response.data) {
        // Standard Django REST format
        if (Array.isArray(response.data.results)) {
          categories.value = response.data.results;
          totalCategories.value = response.data.count || 0;
        } else if (Array.isArray(response.data)) {
          categories.value = response.data;
          totalCategories.value = response.data.length;
        }
      }

      // Update current page and page size
      if (params?.page) currentPage.value = params.page;
      if (params?.pageSize) pageSize.value = params.pageSize;

      return categories.value;
    } catch (error: any) {
      handleApiError(error, '获取产品类列表失败');
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  async function createCategory(categoryData: FormData) {
    isLoading.value = true;
    try {
      const response = await api.post('/product-categories/', categoryData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      await fetchCategories();
      ElMessage.success('创建产品类成功');
      return response.data;
    } catch (error: any) {
      handleApiError(error, '创建产品类失败');
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateCategory(id: number, categoryData: FormData) {
    isLoading.value = true;
    try {
      const response = await api.put(`/product-categories/${id}/`, categoryData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      await fetchCategories();
      ElMessage.success('更新产品类成功');
      return response.data;
    } catch (error: any) {
      handleApiError(error, '更新产品类失败');
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteCategory(id: number) {
    isLoading.value = true;
    try {
      await api.delete(`/product-categories/${id}/`);
      await fetchCategories();
      ElMessage.success('删除产品类成功');
    } catch (error: any) {
      handleApiError(error, '删除产品类失败');
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function importCategories(file: File) {
    isLoading.value = true;
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/product-categories/import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      await fetchCategories();
      ElMessage.success('导入产品类成功');
      return response.data;
    } catch (error: any) {
      handleApiError(error, '导入产品类失败');
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  // Helper function to handle API errors
  function handleApiError(error: any, defaultMessage: string) {
    let errorMessage = defaultMessage;

    if (error.response && error.response.data) {
      const responseData = error.response.data;
      if (typeof responseData === 'string') {
        errorMessage = responseData;
      } else if (responseData.detail) {
        errorMessage = responseData.detail;
      } else if (responseData.error) {
        errorMessage = responseData.error;
      } else if (responseData.message) {
        errorMessage = responseData.message;
      } else if (responseData.msg) {
        errorMessage = responseData.msg;
      } else {
        // Try to extract first error message
        const firstError = Object.values(responseData)[0];
        if (Array.isArray(firstError) && firstError.length > 0) {
          errorMessage = firstError[0] as string;
        } else if (typeof firstError === 'string') {
          errorMessage = firstError;
        }
      }
    }

    ElMessage.error(errorMessage);
    console.error(defaultMessage, error);
  }

  return {
    // State
    categories,
    isLoading,
    totalCategories,
    currentPage,
    pageSize,

    // Getters
    getCategoryById,

    // Actions
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    importCategories
  };
});
