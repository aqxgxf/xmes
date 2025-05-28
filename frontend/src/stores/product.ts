import { defineStore } from 'pinia';
import { productAPI, categoryAPI, unitAPI } from '../api';
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import type { PaginationParams, PaginatedResponse } from '../types';
import type { Product, ProductCategory, Unit } from '../types/common';

export const useProductStore = defineStore('product', () => {
  // State
  const products = ref<Product[]>([]);
  const categories = ref<ProductCategory[]>([]);
  const units = ref<Unit[]>([]);
  const currentProduct = ref<Product | null>(null);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);
  const totalProducts = ref<number>(0);
  const currentPage = ref<number>(1);
  const pageSize = ref<number>(10);
  const searchQuery = ref<string | null>(null);
  const sortField = ref<string | null>(null);
  const sortOrder = ref<'ascending' | 'descending' | null>(null);

  // Getters
  const productsByCategory = computed(() => {
    return (categoryId: number) => {
      if (!categoryId) return products.value;
      return products.value.filter(p => p.category === categoryId);
    };
  });

  // Actions
  const fetchProducts = async (params?: PaginationParams) => {
    isLoading.value = true;
    error.value = null;
    try {
      const effectiveParams: PaginationParams = {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value || undefined,
        ordering: sortField.value ? (sortOrder.value === 'descending' ? `-${sortField.value}` : sortField.value) : undefined,
        ...params,
      };
      const axiosResponse = await productAPI.getProducts(effectiveParams);
      const responseData = axiosResponse.data as PaginatedResponse<any>;

      if (responseData && Array.isArray(responseData.results)) {
        const rawProductsFromApi = responseData.results;
        products.value = rawProductsFromApi.map((p: any) => ({
          id: p.id,
          code: p.code,
          name: p.name,
          category: p.category,
          category_name: p.category_name,
          specification: p.specification,
          description: p.description,
          unit: p.unit,
          unit_name: p.unit_name,
          price: p.price,
          created_at: p.created_at,
          updated_at: p.updated_at,
          drawing_pdf: p.drawing_pdf,
          is_material: typeof p.is_material === 'boolean' ? p.is_material : false
        })) as Product[];
        totalProducts.value = responseData.count;
      } else if (Array.isArray(responseData)) {
        const rawProductsFromApi = responseData as any[];
        products.value = rawProductsFromApi.map((p: any) => ({
          id: p.id, code: p.code, name: p.name, category: p.category, category_name: p.category_name,
          specification: p.specification, description: p.description, unit: p.unit, unit_name: p.unit_name,
          price: p.price, created_at: p.created_at, updated_at: p.updated_at,
          is_material: typeof p.is_material === 'boolean' ? p.is_material : false
        })) as Product[];
        totalProducts.value = products.value.length;
      } else {
        products.value = [];
        totalProducts.value = 0;
        console.warn('Unexpected data structure in productAPI.getProducts response.data:', responseData);
      }
    } catch (err: any) {
      console.error('Failed to fetch products:', err);
      products.value = [];
      totalProducts.value = 0;
      error.value = err.response?.data?.detail || err.message || '获取产品列表失败';
      ElMessage.error(error.value || '获取产品列表失败');
    } finally {
      isLoading.value = false;
    }
  };

  const fetchCategories = async () => {
    isLoading.value = true;
    try {
      const axiosResponse = await categoryAPI.getCategories({ page_size: 1000 });
      const responseData = axiosResponse.data as PaginatedResponse<ProductCategory>;

      if (responseData && Array.isArray(responseData.results)) {
        categories.value = responseData.results.map(cat => ({...cat})) as ProductCategory[];
      } else if (Array.isArray(responseData)) {
        categories.value = responseData.map(cat => ({...cat})) as ProductCategory[];
      } else {
        console.warn('Unexpected data structure in categoryAPI.getCategories response.data:', responseData);
        categories.value = [];
      }
    } catch (err: any) {
      console.error('Failed to fetch categories:', err);
      categories.value = [];
      ElMessage.error(err.response?.data?.detail || err.message || '获取产品类别失败');
    } finally {
      isLoading.value = false;
    }
  };

  const fetchUnits = async () => {
    isLoading.value = true;
    try {
      const axiosResponse = await unitAPI.getUnits({ page_size: 1000 });
      const responseData = axiosResponse.data as PaginatedResponse<Unit>;

      if (responseData && Array.isArray(responseData.results)) {
        units.value = responseData.results.map(u => ({...u})) as Unit[];
      } else if (Array.isArray(responseData)) {
        units.value = responseData.map(u => ({...u})) as Unit[];
      } else {
        console.warn('Unexpected data structure in unitAPI.getUnits response.data:', responseData);
        units.value = [];
      }
    } catch (err: any) {
      console.error('Failed to fetch units:', err);
      units.value = [];
      ElMessage.error(err.response?.data?.detail || err.message ||'获取单位列表失败');
    } finally {
      isLoading.value = false;
    }
  };

  const fetchProductById = async (id: number) => {
    isLoading.value = true;
    try {
      const apiResponse = await productAPI.getProduct(id);
      const rawProductFromApi = apiResponse.data as any;
      
      currentProduct.value = {
        id: rawProductFromApi.id,
        code: rawProductFromApi.code,
        name: rawProductFromApi.name,
        category: rawProductFromApi.category,
        category_name: rawProductFromApi.category_name,
        specification: rawProductFromApi.specification,
        description: rawProductFromApi.description,
        unit: rawProductFromApi.unit,
        unit_name: rawProductFromApi.unit_name,
        price: rawProductFromApi.price,
        created_at: rawProductFromApi.created_at,
        updated_at: rawProductFromApi.updated_at,
        drawing_pdf: rawProductFromApi.drawing_pdf,
        is_material: typeof rawProductFromApi.is_material === 'boolean' ? rawProductFromApi.is_material : false
      } as Product;
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch product details';
      ElMessage.error(error.value || '获取产品详情失败');
      currentProduct.value = null;
    } finally {
      isLoading.value = false;
    }
  };

  const createProduct = async (productData: Partial<Product>) => {
    isLoading.value = true;
    try {
      const payload: any = { ...productData };

      const apiResponse = await productAPI.createProduct(payload);
      await fetchProducts(); 
      ElMessage.success('产品创建成功');
      const rawProductFromApi = apiResponse.data as any;
      return {
        id: rawProductFromApi.id, code: rawProductFromApi.code, name: rawProductFromApi.name,
        category: rawProductFromApi.category, category_name: rawProductFromApi.category_name,
        specification: rawProductFromApi.specification, description: rawProductFromApi.description,
        unit: rawProductFromApi.unit, unit_name: rawProductFromApi.unit_name,
        price: rawProductFromApi.price, created_at: rawProductFromApi.created_at, updated_at: rawProductFromApi.updated_at,
        drawing_pdf: rawProductFromApi.drawing_pdf,
        is_material: typeof rawProductFromApi.is_material === 'boolean' ? rawProductFromApi.is_material : false
      } as Product;
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Failed to create product';
      ElMessage.error(error.value || '创建产品失败');
      throw e; 
    } finally {
      isLoading.value = false;
    }
  };

  const updateProduct = async (id: number, productData: Partial<Product>) => {
    isLoading.value = true;
    try {
      const payload: any = { ...productData };

      const apiResponse = await productAPI.updateProduct(id, payload);
      await fetchProducts(); 
      ElMessage.success('产品更新成功');
      const rawProductFromApi = apiResponse.data as any;
      return {
        id: rawProductFromApi.id, code: rawProductFromApi.code, name: rawProductFromApi.name,
        category: rawProductFromApi.category, category_name: rawProductFromApi.category_name,
        specification: rawProductFromApi.specification, description: rawProductFromApi.description,
        unit: rawProductFromApi.unit, unit_name: rawProductFromApi.unit_name,
        price: rawProductFromApi.price, created_at: rawProductFromApi.created_at, updated_at: rawProductFromApi.updated_at,
        drawing_pdf: rawProductFromApi.drawing_pdf,
        is_material: typeof rawProductFromApi.is_material === 'boolean' ? rawProductFromApi.is_material : false
      } as Product;
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Failed to update product';
      ElMessage.error(error.value || '更新产品失败');
      throw e; 
    } finally {
      isLoading.value = false;
    }
  };

  const deleteProduct = async (id: number) => {
    isLoading.value = true;
    error.value = null;
    try {
      await productAPI.deleteProduct(id);
      const remainingItems = totalProducts.value - 1;
      totalProducts.value = Math.max(0, remainingItems);

      const totalPages = Math.ceil(totalProducts.value / pageSize.value);
      if (currentPage.value > totalPages && totalPages > 0) {
        currentPage.value = totalPages;
      } else if (totalPages === 0) {
        currentPage.value = 1; 
      }
      
      if (currentProduct.value && currentProduct.value.id === id) {
        currentProduct.value = null;
      }
      await fetchProducts();
      ElMessage.success('删除产品成功');
      return true;
    } catch (err: any) {
      console.error(`Failed to delete product with ID ${id}:`, err);
      error.value = err.response?.data?.detail || '删除产品失败';
      ElMessage.error(error.value || '删除产品失败');
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const importProducts = async (file: File) => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await productAPI.importProducts(file);
      await fetchProducts();
      return response.data;
    } catch (err: any) {
      console.error('Failed to import products:', err);
      const errorMessage = err.response?.data?.detail || err.response?.data?.msg || err.message || '导入产品失败';
      error.value = errorMessage;
      ElMessage.error(errorMessage);
      return { 
        msg: errorMessage, total: 0, success: 0, fail: 0, skipped: 0, 
        fail_msgs: [], skipped_reasons: [], duplicate_codes: [], processed_data: {} 
      };
    } finally {
      isLoading.value = false;
    }
  };

  const handleCurrentChange = async (page: number) => {
    currentPage.value = page;
    await fetchProducts();
  };

  const handleSizeChange = async (size: number) => {
    pageSize.value = size;
    currentPage.value = 1;
    await fetchProducts();
  };

  const setSearchQuery = async (query: string) => {
    searchQuery.value = query;
    currentPage.value = 1;
    await fetchProducts();
  };

  const setSorting = async (field: string, order: 'ascending' | 'descending' | null) => {
    sortField.value = field;
    sortOrder.value = order;
    currentPage.value = 1;
    await fetchProducts();
  };
  
  const initialize = async () => {
    isLoading.value = true;
    try {
      await fetchProducts();
      if (units.value.length === 0) {
          await fetchUnits();
      }
    } catch (e) {
        console.error("Initialization failed", e);
    } finally {
        isLoading.value = false;
    }
  };

  return {
    products,
    categories,
    units,
    currentProduct,
    isLoading,
    error,
    totalProducts,
    currentPage,
    pageSize,
    productsByCategory,
    fetchProducts,
    fetchCategories,
    fetchUnits,
    fetchProductById,
    createProduct,
    updateProduct,
    deleteProduct,
    importProducts,
    handleCurrentChange,
    handleSizeChange,
    setSearchQuery,
    setSorting,
    initialize
  };
});
