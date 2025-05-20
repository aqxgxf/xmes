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
  name?: string;
  description?: string;
  version?: string;
  category?: number | null;
  process_pdf?: string;
}

export interface ProcessCodeForm {
  id: number | null;
  code: string;
  description: string;
  version: string;
  process_pdf: string;
  category: number | null;
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
  work_order_number?: string;
  workorder_no?: string;
  order_item?: number;
  order?: number | string;
  order_no?: string;
  product: number;
  product_name?: string;
  product_code?: string;
  plan_quantity?: number;
  quantity?: number;
  actual_quantity?: number;
  start_date?: string;
  end_date?: string;
  plan_start?: string;
  plan_end?: string;
  process_code?: number;
  process_code_text?: string;
  status: string;
  remark?: string;
  created_at?: string;
  updated_at?: string;
}

export interface WorkOrderForm {
  id?: number;
  workorder_no?: string;
  order?: number;
  product: number;
  quantity: number;
  process_code: number;
  plan_start?: string;
  plan_end?: string;
  status: string;
  remark?: string;
}

export interface Feedback {
  id: number;
  workorder_no: string;
  product_name: string;
  step_no: number;
  process_name: string;
  process_content: string;
  completed_quantity: number;
  defective_quantity: number;
  defective_reason: string;
  remark: string;
  created_by: string;
  created_at: string;
}

export interface ProcessDetailType {
  id: number;
  workorder: number;
  step_no: number;
  process: number;
  process_name: string;
  process_content?: string;
  pending_quantity: number;
  processed_quantity: number;
  completed_quantity: number;
  status: string;
}

export interface FeedbackForm {
  completedQuantity: number;
  defectiveQuantity: number;
  defectiveReason: string;
  remark: string;
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

// Equipment Management
export type EquipmentStatus = 'normal' | 'maintenance' | 'inspection' | 'disabled';

export interface Equipment {
  id: number;
  code: string;
  name: string;
  model: string;
  specification?: string;
  manufacturer?: string;
  purchase_date?: string;
  purchase_price?: number;
  installation_date?: string;
  location?: string;
  responsible_person?: string;
  status: EquipmentStatus;
  status_display?: string;
  next_maintenance_date?: string;
  image?: string;
  remark?: string;
  created_at: string;
  updated_at: string;
}

export interface EquipmentForm {
  code: string;
  name: string;
  model: string;
  specification?: string;
  manufacturer?: string;
  purchase_date?: string;
  purchase_price?: number;
  installation_date?: string;
  location?: string;
  responsible_person?: string;
  status: EquipmentStatus;
  next_maintenance_date?: string;
  image?: File | null;
  remark?: string;
}

export type MaintenanceType = 'routine' | 'repair' | 'inspection' | 'calibration';

export interface EquipmentMaintenance {
  id: number;
  equipment: number;
  equipment_name?: string;
  maintenance_date: string;
  maintenance_type: MaintenanceType;
  maintenance_type_display?: string;
  description: string;
  performed_by: string;
  cost?: number;
  result?: string;
  next_maintenance_date?: string;
  remark?: string;
  created_by: number;
  created_by_name?: string;
  created_at: string;
  updated_at: string;
}

export interface EquipmentMaintenanceForm {
  equipment: number;
  maintenance_date: string;
  maintenance_type: MaintenanceType;
  description: string;
  performed_by: string;
  cost?: number;
  result?: string;
  next_maintenance_date?: string;
  remark?: string;
}

export interface EquipmentSpare {
  id: number;
  code: string;
  name: string;
  model: string;
  specification?: string;
  manufacturer?: string;
  unit?: string;
  price?: number;
  min_inventory: number;
  current_inventory?: number;
  applicable_equipment: number[];
  applicable_equipment_names?: string[];
  image?: string;
  remark?: string;
  created_at: string;
  updated_at: string;
}

export interface EquipmentSpareForm {
  code: string;
  name: string;
  model: string;
  specification?: string;
  manufacturer?: string;
  unit?: string;
  price?: number;
  min_inventory: number;
  applicable_equipment: number[];
  image?: File | null;
  remark?: string;
}

export type InventoryTransactionType = 'in' | 'out';

export interface EquipmentSpareInventory {
  id: number;
  spare: number;
  spare_name?: string;
  spare_code?: string;
  transaction_type: InventoryTransactionType;
  transaction_type_display?: string;
  quantity: number;
  transaction_date: string;
  related_equipment?: number;
  related_equipment_name?: string;
  related_maintenance?: number;
  batch_no?: string;
  remark?: string;
  created_by?: number;
  created_by_name?: string;
  created_at: string;
}

export interface EquipmentSpareInventoryForm {
  spare: number;
  transaction_type: InventoryTransactionType;
  quantity: number;
  transaction_date?: string;
  related_equipment?: number;
  related_maintenance?: number;
  batch_no?: string;
  remark?: string;
}

// Form type
export type FormInstance = any;

// OrderForm
export interface OrderFormData {
  id?: number;
  order_number: string;
  customer: number;
  order_date: string;
  delivery_date: string;
  remark?: string;
  items: {
    id?: number;
    product: number;
    quantity: number;
    unit_price: number;
    remark?: string;
  }[];
}

// 产品类BOM物料规则
export interface CategoryMaterialRule {
  id: number;
  source_category: number;
  source_category_name?: string;
  source_category_code?: string;
  target_category: number;
  target_category_name?: string;
  target_category_code?: string;
  created_at?: string;
  updated_at?: string;
  param_expressions?: CategoryMaterialRuleParam[];
}

export interface CategoryMaterialRuleForm {
  id?: number | null;
  source_category: number;
  target_category: number;
}

export interface CategoryMaterialRuleParam {
  id?: number;
  rule: number;
  target_param: number;
  param_name?: string;
  expression: string;
}
