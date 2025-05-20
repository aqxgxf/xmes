import request from './index';
import type { Equipment, EquipmentMaintenance, EquipmentSpare, EquipmentSpareInventory } from '../types/index';

const baseUrl = '/api';

/**
 * 设备API
 */
export const equipmentApi = {
  // 获取设备列表
  getEquipments: (params?: any) => request.get<Equipment[]>(`${baseUrl}/equipments/`, { params }),
  
  // 获取设备详情
  getEquipment: (id: number) => request.get<Equipment>(`${baseUrl}/equipments/${id}/`),
  
  // 创建设备
  createEquipment: (data: FormData) => request.post<Equipment>(`${baseUrl}/equipments/`, data),
  
  // 更新设备
  updateEquipment: (id: number, data: FormData) => request.put<Equipment>(`${baseUrl}/equipments/${id}/`, data),
  
  // 删除设备
  deleteEquipment: (id: number) => request.delete(`${baseUrl}/equipments/${id}/`),
  
  // 获取设备的维保记录
  getEquipmentMaintenanceRecords: (equipmentId: number, params?: any) => 
    request.get<EquipmentMaintenance[]>(`${baseUrl}/equipments/${equipmentId}/maintenance_records/`, { params }),
  
  // 获取适用于设备的备件
  getEquipmentApplicableSpares: (equipmentId: number, params?: any) => 
    request.get<EquipmentSpare[]>(`${baseUrl}/equipments/${equipmentId}/applicable_spares/`, { params }),
  
  // 获取设备使用的备件记录
  getEquipmentSpareUsages: (equipmentId: number, params?: any) => 
    request.get<EquipmentSpareInventory[]>(`${baseUrl}/equipments/${equipmentId}/spare_usages/`, { params }),
};

/**
 * 设备维保记录API
 */
export const maintenanceApi = {
  // 获取维保记录列表
  getMaintenances: (params?: any) => 
    request.get<EquipmentMaintenance[]>(`${baseUrl}/equipment-maintenances/`, { params }),
  
  // 获取维保记录详情
  getMaintenance: (id: number) => 
    request.get<EquipmentMaintenance>(`${baseUrl}/equipment-maintenances/${id}/`),
  
  // 创建维保记录
  createMaintenance: (data: any) => 
    request.post<EquipmentMaintenance>(`${baseUrl}/equipment-maintenances/`, data),
  
  // 更新维保记录
  updateMaintenance: (id: number, data: any) => 
    request.put<EquipmentMaintenance>(`${baseUrl}/equipment-maintenances/${id}/`, data),
  
  // 删除维保记录
  deleteMaintenance: (id: number) => 
    request.delete(`${baseUrl}/equipment-maintenances/${id}/`),
};

/**
 * 设备备件API
 */
export const spareApi = {
  // 获取备件列表
  getSpares: (params?: any) => 
    request.get<EquipmentSpare[]>(`${baseUrl}/equipment-spares/`, { params }),
  
  // 获取备件详情
  getSpare: (id: number) => 
    request.get<EquipmentSpare>(`${baseUrl}/equipment-spares/${id}/`),
  
  // 创建备件
  createSpare: (data: FormData) => 
    request.post<EquipmentSpare>(`${baseUrl}/equipment-spares/`, data),
  
  // 更新备件
  updateSpare: (id: number, data: FormData) => 
    request.put<EquipmentSpare>(`${baseUrl}/equipment-spares/${id}/`, data),
  
  // 删除备件
  deleteSpare: (id: number) => 
    request.delete(`${baseUrl}/equipment-spares/${id}/`),
  
  // 获取备件的库存记录
  getSpareInventoryRecords: (spareId: number, params?: any) => 
    request.get<EquipmentSpareInventory[]>(`${baseUrl}/equipment-spares/${spareId}/inventory_records/`, { params }),
  
  // 获取所有备件的库存状态
  getSparesInventoryStatus: (params?: any) => 
    request.get<EquipmentSpare[]>(`${baseUrl}/equipment-spares/inventory_status/`, { params }),
  
  // 获取库存不足的备件列表
  getLowInventorySpares: (params?: any) => 
    request.get<EquipmentSpare[]>(`${baseUrl}/equipment-spares/low_inventory/`, { params }),
};

/**
 * 备件库存记录API
 */
export const inventoryApi = {
  // 获取库存记录列表
  getInventories: (params?: any) => 
    request.get<EquipmentSpareInventory[]>(`${baseUrl}/equipment-spare-inventories/`, { params }),
  
  // 获取库存记录详情
  getInventory: (id: number) => 
    request.get<EquipmentSpareInventory>(`${baseUrl}/equipment-spare-inventories/${id}/`),
  
  // 创建库存记录
  createInventory: (data: any) => 
    request.post<EquipmentSpareInventory>(`${baseUrl}/equipment-spare-inventories/`, data),
  
  // 更新库存记录
  updateInventory: (id: number, data: any) => 
    request.put<EquipmentSpareInventory>(`${baseUrl}/equipment-spare-inventories/${id}/`, data),
  
  // 删除库存记录
  deleteInventory: (id: number) => 
    request.delete(`${baseUrl}/equipment-spare-inventories/${id}/`),
}; 