<template>
  <div>
    <el-button type="primary" link @click="generateTemplate">
      <el-icon><Download /></el-icon> 下载模板
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Download } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// Define props
const props = defineProps<{
  templateType: string;
  fileName?: string;
}>();

interface ColumnDef {
  header: string;
  width: number;
  example?: string[];
}

// Map of template types to their column definitions
const templates: Record<string, { columns: Record<string, ColumnDef>, examples: string[][] }> = {
  'product-categories': {
    columns: {
      'code': { header: '产品类编码', width: 15, example: ['PC001', 'PC002'] },
      'display_name': { header: '产品类名称', width: 25, example: ['金属零件', '塑料配件'] },
      'company': { header: '所属公司', width: 20, example: ['公司A', '公司A'] }
    },
    examples: [
      ['PC001', '金属零件', '公司A'],
      ['PC002', '塑料配件', '公司A']
    ]
  },
  'category-params': {
    columns: {
      'category_code': { header: '产品类编码', width: 15, example: ['PC001', 'PC001'] },
      'name': { header: '参数项名称', width: 25, example: ['尺寸', '材质'] }
    },
    examples: [
      ['PC001', '尺寸'],
      ['PC001', '材质']
    ]
  },
  'products': {
    columns: {
      'code': { header: '产品代码', width: 15, example: ['P001', 'P002'] },
      'name': { header: '产品名称', width: 25, example: ['产品A', '产品B'] },
      'price': { header: '价格', width: 10, example: ['100', '200'] },
      'category_code': { header: '产品类编码', width: 15, example: ['PC001', 'PC002'] }
    },
    examples: [
      ['P001', '产品A', '100', 'PC001'],
      ['P002', '产品B', '200', 'PC002']
    ]
  },
  'materials': {
    columns: {
      'code': { header: '物料代码', width: 15, example: ['M001', 'M002'] },
      'name': { header: '物料名称', width: 25, example: ['物料A', '物料B'] },
      'price': { header: '价格', width: 10, example: ['50', '75'] },
      'category_code': { header: '产品类编码', width: 15, example: ['PC001', 'PC002'] }
    },
    examples: [
      ['M001', '物料A', '50', 'PC001'],
      ['M002', '物料B', '75', 'PC002']
    ]
  },
  'processes': {
    columns: {
      'code': { header: '工序代码', width: 15, example: ['PR001', 'PR002'] },
      'name': { header: '工序名称', width: 25, example: ['切割', '焊接'] },
      'description': { header: '工序描述', width: 30, example: ['材料切割成型', '零件焊接'] }
    },
    examples: [
      ['PR001', '切割', '材料切割成型'],
      ['PR002', '焊接', '零件焊接']
    ]
  },
  'process-codes': {
    columns: {
      'code': { header: '工艺流程代码', width: 15, example: ['PC001', 'PC002'] },
      'version': { header: '版本号', width: 10, example: ['1.0', '2.0'] },
      'description': { header: '工艺流程描述', width: 30, example: ['标准工艺', '特殊工艺'] }
    },
    examples: [
      ['PC001', '1.0', '标准工艺'],
      ['PC002', '2.0', '特殊工艺']
    ]
  },
  'boms': {
    columns: {
      'product_code': { header: '产品代码', width: 15, example: ['P001', 'P001'] },
      'name': { header: 'BOM名称', width: 20, example: ['标准BOM', '标准BOM'] },
      'version': { header: 'BOM版本', width: 10, example: ['1.0', '1.0'] },
      'material_code': { header: '物料代码', width: 15, example: ['M001', 'M002'] },
      'quantity': { header: '数量', width: 10, example: ['2', '1'] },
      'remark': { header: '备注', width: 30, example: ['主要材料', '辅助材料'] }
    },
    examples: [
      ['P001', '标准BOM', '1.0', 'M001', '2', '主要材料'],
      ['P001', '标准BOM', '1.0', 'M002', '1', '辅助材料']
    ]
  }
};

// Function to generate Excel template
const generateTemplate = async () => {
  // Check if template type is supported
  if (!props.templateType || !templates[props.templateType]) {
    ElMessage.error('不支持的模板类型');
    return;
  }
  
  try {
    // Load xlsx library
    const XLSX = await import('xlsx');
    
    const template = templates[props.templateType];
    // 确保文件名以.xlsx结尾
    let fileName = props.fileName || `${props.templateType}_template`;
    if (!fileName.endsWith('.xlsx')) {
      fileName += '.xlsx';
    }
    
    // Create headers row
    const headers = Object.values(template.columns).map(col => col.header);
    
    // Combine headers and examples
    const data = [headers, ...template.examples];
    
    // Create workbook and worksheet
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(data);
    
    // Set column widths
    ws['!cols'] = Object.values(template.columns).map(col => ({ wch: col.width }));
    
    // Add worksheet to workbook and save
    XLSX.utils.book_append_sheet(wb, ws, '导入模板');
    XLSX.writeFile(wb, fileName);
    
    ElMessage.success('模板已下载');
  } catch (error) {
    console.error('生成模板文件失败:', error);
    ElMessage.error('下载模板失败，请稍后重试');
  }
};
</script>

<style scoped>
</style> 