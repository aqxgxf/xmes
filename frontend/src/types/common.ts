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
  unit?: number;
  unit_name?: string;
  drawing_pdf?: string;
  drawing_pdf_url?: string;
  param_values?: Array<{ param: number; value: string }>;
  category_name?: string;
  is_material: boolean;
}

export interface Material extends Product {
  // Material is a proxy model for Product in the backend, always with is_material=true
  is_material: true;
}

// Category interface
export interface Category extends BaseEntity {
  code: string;
  display_name: string;
  company?: number;
  company_name?: string;
}

// Parameter interfaces
export interface Param extends BaseEntity {
  name: string;
  category: number;
}

export interface ParamValue {
  param: number;
  value: string;
}

// Unit interface
export interface Unit extends BaseEntity {
  code: string;
  name: string;
  description?: string;
}

// Material form interface
export interface MaterialForm {
  id: number | null;
  code: string;
  name: string;
  price: number;
  category: number | null;
  unit: number | null;
  paramValues: Record<number, string>;
  drawing_pdf?: File;
  drawing_pdf_url?: string;
}

// Process interfaces
export interface Process extends BaseEntity {
  code: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface ProcessForm {
  id: number | null;
  code: string;
  name: string;
  description: string;
}

// Process Code interfaces
export interface ProcessCode extends BaseEntity {
  code: string;
  description: string;
  version: string;
  process_pdf?: string;
  product?: number | null;
  created_at?: string;
  updated_at?: string;
}

export interface ProcessCodeForm {
  id: number | null;
  code: string;
  description: string;
  version: string;
  process_pdf?: string;
  product: number | null;
}

// Process Detail interfaces
export interface ProcessDetail extends BaseEntity {
  process_code: number;
  step_no: number;
  step: number;
  process_name?: string;
  machine_time: number;
  labor_time: number;
  required_equipment?: string;
  remark?: string;
}

export interface ProcessDetailForm {
  id: number | null;
  process_code: number;
  step_no: number;
  step: number;
  machine_time: number;
  labor_time: number;
  required_equipment?: string;
  remark?: string;
}

// 产品工艺关联接口
export interface ProductProcessCode extends BaseEntity {
  product: number;
  product_name?: string;
  product_code?: string;
  process_code: number;
  process_code_text?: string;
  process_code_version?: string;
  is_default: boolean;
  remark?: string;
}

export interface ProductProcessCodeForm {
  id: number | null;
  product: number;
  process_code: number;
  is_default: boolean;
  remark?: string;
}

// BOM接口
export interface Bom extends BaseEntity {
  name: string;
  product: number;
  product_name?: string;
  version: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface BomForm {
  id: number | null;
  product: number | null;
  name: string;
  version: string;
  description?: string;
}

// BOM明细接口
export interface BomDetail extends BaseEntity {
  bom: number;
  bom_name?: string;
  material: number;
  material_name?: string;
  material_code?: string;
  quantity: number;
  remark?: string;
}

export interface BomDetailForm {
  id: number | null;
  bom: number | null;
  material: number | null;
  quantity: number;
  remark: string;
}

// 产品类管理接口
export interface ProductCategory extends BaseEntity {
  code: string;
  display_name: string;
  company: number;
  company_name?: string;
  unit?: number;
  unit_name?: string;
  drawing_pdf?: string;
  process_pdf?: string;
}

export interface ProductCategoryForm {
  id: number | null;
  code: string;
  display_name: string;
  company: number | null;
  unit?: number | null;
  unit_name?: string;
  drawing_pdf?: File;
  process_pdf?: File;
  drawing_pdf_url?: string;
  process_pdf_url?: string;
}
