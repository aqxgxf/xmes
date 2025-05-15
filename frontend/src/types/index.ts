// Generic Interfaces
export interface PaginationParams {
  page?: number;
  pageSize?: number;
  search?: string;
  ordering?: string;
  [key: string]: any;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// User Management
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
  last_login?: string;
}

// Base Data Types
export interface Company {
  id: number;
  name: string;
  code: string;
  address?: string;
  contact?: string;
  phone?: string;
  email?: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CompanyForm {
  id: number | null;
  name: string;
  code: string;
  address: string;
  contact: string;
  phone: string;
}

export interface Unit {
  id: number;
  code: string;
  name: string;
  description?: string;
}

export interface Category {
  id: number;
  code: string;
  name: string;
  display_name: string;
  company?: number;
  company_name?: string;
}

export interface ProductCategory {
  id: number;
  code: string;
  name: string;
  display_name: string;
  company: number;
  company_name?: string;
  drawing_pdf?: string;
  process_pdf?: string;
}

export interface ProductCategoryForm {
  id?: number;
  code: string;
  display_name: string;
  company: number | null;
  drawing_pdf?: string;
  process_pdf?: string;
}

export interface Product {
  id: number;
  code: string;
  name: string;
  category: number;
  category_name?: string;
  specification?: string;
  description?: string;
  unit?: number;
  unit_name?: string;
  price?: number;
  created_at?: string;
  updated_at?: string;
}

// BOM Management
export interface Bom {
  id: number;
  name: string;
  product: number;
  product_name?: string;
  version: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface BomDetail {
  id: number;
  bom: number;
  bom_name?: string;
  material: number;
  material_name?: string;
  quantity: number;
  remark?: string;
}

// Material Management
export interface Material {
  id: number;
  code: string;
  name: string;
  price: number | string;
  category: number;
  category_name?: string;
  unit?: number | null;
  unit_name?: string;
  drawing_pdf_url?: string;
  param_values?: ParamValue[];
}

export interface Param {
  id: number;
  name: string;
  category: number;
}

export interface ParamValue {
  param: number;
  value: string;
}

export interface MaterialForm {
  id: number | null;
  code: string;
  name: string;
  price: number | string;
  category: number | null;
  unit: number | null;
  paramValues: Record<number, string>;
  drawing_pdf_url?: string;
}

// Process Management
export interface Process {
  id: number;
  name: string;
  code: string;
  description?: string;
}

export interface ProcessCode {
  id: number;
  code: string;
  name: string;
  process_pdf?: string;
}

export interface ProductProcessCode {
  id: number;
  product: number;
  product_name?: string;
  process_code: number;
  process_code_name?: string;
  sequence: number;
  description?: string;
}

// Sales Management
export interface Customer {
  id: number;
  name: string;
  code: string;
  contact?: string;
  phone?: string;
  address?: string;
  email?: string;
}

export interface Order {
  id: number;
  order_number: string;
  customer: number;
  customer_name?: string;
  order_date: string;
  delivery_date?: string;
  status: string;
  remark?: string;
}

export interface OrderItem {
  id: number;
  order: number;
  product: number;
  product_name?: string;
  quantity: number;
  unit_price?: number;
  remark?: string;
}

// Production Management
export interface WorkOrder {
  id: number;
  work_order_number: string;
  order_item: number;
  product_name?: string;
  plan_quantity: number;
  actual_quantity?: number;
  start_date: string;
  end_date?: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface ProductParam {
  id: number;
  category: number;
  name: string;
  data_type: string;
  required: boolean;
  default_value?: string;
  created_at: string;
  updated_at: string;
}

export interface ProductParamValue {
  id: number;
  product: number;
  param: number;
  param_name?: string;
  value: string;
  created_at: string;
  updated_at: string;
}

export interface ProcessDetail {
  id: number;
  process_code: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface BomItem {
  id: number;
  bom: number;
  material: number;
  material_name?: string;
  quantity: number;
  unit: number;
  unit_name?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

// API 普通响应接口
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string | Record<string, string[]>;
  code?: number;
}
