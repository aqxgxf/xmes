import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../api';
import { ElMessage } from 'element-plus';
import type { Unit } from '../types';

export const useUnitStore = defineStore('unit', () => {
  // State
  const units = ref<Unit[]>([]);
  const currentUnit = ref<Unit | null>(null);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);
  const totalUnits = ref<number>(0);
  const currentPage = ref<number>(1);
  const pageSize = ref<number>(20);

  // Getters
  const getUnitById = computed(() => {
    return (id: number) => units.value.find(unit => unit.id === id);
  });

  // Actions
  async function fetchUnits(params?: { page?: number; pageSize?: number; search?: string }) {
    isLoading.value = true;
    try {
      const queryParams: any = {
        page: params?.page || currentPage.value,
        page_size: params?.pageSize || pageSize.value
      };

      if (params?.search) {
        queryParams.search = params.search;
      }

      const response = await api.get('/units/', { params: queryParams });

      if (response.data && response.data.success === true) {
        // API format with success flag
        const responseData = response.data.data || {};
        if (responseData && Array.isArray(responseData.results)) {
          units.value = responseData.results;
          totalUnits.value = responseData.count || 0;
        } else if (responseData && Array.isArray(responseData)) {
          units.value = responseData;
          totalUnits.value = responseData.length;
        }
      } else if (response.data) {
        // Standard Django REST format
        if (Array.isArray(response.data.results)) {
          units.value = response.data.results;
          totalUnits.value = response.data.count || 0;
        } else if (Array.isArray(response.data)) {
          units.value = response.data;
          totalUnits.value = response.data.length;
        }
      }

      // Update current page and page size
      if (params?.page) currentPage.value = params.page;
      if (params?.pageSize) pageSize.value = params.pageSize;

      return units.value;
    } catch (error: any) {
      handleApiError(error, '获取单位列表失败');
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  const fetchUnitById = async (id: number) => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get(`/units/${id}/`);
      currentUnit.value = response.data;
    } catch (err: any) {
      console.error(`Failed to fetch unit with ID ${id}:`, err);
      error.value = err.response?.data?.detail || '获取单位详情失败';
      ElMessage.error(error.value || '获取单位详情失败');
    } finally {
      isLoading.value = false;
    }
  };

  async function createUnit(unitData: Partial<Unit>) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/units/', unitData);
      await fetchUnits();
      return response.data;
    } catch (error: any) {
      handleApiError(error, '创建单位失败');
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateUnit(id: number, unitData: Partial<Unit>) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.put(`/units/${id}/`, unitData);
      await fetchUnits();
      return response.data;
    } catch (error: any) {
      handleApiError(error, '更新单位失败');
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteUnit(id: number) {
    isLoading.value = true;
    error.value = null;

    try {
      await api.delete(`/units/${id}/`);
      await fetchUnits();
      ElMessage.success('单位删除成功');
    } catch (error: any) {
      handleApiError(error, '删除单位失败');
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function importUnits(formData: FormData) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/units/import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      await fetchUnits();
      ElMessage.success('导入单位成功');
      return response.data;
    } catch (error: any) {
      handleApiError(error, '导入单位失败');
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
    units,
    currentUnit,
    isLoading,
    error,
    totalUnits,
    currentPage,
    pageSize,

    // Getters
    getUnitById,

    // Actions
    fetchUnits,
    fetchUnitById,
    createUnit,
    updateUnit,
    deleteUnit,
    importUnits
  };
});
