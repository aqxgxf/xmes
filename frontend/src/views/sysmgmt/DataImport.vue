<template>
  <div class="data-import-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">数据批量导入</h2>
        </div>
      </template>

      <el-form label-position="top" class="import-form">
        <el-form-item label="选择导入类型">
          <el-select v-model="importType" placeholder="请选择导入类型" @change="handleImportTypeChange">
            <el-option label="产品类别" value="product-categories" />
            <el-option label="产品类别参数项" value="category-params" />
            <el-option label="产品" value="products" />
            <el-option label="物料" value="materials" />
            <el-option label="工序" value="processes" />
            <el-option label="工艺流程" value="process-codes" />
            <el-option label="工艺流程明细" value="process-details" />
            <el-option label="产品类工艺关联" value="category-process-codes" />
            <el-option label="BOM信息" value="boms" />
            <el-option label="单位" value="units" />
          </el-select>
        </el-form-item>

        <div v-if="importType" class="import-info">
          <h3>导入格式说明</h3>
          <div v-if="importType === 'product-categories'">
            <p>导入产品类别需要包含以下字段：</p>
            <el-table :data="categoryHeaders" border>
              <el-table-column prop="field" label="字段名" width="150" />
              <el-table-column prop="required" label="是否必填" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.required ? 'danger' : 'info'">
                    {{ row.required ? "必填" : "选填" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
            </el-table>
            <div class="template-download">
              <el-button type="primary" link @click="downloadProductCategoriesTemplate">
                <el-icon><Download /></el-icon> 下载模板
              </el-button>
            </div>
          </div>

          <div v-if="importType === 'category-params'">
            <p>导入产品类别参数项需要包含以下字段：</p>
            <el-table :data="categoryParamsHeaders" border>
              <el-table-column prop="field" label="字段名" width="150" />
              <el-table-column prop="required" label="是否必填" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.required ? 'danger' : 'info'">
                    {{ row.required ? "必填" : "选填" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
            </el-table>
            <div class="template-download">
              <el-button type="primary" link @click="downloadCategoryParamsTemplate">
                <el-icon><Download /></el-icon> 下载模板
              </el-button>
            </div>
          </div>

          <div v-if="importType === 'products'">
            <p>导入产品需要包含以下字段：</p>
            <el-table :data="productHeaders" border>
              <el-table-column prop="field" label="字段名" width="150" />
              <el-table-column prop="required" label="是否必填" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.required ? 'danger' : 'info'">
                    {{ row.required ? "必填" : "选填" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
            </el-table>
            <div class="template-download">
              <el-button type="primary" link @click="downloadProductsTemplate">
                <el-icon><Download /></el-icon> 下载模板
              </el-button>
            </div>
          </div>

          <div v-if="importType === 'materials'">
            <p>导入物料需要包含以下字段：</p>
            <el-table :data="materialHeaders" border>
              <el-table-column prop="field" label="字段名" width="150" />
              <el-table-column prop="required" label="是否必填" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.required ? 'danger' : 'info'">
                    {{ row.required ? "必填" : "选填" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
            </el-table>
            <div class="template-download">
              <el-button type="primary" link @click="downloadMaterialsTemplate">
                <el-icon><Download /></el-icon> 下载模板
              </el-button>
            </div>
          </div>

          <div v-if="importType === 'processes'">
            <p>导入工序需要包含以下字段：</p>
            <el-table :data="processHeaders" border>
              <el-table-column prop="field" label="字段名" width="150" />
              <el-table-column prop="required" label="是否必填" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.required ? 'danger' : 'info'">
                    {{ row.required ? "必填" : "选填" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
            </el-table>
            <div class="template-download">
              <el-button type="primary" link @click="downloadProcessesTemplate">
                <el-icon><Download /></el-icon> 下载模板
              </el-button>
            </div>
          </div>

          <div v-if="importType === 'process-codes'">
            <p>导入工艺流程需要包含以下字段：</p>
            <el-table :data="processCodeHeaders" border>
              <el-table-column prop="field" label="字段名" width="150" />
              <el-table-column prop="required" label="是否必填" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.required ? 'danger' : 'info'">
                    {{ row.required ? "必填" : "选填" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
            </el-table>
            <div class="template-download">
              <el-button type="primary" link @click="downloadProcessCodesTemplate">
                <el-icon><Download /></el-icon> 下载模板
              </el-button>
            </div>
          </div>

          <div v-if="importType === 'process-details'">
            <p>导入工艺流程明细需要包含以下字段：</p>
            <el-table :data="processDetailHeaders" border>
              <el-table-column prop="field" label="字段名" width="150" />
              <el-table-column prop="required" label="是否必填" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.required ? 'danger' : 'info'">
                    {{ row.required ? "必填" : "选填" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
            </el-table>
            <div class="template-download">
              <el-button type="primary" link @click="downloadProcessDetailsTemplate">
                <el-icon><Download /></el-icon> 下载模板
              </el-button>
            </div>
          </div>

          <div v-if="importType === 'category-process-codes'">
            <p>导入产品类工艺关联需要包含以下字段：</p>
            <el-table :data="categoryProcessCodeHeaders" border>
              <el-table-column prop="field" label="字段名" width="150" />
              <el-table-column prop="required" label="是否必填" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.required ? 'danger' : 'info'">
                    {{ row.required ? "必填" : "选填" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
            </el-table>
            <div class="template-download">
              <el-button type="primary" link @click="downloadCategoryProcessCodesTemplate">
                <el-icon><Download /></el-icon> 下载模板
              </el-button>
            </div>
          </div>

          <div v-if="importType === 'boms'">
            <p>导入BOM信息需要包含以下字段：</p>
            <el-table :data="bomHeaders" border>
              <el-table-column prop="field" label="字段名" width="150" />
              <el-table-column prop="required" label="是否必填" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.required ? 'danger' : 'info'">
                    {{ row.required ? "必填" : "选填" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
            </el-table>
            <div class="template-download">
              <el-button type="primary" link @click="downloadBomsTemplate">
                <el-icon><Download /></el-icon> 下载模板
              </el-button>
            </div>
          </div>

          <div v-if="importType === 'units'">
            <p>导入单位需要包含以下字段：</p>
            <el-table :data="unitHeaders" border>
              <el-table-column prop="field" label="字段名" width="150" />
              <el-table-column prop="required" label="是否必填" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.required ? 'danger' : 'info'">
                    {{ row.required ? "必填" : "选填" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
            </el-table>
            <div class="template-download">
              <el-button type="primary" link @click="downloadUnitsTemplate">
                <el-icon><Download /></el-icon> 下载模板
              </el-button>
            </div>
          </div>
        </div>

        <el-form-item label="上传文件" v-if="importType">
          <el-upload
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="fileList"
            accept=".xlsx,.xls,.csv"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 .xlsx, .xls, .csv 格式文件，文件大小不超过10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item v-if="importType && fileList.length > 0">
          <el-button 
            type="primary" 
            @click="submitImport" 
            :loading="importing"
          >
            开始导入
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Import Results -->
      <div v-if="importResult" class="import-result">
        <el-divider content-position="center">导入结果</el-divider>
        <el-alert
          :title="importResult.message"
          :type="importResult.success ? 'success' : 'error'"
          :description="importResult.details"
          show-icon
        />
        <div v-if="importResult.errors && importResult.errors.length > 0" class="error-details">
          <h4>错误详情：</h4>
          <el-table :data="importResult.errors" border stripe>
            <el-table-column prop="row" label="行号" width="80" />
            <el-table-column prop="message" label="错误信息" />
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { Download, UploadFilled } from '@element-plus/icons-vue';
import axios from 'axios';

// Define interfaces for type safety
interface ImportError {
  row: string;
  message: string;
}

interface ImportResult {
  success: boolean;
  message: string;
  details: string;
  errors: ImportError[];
}

interface HeaderInfo {
  field: string;
  required: boolean;
  description: string;
}

// Define import type
const importType = ref('');
const fileList = ref<any[]>([]);
const importing = ref(false);
const importResult = ref<ImportResult | null>(null);

// Define headers for each import type
const categoryHeaders: HeaderInfo[] = [
  { field: 'code', required: true, description: '产品类编码（唯一）' },
  { field: 'display_name', required: true, description: '产品类名称' },
  { field: 'company', required: true, description: '所属公司名称（必须已存在）' }
];

const categoryParamsHeaders: HeaderInfo[] = [
  { field: 'category_code', required: true, description: '产品类编码（必须已存在）' },
  { field: 'name', required: true, description: '参数项名称' }
];

const productHeaders: HeaderInfo[] = [
  { field: 'category_code', required: true, description: '产品类编码（必须已存在）' },
  { field: 'param_items', required: true, description: '参数项名称（多个用逗号分隔）' },
  { field: 'param_values', required: true, description: '参数值（多个用逗号分隔，顺序与参数项对应）' },
  { field: 'price', required: true, description: '价格' },
  { field: 'unit_code', required: false, description: '单位编码（必须已存在）' },
  { field: 'remark', required: false, description: '备注' }
];

const materialHeaders: HeaderInfo[] = [
  { field: 'code', required: true, description: '物料代码（唯一）' },
  { field: 'name', required: true, description: '物料名称' },
  { field: 'price', required: true, description: '价格' },
  { field: 'category_code', required: true, description: '产品类编码（必须已存在）' },
  { field: 'unit_code', required: false, description: '单位编码（必须已存在）' }
];

const processHeaders: HeaderInfo[] = [
  { field: 'code', required: true, description: '工序代码（唯一）' },
  { field: 'name', required: true, description: '工序名称（唯一）' },
  { field: 'description', required: false, description: '工序描述' }
];

const processCodeHeaders: HeaderInfo[] = [
  { field: 'code', required: true, description: '工艺流程代码' },
  { field: 'version', required: true, description: '版本号' },
  { field: 'description', required: false, description: '工艺流程描述' }
];

const processDetailHeaders: HeaderInfo[] = [
  { field: 'process_code', required: true, description: '工艺流程代码（必须已存在）' },
  { field: 'step_no', required: true, description: '工序号（同一工艺流程代码下唯一）' },
  { field: 'step', required: true, description: '工序名称（必须已存在）' },
  { field: 'machine_time', required: true, description: '设备时间(分钟)' },
  { field: 'labor_time', required: true, description: '人工时间(分钟)' },
  { field: 'process_content', required: false, description: '工序内容' },
  { field: 'required_equipment', required: false, description: '所需设备' },
  { field: 'remark', required: false, description: '备注' }
];

const categoryProcessCodeHeaders: HeaderInfo[] = [
  { field: 'category_code', required: true, description: '产品类代码（必须已存在）' },
  { field: 'process_code', required: true, description: '工艺流程代码（必须已存在）' },
  { field: 'version', required: true, description: '工艺流程版本' },
  { field: 'is_default', required: false, description: '是否默认（是/否）' }
];

const bomHeaders: HeaderInfo[] = [
  { field: 'product_code', required: true, description: '产品代码（必须已存在）' },
  { field: 'name', required: true, description: 'BOM名称' },
  { field: 'version', required: true, description: 'BOM版本' },
  { field: 'material_code', required: true, description: '物料代码（必须已存在）' },
  { field: 'quantity', required: true, description: '数量' },
  { field: 'remark', required: false, description: '备注' }
];

const unitHeaders: HeaderInfo[] = [
  { field: 'code', required: true, description: '单位编码（唯一）' },
  { field: 'name', required: true, description: '单位名称' },
  { field: 'description', required: false, description: '单位描述' }
];

// Handle import type change
const handleImportTypeChange = () => {
  fileList.value = [];
  importResult.value = null;
};

// Handle file change
const handleFileChange = (file: any) => {
  fileList.value = [file];
};

// Submit import
const submitImport = async () => {
  if (!importType.value) {
    ElMessage.warning('请选择导入类型');
    return;
  }

  if (fileList.value.length === 0) {
    ElMessage.warning('请选择要导入的文件');
    return;
  }

  const file = fileList.value[0].raw;
  if (!file) {
    ElMessage.warning('文件无效，请重新选择');
    return;
  }

  // Check file extension
  const allowedExtensions = ['.xlsx', '.xls', '.csv'];
  const fileName = file.name;
  const fileExt = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();
  if (!allowedExtensions.includes(fileExt)) {
    ElMessage.error('只支持 .xlsx, .xls, .csv 格式的文件');
    return;
  }

  // Check file size (10MB max)
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB');
    return;
  }

  importing.value = true;
  importResult.value = null;

  // Create form data
  const formData = new FormData();
  formData.append('file', file);

  try {
    // Determine import endpoint based on selected type
    let endpoint = '';
    switch (importType.value) {
      case 'product-categories':
        endpoint = '/api/product-categories/import/';
        break;
      case 'category-params':
        endpoint = '/api/category-params/import/';
        break;
      case 'products':
        endpoint = '/api/products/import/';
        break;
      case 'materials':
        endpoint = '/api/materials/import/';
        break;
      case 'processes':
        endpoint = '/api/processes/import/';
        break;
      case 'process-codes':
        endpoint = '/api/process-codes/import/';
        break;
      case 'process-details':
        endpoint = '/api/process-details/import/';
        break;
      case 'category-process-codes':
        endpoint = '/api/category-process-codes/import/';
        break;
      case 'boms':
        endpoint = '/api/boms/import/';
        break;
      case 'units':
        endpoint = '/api/units/import/';
        break;
      default:
        ElMessage.error('不支持的导入类型');
        importing.value = false;
        return;
    }

    const response = await axios.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    // Process import result
    if (response.data) {
      importResult.value = {
        success: true,
        message: response.data.msg || '导入成功',
        details: `成功导入 ${response.data.success || 0} 条记录，失败 ${response.data.fail || 0} 条记录。`,
        errors: []
      };
      
      // Extract error messages if any
      if (response.data.fail_msgs && response.data.fail_msgs.length > 0) {
        importResult.value.errors = response.data.fail_msgs.map((msg: string, index: number) => {
          const matches = msg.match(/第(\d+)行: (.*)/);
          return {
            row: matches ? matches[1] : `错误${index + 1}`,
            message: matches ? matches[2] : msg
          };
        });
      }
    } else {
      importResult.value = {
        success: false,
        message: '导入失败',
        details: '服务器没有返回有效的响应',
        errors: []
      };
    }
  } catch (error: any) {
    console.error('导入失败:', error);
    importResult.value = {
      success: false,
      message: '导入失败',
      details: error.response?.data?.msg || error.message || '未知错误',
      errors: []
    };
    
    if (error.response?.data?.fail_msgs) {
      importResult.value.errors = error.response.data.fail_msgs.map((msg: string, index: number) => {
        const matches = msg.match(/第(\d+)行: (.*)/);
        return {
          row: matches ? matches[1] : `错误${index + 1}`,
          message: matches ? matches[2] : msg
        };
      });
    }
  } finally {
    importing.value = false;
  }
};

// Template download functions
const downloadProductCategoriesTemplate = () => {
  const fields = categoryHeaders.map(h => h.field);
  const data = [
    ['PC001', '金属零件', '公司A'],
    ['PC002', '塑料配件', '公司A']
  ];
  
  generateExcelTemplate(fields, data, '产品类别导入模板');
};

const downloadCategoryParamsTemplate = () => {
  const fields = categoryParamsHeaders.map(h => h.field);
  const data = [
    ['PC001', '尺寸'],
    ['PC001', '材质']
  ];
  
  generateExcelTemplate(fields, data, '产品类别参数项导入模板');
};

const downloadProductsTemplate = () => {
  const fields = productHeaders.map(h => h.field);
  const data = [
    ['PC001', '尺寸,材质', '10cm,不锈钢', '100', 'PCS', '样品产品'],
    ['PC001', '尺寸,材质', '20cm,铝合金', '200', 'KG', '']
  ];
  
  // 添加额外的产品代码和名称生成说明
  const fileName = '产品导入模板';
  
  try {
    import('xlsx').then(XLSX => {
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.aoa_to_sheet([fields, ...data]);
      
      // 设置列宽
      ws['!cols'] = fields.map(() => ({ wch: 20 }));
      
      // 添加说明工作表
      const instructions = [
        ['产品导入说明'],
        [''],
        ['1. 产品代码生成规则：产品类编码 + 参数项 + 参数值'],
        ['2. 产品名称生成规则：产品类名称 + 参数项 + 参数值'],
        ['3. 参数项必须是已在该产品类中定义的参数项'],
        ['4. 多个参数项和参数值用逗号分隔，顺序必须一一对应'],
        ['5. unit_code为单位编码，必须已在系统中存在'],
        ['6. 例如：产品类PC001(金属零件)有参数项"尺寸"和"材质"，填写值为"10cm"和"不锈钢"'],
        ['   则生成的产品代码可能为：PC001-10cm-不锈钢'],
        ['   生成的产品名称可能为：金属零件-10cm-不锈钢'],
        [''],
        ['注意：实际的代码和名称格式可能根据系统设置有所不同，请以系统生成结果为准']
      ];
      
      const instructionSheet = XLSX.utils.aoa_to_sheet(instructions);
      instructionSheet['!cols'] = [{ wch: 60 }];
      
      XLSX.utils.book_append_sheet(wb, ws, '产品数据');
      XLSX.utils.book_append_sheet(wb, instructionSheet, '使用说明');
      
      XLSX.writeFile(wb, `${fileName}.xlsx`);
      
      ElMessage.success('模板已下载');
    }).catch(error => {
      console.error('加载XLSX库失败:', error);
      ElMessage.error('下载模板失败，请确保已安装xlsx库');
    });
  } catch (error) {
    console.error('生成模板文件失败:', error);
    ElMessage.error('下载模板失败，请稍后重试');
  }
};

const downloadMaterialsTemplate = () => {
  const fields = materialHeaders.map(h => h.field);
  const data = [
    ['M001', '物料A', '50', 'PC001', 'PCS'],
    ['M002', '物料B', '75', 'PC002', 'KG']
  ];
  
  generateExcelTemplate(fields, data, '物料导入模板');
};

const downloadProcessesTemplate = () => {
  const fields = processHeaders.map(h => h.field);
  const data = [
    ['PR001', '切割', '材料切割成型'],
    ['PR002', '焊接', '零件焊接']
  ];
  
  generateExcelTemplate(fields, data, '工序导入模板');
};

const downloadProcessCodesTemplate = () => {
  const fields = processCodeHeaders.map(h => h.field);
  const data = [
    ['PC001', '1.0', '标准工艺'],
    ['PC002', '2.0', '特殊工艺']
  ];
  
  generateExcelTemplate(fields, data, '工艺流程导入模板');
};

const downloadProcessDetailsTemplate = () => {
  const fields = ['process_code', 'step_no', 'step', 'machine_time', 'labor_time', 'process_content', 'required_equipment', 'remark'];
  const data = [
    ['GYA001', '10', '车加工', '30', '15', '加工内容示例', 'CNC设备', '备注示例']
  ];
  generateExcelTemplate(fields, data, '工艺流程明细导入模板');
};

const downloadCategoryProcessCodesTemplate = () => {
  const fields = ['category_code', 'process_code', 'version', 'is_default'];
  const data = [
    ['ZLA001', 'GYA001', '1.0', '是']
  ];
  generateExcelTemplate(fields, data, '产品类工艺关联导入模板');
};

const downloadBomsTemplate = () => {
  const fields = bomHeaders.map(h => h.field);
  const data = [
    ['P001', '标准BOM', '1.0', 'M001', '2', '主要材料'],
    ['P001', '标准BOM', '1.0', 'M002', '1', '辅助材料']
  ];
  
  generateExcelTemplate(fields, data, 'BOM信息导入模板');
};

const downloadUnitsTemplate = () => {
  const fields = unitHeaders.map(h => h.field);
  const data = [
    ['PCS', '个', '计数单位'],
    ['KG', '千克', '重量单位']
  ];
  
  generateExcelTemplate(fields, data, '单位导入模板');
};

// Generic Excel template generator
const generateExcelTemplate = (fields: string[], exampleData: string[][], fileName: string) => {
  try {
    // Create workbook with SheetJS
    import('xlsx').then(XLSX => {
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.aoa_to_sheet([fields, ...exampleData]);
      
      // Add column widths for better display
      ws['!cols'] = fields.map(() => ({ wch: 20 }));
      
      XLSX.utils.book_append_sheet(wb, ws, '导入模板');
      XLSX.writeFile(wb, `${fileName}.xlsx`);
      
      ElMessage.success('模板已下载');
    }).catch(error => {
      console.error('加载XLSX库失败:', error);
      ElMessage.error('下载模板失败，请确保已安装xlsx库');
    });
  } catch (error) {
    console.error('生成模板文件失败:', error);
    ElMessage.error('下载模板失败，请稍后重试');
  }
};
</script>

<style lang="scss" scoped>
.data-import-container {
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .page-title {
    margin: 0;
    font-size: 18px;
  }

  .import-form {
    max-width: 800px;
  }

  .import-info {
    margin: 20px 0;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 4px;

    h3 {
      margin-top: 0;
      margin-bottom: 15px;
    }
  }

  .template-download {
    margin-top: 15px;
    text-align: right;
  }

  .import-result {
    margin-top: 30px;

    .error-details {
      margin-top: 20px;
    }
  }
}
</style> 