/**
 * 日期格式化工具
 */

/**
 * 格式化日期为标准日期格式 (YYYY-MM-DD)
 */
export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return '';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  
  // 检查日期是否有效
  if (isNaN(d.getTime())) return '';
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
}

/**
 * 格式化日期时间为标准格式 (YYYY-MM-DD HH:MM:SS)
 */
export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return '';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  
  // 检查日期是否有效
  if (isNaN(d.getTime())) return '';
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

/**
 * 格式化日期时间为短格式 (YYYY-MM-DD HH:MM)
 */
export function formatDateTimeShort(date: string | Date | null | undefined): string {
  if (!date) return '';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  
  // 检查日期是否有效
  if (isNaN(d.getTime())) return '';
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}`;
}

/**
 * 格式化为相对时间（如：刚刚、5分钟前、2小时前、昨天等）
 */
export function formatRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return '';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  
  // 检查日期是否有效
  if (isNaN(d.getTime())) return '';
  
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  
  // 小于1分钟
  if (diff < 60 * 1000) {
    return '刚刚';
  }
  
  // 小于1小时
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000));
    return `${minutes}分钟前`;
  }
  
  // 小于24小时
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    return `${hours}小时前`;
  }
  
  // 小于30天
  if (diff < 30 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000));
    if (days === 1) return '昨天';
    return `${days}天前`;
  }
  
  // 小于12个月
  if (diff < 12 * 30 * 24 * 60 * 60 * 1000) {
    const months = Math.floor(diff / (30 * 24 * 60 * 60 * 1000));
    return `${months}个月前`;
  }
  
  // 大于12个月
  const years = Math.floor(diff / (12 * 30 * 24 * 60 * 60 * 1000));
  return `${years}年前`;
}

/**
 * 格式化交货日期（交货日期按照中文习惯格式化为：YYYY年MM月DD日）
 */
export function formatDeliveryDate(date: string | Date | null | undefined): string {
  if (!date) return '';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  
  // 检查日期是否有效
  if (isNaN(d.getTime())) return '';
  
  const year = d.getFullYear();
  const month = d.getMonth() + 1;
  const day = d.getDate();
  
  return `${year}年${month}月${day}日`;
}

/**
 * 计算两个日期之间的天数差
 */
export function getDaysBetween(startDate: string | Date, endDate: string | Date): number {
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  // 检查日期是否有效
  if (isNaN(start.getTime()) || isNaN(end.getTime())) return 0;
  
  // 计算天数差（将时间转换为天，然后向下取整）
  const diffTime = Math.abs(end.getTime() - start.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays;
}

/**
 * 检查日期是否已过期（当前日期是否已超过给定日期）
 */
export function isExpired(date: string | Date | null | undefined): boolean {
  if (!date) return false;
  
  const d = new Date(date);
  const now = new Date();
  
  // 检查日期是否有效
  if (isNaN(d.getTime())) return false;
  
  // 设置时间为一天的结束，以便比较整天
  d.setHours(23, 59, 59, 999);
  
  return now > d;
}

/**
 * 格式化为日期范围字符串（如：2023-01-01 至 2023-01-31）
 */
export function formatDateRange(startDate: string | Date, endDate: string | Date): string {
  return `${formatDate(startDate)} 至 ${formatDate(endDate)}`;
}

/**
 * 格式化为月份（如：2023年1月）
 */
export function formatMonth(date: string | Date | null | undefined): string {
  if (!date) return '';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  
  // 检查日期是否有效
  if (isNaN(d.getTime())) return '';
  
  const year = d.getFullYear();
  const month = d.getMonth() + 1;
  
  return `${year}年${month}月`;
}

/**
 * 将日期字符串转换为Date对象
 * 支持多种常见日期格式，返回有效的Date对象或null
 */
export function parseDate(dateStr: string): Date | null {
  if (!dateStr) return null;
  
  // 尝试解析标准ISO格式
  let date = new Date(dateStr);
  
  // 检查是否成功解析
  if (!isNaN(date.getTime())) return date;
  
  // 尝试解析常见的中文格式 YYYY年MM月DD日
  const chinesePattern = /(\d{4})年(\d{1,2})月(\d{1,2})日/;
  const chineseMatch = dateStr.match(chinesePattern);
  if (chineseMatch) {
    const [, year, month, day] = chineseMatch;
    date = new Date(Number(year), Number(month) - 1, Number(day));
    if (!isNaN(date.getTime())) return date;
  }
  
  // 尝试解析 DD/MM/YYYY 格式
  const slashPattern = /(\d{1,2})\/(\d{1,2})\/(\d{4})/;
  const slashMatch = dateStr.match(slashPattern);
  if (slashMatch) {
    const [, day, month, year] = slashMatch;
    date = new Date(Number(year), Number(month) - 1, Number(day));
    if (!isNaN(date.getTime())) return date;
  }
  
  return null;
} 