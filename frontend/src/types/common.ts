// Common types used throughout the application

// Common pagination parameters
export interface PaginationParams {
  page: number;
  page_size: number;
  search?: string;
  ordering?: string;
  [key: string]: any;
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  count: number;
  next: string | null;
  previous: string | null;
}

// Common status type mapping
export interface StatusMapping {
  [key: string]: {
    label: string;
    type: string;
  }
}

// Common entity interfaces
export interface BaseEntity {
  id: number;
  [key: string]: any;
}

export interface Company extends BaseEntity {
  name: string;
  code: string;
  address?: string;
  contact?: string;
  phone?: string;
}

export interface Customer extends Company {
  // Customer is a proxy model for Company in the backend
}

export interface Product extends BaseEntity {
  code: string;
  name: string;
  price: number;
  category: number;
  drawing_pdf?: string;
  drawing_pdf_url?: string;
  param_values?: any[];
  is_material: boolean;
}

export interface Material extends Product {
  // Material is a proxy model for Product in the backend, always with is_material=true
  is_material: true;
} 