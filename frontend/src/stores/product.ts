import { defineStore } from 'pinia';
import { productAPI, categoryAPI, unitAPI } from '../api';
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { type Product, type ProductCategory, type Unit, type PaginationParams, type PaginatedResponse } from '../types';

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
      const response = await productAPI.getProducts({
        page: params?.page || currentPage.value,
        page_size: params?.pageSize || pageSize.value,
        search: params?.search || '',
        category: params?.category || '',
        ...params
      });

      const data = response.data;
      if (data) {
        // Determine if the response is paginated
        if (isPaginatedResponse(data)) {
          products.value = data.results;
          totalProducts.value = data.count;
        } else {
          products.value = data;
          totalProducts.value = data.length;
        }

        // Update current page if it was changed
        if (params?.page) {
          currentPage.value = params.page;
        }

        // Update page size if it was changed
        if (params?.pageSize) {
          pageSize.value = params.pageSize;
        }
      }
    } catch (err: any) {
      console.error('Failed to fetch products:', err);
      error.value = err.response?.data?.detail || '获取产品列表失败';
      ElMessage.error(error.value || '获取产品列表失败');
    } finally {
      isLoading.value = false;
    }
  };

  const fetchCategories = async () => {
    isLoading.value = true;

    try {
      const response = await categoryAPI.getCategories();
      const data = response.data;

      // Determine if the response is paginated
      if (isPaginatedResponse(data)) {
        categories.value = data.results;
      } else {
        categories.value = data;
      }
    } catch (err: any) {
      console.error('Failed to fetch categories:', err);
      ElMessage.error('获取产品类别失败');
    } finally {
      isLoading.value = false;
    }
  };

  const fetchUnits = async () => {
    try {
      const response = await unitAPI.getUnits();
      const data = response.data;

      // Determine if the response is paginated
      if (isPaginatedResponse(data)) {
        units.value = data.results;
      } else {
        units.value = data;
      }
    } catch (err: any) {
      console.error('Failed to fetch units:', err);
      ElMessage.error('获取单位列表失败');
    }
  };

  // Type guard function to check if response is paginated
  function isPaginatedResponse<T>(data: T[] | PaginatedResponse<T>): data is PaginatedResponse<T> {
    return (data as PaginatedResponse<T>).results !== undefined;
  }

  const fetchProductById = async (id: number) => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await productAPI.getProduct(id);
      currentProduct.value = response.data;
    } catch (err: any) {
      console.error(`Failed to fetch product with ID ${id}:`, err);
      error.value = err.response?.data?.detail || '获取产品详情失败';
      ElMessage.error(error.value || '获取产品详情失败');
    } finally {
      isLoading.value = false;
    }
  };

  const createProduct = async (productData: Partial<Product>) => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await productAPI.createProduct(productData);
      ElMessage.success('创建产品成功');

      // Refresh product list
      await fetchProducts();

      return response.data;
    } catch (err: any) {
      console.error('Failed to create product:', err);
      error.value = err.response?.data?.detail || '创建产品失败';
      ElMessage.error(error.value || '创建产品失败');
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const updateProduct = async (id: number, productData: Partial<Product>) => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await productAPI.updateProduct(id, productData);
      ElMessage.success('更新产品成功');

      // Update current product if it's the one being edited
      if (currentProduct.value && currentProduct.value.id === id) {
        currentProduct.value = response.data;
      }

      // Refresh product list
      await fetchProducts();

      return response.data;
    } catch (err: any) {
      console.error(`Failed to update product with ID ${id}:`, err);
      error.value = err.response?.data?.detail || '更新产品失败';
      ElMessage.error(error.value || '更新产品失败');
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteProduct = async (id: number) => {
    isLoading.value = true;
    error.value = null;

    try {
      await productAPI.deleteProduct(id);
      ElMessage.success('删除产品成功');

      // Clear current product if it's the one being deleted
      if (currentProduct.value && currentProduct.value.id === id) {
        currentProduct.value = null;
      }

      // Refresh product list
      await fetchProducts();

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
      ElMessage.success(`导入完成: 成功${response.data.success}条, 失败${response.data.fail}条, 跳过${response.data.skipped}条`);

      // Refresh product list
      await fetchProducts();

      return response.data;
    } catch (err: any) {
      console.error('Failed to import products:', err);
      error.value = err.response?.data?.detail || '导入产品失败';
      ElMessage.error(error.value || '导入产品失败');
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    // State
    products,
    categories,
    units,
    currentProduct,
    isLoading,
    error,
    totalProducts,
    currentPage,
    pageSize,

    // Getters
    productsByCategory,

    // Actions
    fetchProducts,
    fetchCategories,
    fetchUnits,
    fetchProductById,
    createProduct,
    updateProduct,
    deleteProduct,
    importProducts
  };
});
