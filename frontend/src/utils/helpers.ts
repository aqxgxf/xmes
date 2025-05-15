import * as XLSX from 'xlsx';
import { ElMessage } from 'element-plus';

/**
 * Format date to YYYY-MM-DD HH:MM:SS
 * @param date Date object or date string
 * @returns Formatted date string
 */
export const formatDateTime = (date: Date | string): string => {
  const d = date instanceof Date ? date : new Date(date);
  
  if (isNaN(d.getTime())) {
    return '';
  }
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

/**
 * Format date to YYYY-MM-DD
 * @param date Date object or date string
 * @returns Formatted date string
 */
export const formatDate = (date: Date | string): string => {
  const d = date instanceof Date ? date : new Date(date);
  
  if (isNaN(d.getTime())) {
    return '';
  }
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
};

/**
 * Truncate text to a specific length and add ellipsis if needed
 * @param text Text to truncate
 * @param maxLength Maximum length before truncation
 * @returns Truncated text
 */
export const truncateText = (text: string, maxLength: number = 50): string => {
  if (!text) return '';
  
  if (text.length <= maxLength) {
    return text;
  }
  
  return text.substring(0, maxLength) + '...';
};

/**
 * Convert object to form data
 * @param obj Object to convert
 * @returns FormData object
 */
export const objectToFormData = (obj: Record<string, any>): FormData => {
  const formData = new FormData();
  
  Object.entries(obj).forEach(([key, value]) => {
    // Skip null or undefined values
    if (value === null || value === undefined) {
      return;
    }
    
    // Handle File objects
    if (value instanceof File) {
      formData.append(key, value);
      return;
    }
    
    // Handle arrays
    if (Array.isArray(value)) {
      value.forEach((item, index) => {
        if (typeof item === 'object' && item !== null) {
          Object.entries(item).forEach(([itemKey, itemValue]) => {
            formData.append(`${key}[${index}][${itemKey}]`, String(itemValue));
          });
        } else {
          formData.append(`${key}[]`, String(item));
        }
      });
      return;
    }
    
    // Handle objects
    if (typeof value === 'object' && value !== null) {
      Object.entries(value).forEach(([objKey, objValue]) => {
        formData.append(`${key}[${objKey}]`, String(objValue));
      });
      return;
    }
    
    // Handle primitive values
    formData.append(key, String(value));
  });
  
  return formData;
};

/**
 * Generate a download template for Excel import
 * @param headers Array of column headers
 * @param exampleData Array of example data rows
 * @param sheetName Name of the worksheet
 * @param fileName Name of the file to download
 */
export const generateExcelTemplate = (
  headers: string[],
  exampleData: any[][] = [],
  sheetName: string = 'Import Template',
  fileName: string = 'import_template.xlsx'
): void => {
  try {
    // Create workbook and worksheet
    const wb = XLSX.utils.book_new();
    
    // Combine headers and example data
    const worksheet = XLSX.utils.aoa_to_sheet([headers, ...exampleData]);
    
    // Add the worksheet to the workbook
    XLSX.utils.book_append_sheet(wb, worksheet, sheetName);
    
    // Write and download the file
    XLSX.writeFile(wb, fileName);
  } catch (error) {
    console.error('Failed to generate Excel template:', error);
    ElMessage.error('生成Excel模板失败');
  }
};

/**
 * Get value from deeply nested object using dot notation
 * @param obj Object to get value from
 * @param path Path to the value using dot notation
 * @param defaultValue Default value if path doesn't exist
 * @returns Value at path or default value
 */
export const getNestedValue = (
  obj: Record<string, any>,
  path: string,
  defaultValue: any = undefined
): any => {
  if (!obj || !path) return defaultValue;
  
  const keys = path.split('.');
  let current = obj;
  
  for (const key of keys) {
    if (current === null || current === undefined || typeof current !== 'object') {
      return defaultValue;
    }
    
    current = current[key];
  }
  
  return current !== undefined ? current : defaultValue;
};

/**
 * Convert error object to readable message
 * @param error Error object from API request
 * @returns Readable error message
 */
export const getErrorMessage = (error: any): string => {
  // Handle axios error responses
  if (error.response) {
    // The request was made and the server responded with an error status
    const { status, data } = error.response;
    
    // Handle different status codes
    if (status === 400) {
      // Bad request - usually validation errors
      if (typeof data === 'string') {
        return data;
      }
      
      if (data.detail) {
        return data.detail;
      }
      
      // Handle DRF validation errors object
      if (typeof data === 'object') {
        const messages: string[] = [];
        
        Object.entries(data).forEach(([field, errors]) => {
          if (Array.isArray(errors)) {
            messages.push(`${field}: ${errors.join(', ')}`);
          } else if (typeof errors === 'string') {
            messages.push(`${field}: ${errors}`);
          }
        });
        
        if (messages.length > 0) {
          return messages.join('\n');
        }
      }
      
      return '请求参数错误';
    }
    
    if (status === 401) {
      return '未授权，请登录';
    }
    
    if (status === 403) {
      return '您没有权限执行此操作';
    }
    
    if (status === 404) {
      return '请求的资源不存在';
    }
    
    if (status === 500) {
      return '服务器内部错误';
    }
    
    // Default message for other status codes
    return `请求失败 (${status})`;
  }
  
  // The request was made but no response was received
  if (error.request) {
    return '无法连接到服务器，请检查网络连接';
  }
  
  // Something happened in setting up the request
  return error.message || '发生未知错误';
}; 