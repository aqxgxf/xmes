<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">工单管理</span>
      <el-button type="primary" @click="openAddWorkOrder">新增工单</el-button>
      <el-button type="success" @click="openCreateByOrderDialog">通过订单新增</el-button>
    </div>
    <el-table :data="workorders" style="width:100%;margin-top:16px;">
      <el-table-column prop="workorder_no" label="工单号" />
      <el-table-column prop="order" label="订单号" />
      <el-table-column prop="product" label="产品" />
      <el-table-column prop="quantity" label="数量" />
      <el-table-column prop="process_code" label="工艺流程代码" />
      <el-table-column prop="plan_start" label="计划开始" />
      <el-table-column prop="plan_end" label="计划结束" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          {{ getStatusText(scope.row.status) }}
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click.stop="editWorkOrder(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click.stop="deleteWorkOrder(scope.row)">删除</el-button>
          <el-button size="small" type="primary" @click.stop="viewProcessDetails(scope.row)">查看工艺明细</el-button>
          <el-button 
            size="small" 
            type="success" 
            @click.stop="printWorkOrder(scope.row)"
            v-if="scope.row.status === 'print'">打印工单</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showWorkOrderDialog" :title="workOrderForm.id ? '编辑工单' : '新增工单'" width="600px" @close="cancelWorkOrderEdit">
      <el-form :model="workOrderForm" :rules="workOrderFormRules" ref="workOrderFormRef" label-width="100px">
        <el-form-item label="工单号" prop="workorder_no"><el-input v-model="workOrderForm.workorder_no" /></el-form-item>
        <el-form-item label="订单号" prop="order">
          <el-select v-model="workOrderForm.order" filterable placeholder="请选择订单号" style="width:100%">
            <el-option v-for="o in orders" :key="o.id" :label="o.order_no" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品" prop="product">
          <el-select v-model="workOrderForm.product" filterable placeholder="请选择产品" style="width:100%">
            <el-option v-for="p in products" :key="p.id" :label="p.name+ '（' + p.code + '）'" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity"><el-input-number v-model="workOrderForm.quantity" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="工艺流程代码" prop="process_code">
          <el-select v-model="workOrderForm.process_code" filterable placeholder="请选择工艺流程" style="width:100%">
            <el-option v-for="c in processCodes" :key="c.id" :label="c.code + ' ' + c.version" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划开始" prop="plan_start"><el-date-picker v-model="workOrderForm.plan_start" type="datetime" style="width:100%" /></el-form-item>
        <el-form-item label="计划结束" prop="plan_end"><el-date-picker v-model="workOrderForm.plan_end" type="datetime" style="width:100%" /></el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="workOrderForm.status" style="width:100%">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark"><el-input v-model="workOrderForm.remark" type="text" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelWorkOrderEdit">取消</el-button>
        <el-button type="primary" @click="saveOrUpdateWorkOrder">保存工单</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showCreateByOrderDialog" title="通过订单新增工单" width="600px">
      <el-table :data="ordersWithoutWorkOrder" style="width:100%;margin-bottom:12px;" row-key="id">
        <el-table-column prop="order_no" label="订单号" />
        <el-table-column prop="company_name" label="公司" />
        <el-table-column prop="order_date" label="下单日期" />
        <el-table-column prop="total_amount" label="订单金额合计" />
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" type="primary" @click.stop="createWorkOrderByOrder(scope.row)">选择</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showCreateByOrderDialog=false">关闭</el-button>
      </template>
    </el-dialog>
    
    <el-dialog
      title="工单打印预览"
      v-model="showPrintDialog"
      width="90%"
      :before-close="handlePrintDialogClose"
      fullscreen
      :destroy-on-close="true"
      class="print-dialog"
    >
      <div class="print-container">
        <div class="print-actions">
          <span class="print-instruction">请检查内容后点击"打印"按钮</span>
          <div class="print-buttons">
            <el-button type="primary" @click="handlePrint" icon="Printer">打印</el-button>
            <el-button @click="handlePrintDialogClose">关闭</el-button>
          </div>
        </div>
        <iframe 
          ref="printFrame" 
          class="print-frame" 
          style="width:100%;border:none;" 
          v-if="printHtml">
        </iframe>
      </div>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import QRCode from 'qrcode'

const router = useRouter()
const workorders = ref([])
const products = ref<any[]>([])
const processCodes = ref<any[]>([])
const orders = ref<any[]>([])
const showWorkOrderDialog = ref(false)
const workOrderForm = ref<any>({ id: null, workorder_no: '', order: '', product: '', quantity: 0, process_code: '', plan_start: '', plan_end: '', status: '', remark: '' })
const showPrintDialog = ref(false)
const printHtml = ref('')
const printFrame = ref<HTMLIFrameElement | null>(null)
const currentPrintWorkOrder = ref<any>(null)
const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'print', label: '待打印' },
  { value: 'released', label: '已下达' },
  { value: 'in_progress', label: '生产中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]

function fetchWorkOrders() {
  axios.get('/api/workorders/').then(res => {
    workorders.value = res.data
  })
}
function openAddWorkOrder() {
  workOrderForm.value = { id: null, workorder_no: '', order: '', product: '', quantity: 0, process_code: '', plan_start: '', plan_end: '', status: '', remark: '' }
  showWorkOrderDialog.value = true
}
function editWorkOrder(row: any) {
  workOrderForm.value = { 
    ...row, 
    quantity: row.quantity ? Number(row.quantity) : 0 
  }
  showWorkOrderDialog.value = true
}
function cancelWorkOrderEdit() {
  showWorkOrderDialog.value = false
  workOrderForm.value = { id: null, workorder_no: '', order: '', product: '', quantity: 0, process_code: '', plan_start: '', plan_end: '', status: '', remark: '' }
  fetchWorkOrders()
}
async function saveOrUpdateWorkOrder() {
  let res
  if (workOrderForm.value.id) {
    res = await axios.put(`/api/workorders/${workOrderForm.value.id}/`, workOrderForm.value)
    ElMessage.success('工单更新成功')
  } else {
    res = await axios.post('/api/workorders/', workOrderForm.value)
    ElMessage.success('工单创建成功')
  }
  fetchWorkOrders()
}
async function deleteWorkOrder(row: any) {
  await axios.delete(`/api/workorders/${row.id}/`)
  ElMessage.success('工单已删除')
  fetchWorkOrders()
}
onMounted(() => {
  fetchWorkOrders()
  axios.get('/api/products/').then(res => {
    products.value = res.data.results || res.data
  })
  axios.get('/api/process-codes/').then(res => {
    processCodes.value = res.data.results || res.data
  })
  axios.get('/api/orders/').then(res => {
    orders.value = res.data
  })
})

// 监听产品变化，加载对应的工艺流程代码
watch(() => workOrderForm.value.product, (newProductId) => {
  if (newProductId) {
    axios.get(`/api/product-process-codes/?product=${newProductId}`).then(res => {
      const results = res.data.results || res.data;
      // 提取工艺流程代码数据
      const processCodeIds = new Set<number>();
      const filteredProcessCodes: Array<any> = [];
      
      // 遍历结果，提取工艺流程代码
      results.forEach((item: any) => {
        const processCode = item.process_code_detail || item.process_code;
        // 避免重复添加相同的工艺流程代码
        if (processCode && !processCodeIds.has(processCode.id)) {
          processCodeIds.add(processCode.id);
          filteredProcessCodes.push(processCode);
        }
      });
      
      processCodes.value = filteredProcessCodes;
      
      // 如果有默认工艺流程，自动选择
      const defaultProcess = results.find((item: any) => item.is_default);
      if (defaultProcess) {
        const processCode = defaultProcess.process_code_detail || defaultProcess.process_code;
        workOrderForm.value.process_code = processCode.id;
      } else if (filteredProcessCodes.length > 0) {
        workOrderForm.value.process_code = filteredProcessCodes[0].id;
      } else {
        workOrderForm.value.process_code = '';
      }
    }).catch(error => {
      console.error('获取工艺流程代码失败:', error);
      processCodes.value = [];
      workOrderForm.value.process_code = '';
    });
  } else {
    // 如果没有选择产品，加载所有工艺流程代码
    axios.get('/api/process-codes/').then(res => {
      processCodes.value = res.data.results || res.data;
    });
    workOrderForm.value.process_code = '';
  }
});

const workOrderFormRules = {
  workorder_no: [{ required: true, message: '工单号必填', trigger: 'blur' }],
  order: [{ required: true, message: '订单号必选', trigger: 'change' }],
  product: [{ required: true, message: '产品必选', trigger: 'change' }],
  quantity: [{ required: true, message: '数量必填', trigger: 'blur' }],
  process_code: [{ required: true, message: '工艺流程必选', trigger: 'change' }],
  status: [{ required: true, message: '状态必选', trigger: 'change' }]
}

const showCreateByOrderDialog = ref(false)
const ordersWithoutWorkOrder = ref<any[]>([])
function openCreateByOrderDialog() {
  axios.get('/api/orders-without-workorder/').then(res => {
    ordersWithoutWorkOrder.value = res.data
    showCreateByOrderDialog.value = true
  })
}
async function createWorkOrderByOrder(order: any) {
  const loading = ElMessage({ message: '正在创建工单...', type: 'info', duration: 0 })
  try {
    const res = await axios.post('/api/workorders/create-by-order/', { order_id: order.id }, {
      headers: {
        'Content-Type': 'application/json',
      }
    })
    showCreateByOrderDialog.value = false
    await fetchWorkOrders()
    if (res.data && res.data.id) {
      editWorkOrder(res.data)
      ElMessage.success('工单已自动生成，请补充完善后保存')
    } else {
      ElMessage.success('工单已自动生成')
    }
  } catch (e: any) {
    ElMessage.error('创建失败: ' + (e?.response?.data?.detail || e.message || '未知错误'))
  } finally {
    loading.close && loading.close()
  }
}

function viewProcessDetails(row: any) {
  router.push(`/workorder-process-details/${row.id}`)
}

function getStatusText(status: string) {
  const found = statusOptions.find(s => s.value === status)
  return found ? found.label : status
}

async function printWorkOrder(row: any) {
  // 设置当前打印的工单
  currentPrintWorkOrder.value = row;
  
  // 获取完整的工单信息，包括产品参数项
  try {
    const workorderResponse = await axios.get(`/api/workorders/${row.id}/`);
    const workorder = workorderResponse.data;
    
    // 获取产品参数项
    if (workorder.product) {
      const productResponse = await axios.get(`/api/products/${workorder.product}/`);
      const product = productResponse.data;
      
      // 获取产品图纸PDF
      let productDrawingPdf = product.drawing_pdf || '';
      
      // 如果产品没有图纸PDF，则获取所属产品类的图纸PDF
      if (!productDrawingPdf && product.category) {
        try {
          const categoryResponse = await axios.get(`/api/product-categories/${product.category}/`);
          const category = categoryResponse.data;
          productDrawingPdf = category.drawing_pdf || '';
        } catch (err) {
          console.error('获取产品类别信息失败:', err);
        }
      }
      
      // 获取工艺流程PDF
      let processPdf = '';
      
      // 优先获取工单工艺流程对应的工艺PDF
      if (workorder.process_code) {
        try {
          const processCodeResponse = await axios.get(`/api/process-codes/${workorder.process_code}/`);
          const processCode = processCodeResponse.data;
          processPdf = processCode.process_pdf || '';
        } catch (err) {
          console.error('获取工艺流程PDF失败:', err);
        }
      }
      
      // 如果工艺流程没有PDF，则获取产品所属产品类的工艺PDF
      if (!processPdf && product.category) {
        try {
          const categoryResponse = await axios.get(`/api/product-categories/${product.category}/`);
          const category = categoryResponse.data;
          processPdf = category.process_pdf || '';
        } catch (err) {
          console.error('获取产品类别工艺PDF失败:', err);
        }
      }

      // 获取产品BOM信息
      let bomItemsHtml = '<tr><td colspan="6">无BOM信息</td></tr>';
      try {
        // 查询产品的BOM
        const bomsResponse = await axios.get('/api/boms/', { 
          params: { product: workorder.product } 
        });
        const boms = bomsResponse.data.results || bomsResponse.data;
        
        if (boms && boms.length > 0) {
          // 获取最新版本的BOM
          const latestBom = boms.sort((a: any, b: any) => {
            return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
          })[0];
          
          // 获取BOM明细
          const bomResponse = await axios.get(`/api/boms/${latestBom.id}/`);
          const bomDetails = bomResponse.data;
          
          if (bomDetails && bomDetails.items && bomDetails.items.length > 0) {
            // 根据工单数量计算子零件数量
            const workorderQuantity = Number(workorder.quantity) || 0;
            
            // 获取所有物料的详细信息以获取代码
            const materialIds = bomDetails.items.map((item: any) => item.material);
            const materialsMap = new Map();
            
            // 如果有物料ID，获取详细信息
            if (materialIds.length > 0) {
              try {
                // 并行获取所有物料详情
                const materialPromises = materialIds.map((id: any) => 
                  axios.get(`/api/products/${id}/`)
                );
                const materialResponses = await Promise.all(materialPromises);
                
                // 建立ID到物料详情的映射
                materialResponses.forEach((response: any) => {
                  const material = response.data;
                  if (material && material.id) {
                    materialsMap.set(material.id, material);
                  }
                });
              } catch (err) {
                console.error('获取物料详情失败:', err);
              }
            }
            
            bomItemsHtml = bomDetails.items.map((item: any) => {
              const totalQuantity = (Number(item.quantity) * workorderQuantity).toFixed(2);
              // 从映射中获取物料详情
              const materialDetail = materialsMap.get(item.material);
              const materialCode = materialDetail ? materialDetail.code : '';
              
              return `
                <tr>
                  <td>${materialCode || ''}</td>
                  <td>${item.material_name || ''}</td>
                  <td>${item.quantity || 0}</td>
                  <td>${workorderQuantity}</td>
                  <td>${totalQuantity}</td>
                  <td>${item.remark || ''}</td>
                </tr>
              `;
            }).join('');
          }
        }
      } catch (err) {
        console.error('获取BOM信息失败:', err);
      }
      
      // 使用QRCode生成二维码
      let qrCodeDataURL = '';
      try {
        qrCodeDataURL = await QRCode.toDataURL(workorder.workorder_no, { 
          errorCorrectionLevel: 'M',
          margin: 1,
          width: 150
        });
      } catch (err) {
        console.error('生成二维码失败:', err);
        // 备用方案：使用在线服务
        qrCodeDataURL = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(workorder.workorder_no)}&qzone=1`;
      }
      
      // 生成工艺流程明细表格内容
      let processDetailsHtml = '<tr><td colspan="7">无工艺流程明细</td></tr>';
      if (workorder.process_details && workorder.process_details.length > 0) {
        processDetailsHtml = workorder.process_details.map((detail: any, index: number) => {
          // 只有第一道工序显示待加工数量，其他工序的待加工数量、已加工数量和完工数量都置空
          const pendingQty = index === 0 ? detail.pending_quantity : '';
          
          return `
            <tr>
              <td>${detail.step_no}</td>
              <td>${detail.process_name}</td>
              <td>${pendingQty}</td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
          `;
        }).join('');
      }
      
      // 生成转置后的产品参数项表格内容
      let paramColumnsHtml = '<tr><td colspan="2">无参数项</td></tr>';
      let paramValuesHtml = '<tr><td colspan="2">无参数项</td></tr>';
      
      if (product.param_values && product.param_values.length > 0) {
        paramColumnsHtml = '<tr>' + product.param_values.map((param: any) => `
          <th>${param.param_name}</th>
        `).join('') + '</tr>';
        
        paramValuesHtml = '<tr>' + product.param_values.map((param: any) => `
          <td>${param.value || ''}</td>
        `).join('') + '</tr>';
      }
      
      // 定义CSS样式
      const cssStyle = `
        @page {
          size: A4 landscape;
          margin: 1cm;
        }
        body {
          font-family: Arial, sans-serif;
          margin: 0;
          padding: 0;
          font-size: 12px;
          background: white;
        }
        .container {
          padding: 0.8cm;
          box-sizing: border-box;
          page-break-inside: avoid;
          break-inside: avoid;
        }
        .print-header { 
          text-align: center; 
          font-size: 22px; 
          font-weight: bold; 
          margin-bottom: 20px; 
          position: relative; 
        }
        .qrcode { 
          position: absolute; 
          top: 0; 
          right: 0; 
          width: 80px; 
          height: 80px; 
        }
        .print-info { 
          margin-bottom: 15px; 
          font-size: 12px;
          display: grid;
          grid-template-columns: 1fr 1fr;
          grid-gap: 10px;
        }
        .print-info div { 
          margin-bottom: 5px; 
        }
        .tables-container {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }
        .params-section, .bom-section, .process-section {
          margin-bottom: 15px;
        }
        table { 
          width: 100%; 
          border-collapse: collapse; 
          font-size: 11px;
        }
        th, td { 
          border: 1px solid #ddd; 
          padding: 5px; 
          text-align: left; 
        }
        th { 
          background-color: #f2f2f2; 
        }
        h3 {
          font-size: 16px;
          margin: 15px 0 10px 0;
          border-left: 4px solid #409EFF;
          padding-left: 10px;
        }
        @media print { 
          button { 
            display: none; 
          }
          .page { 
            page-break-after: always; 
          }
          .last-page {
            page-break-after: avoid !important;
          }
          body {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }
        }
        .drawing-container { 
          width: 100%; 
          text-align: center;
          margin: 0;
          overflow: visible;
          max-width: 100%;
          box-sizing: border-box;
          height: auto;
        }
        .drawing-img {
          max-width: 100%;
          max-height: 620px; /* 进一步减小高度 */
          object-fit: contain;
          border: 1px solid #ddd;
          margin: 0 auto;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .signatures {
          margin-top: 30px;
          display: flex;
          justify-content: space-between;
        }
      `;
      
      // 修改printScript以支持加载两个PDF
      const printScript = `
        let productPdfLoaded = false;
        let processPdfLoaded = false;

        // PDF渲染成图片
        async function renderPDFToImage(url, imgElement, loadingId, errorId) {
          try {
            // 异步加载PDF.js
            const pdfjsLib = window.pdfjsLib;
            if (!pdfjsLib) {
              console.error('PDF.js库未加载');
              document.getElementById(errorId).style.display = 'block';
              document.getElementById(loadingId).style.display = 'none';
              return false;
            }

            // 加载PDF文档
            const loadingTask = pdfjsLib.getDocument(url);
            const pdf = await loadingTask.promise;
            
            // 获取第一页
            const page = await pdf.getPage(1);
            
            // 获取PDF页面尺寸
            const originalViewport = page.getViewport({ scale: 1.0 });
            const originalWidth = originalViewport.width;
            const originalHeight = originalViewport.height;
            const originalAspectRatio = originalWidth / originalHeight;
            
            // A4纸张尺寸 (mm): 210×297
            // 转换为像素 (96 DPI): 约 794×1123
            // 横向A4: 1123×794
            // 考虑页边距和安全距离: 减去2.5cm边距 (约95px)
            const a4WidthInPx = 1123 - 95;  // A4宽度(横向)减去页边距
            const a4HeightInPx = 794 - 95;  // A4高度(横向)减去页边距
            
            // 根据PDF原始比例计算最佳尺寸
            let finalWidth, finalHeight, scale;
            
            if (originalWidth > originalHeight) {
              // 对于横向PDF，限制宽度为A4横向宽度
              finalWidth = a4WidthInPx;
              finalHeight = finalWidth / originalAspectRatio;
              
              // 如果高度超出A4高度，则按高度缩放
              if (finalHeight > a4HeightInPx) {
                finalHeight = a4HeightInPx;
                finalWidth = finalHeight * originalAspectRatio;
              }
              
              scale = finalWidth / originalWidth;
            } else {
              // 对于纵向PDF，限制高度为A4横向高度
              finalHeight = a4HeightInPx;
              finalWidth = finalHeight * originalAspectRatio;
              
              // 如果宽度超出A4宽度，则按宽度缩放
              if (finalWidth > a4WidthInPx) {
                finalWidth = a4WidthInPx;
                finalHeight = finalWidth / originalAspectRatio;
              }
              
              scale = finalHeight / originalHeight;
            }
            
            // 应用缩放，并进一步缩小5%以确保安全
            scale = scale * 0.95;
            finalWidth = finalWidth * 0.95;
            finalHeight = finalHeight * 0.95;
            
            // 应用缩放
            const viewport = page.getViewport({ scale: scale });
            
            // 创建canvas
            const canvas = document.createElement('canvas');
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            
            // 渲染到canvas
            const context = canvas.getContext('2d');
            await page.render({
              canvasContext: context,
              viewport: viewport
            }).promise;
            
            // 转换为图片URL
            const imgUrl = canvas.toDataURL('image/png');
            imgElement.src = imgUrl;
            imgElement.style.display = 'block';
            
            // 根据计算设置图片尺寸
            imgElement.style.width = finalWidth + 'px';
            imgElement.style.height = finalHeight + 'px';
            imgElement.style.maxWidth = '100%';  // 在小屏幕上自适应
            imgElement.style.boxSizing = 'border-box';
            
            document.getElementById(loadingId).style.display = 'none';
            
            return true;
          } catch (error) {
            console.error('PDF渲染失败:', error);
            document.getElementById(errorId).style.display = 'block';
            document.getElementById(loadingId).style.display = 'none';
            return false;
          }
        }
        
        // 检查是否所有PDF都已加载或超时，然后执行打印
        function checkAllPdfsAndPrint() {
          // 获取URL
          const productPdfUrl = document.getElementById('pdf-url');
          const processPdfUrl = document.getElementById('process-pdf-url');
          
          // 如果没有任何PDF，直接打印
          if (!productPdfUrl && !processPdfUrl) {
            console.log('没有PDF需要加载');
            return;
          }
          
          // 检查是否所有PDF都已加载或没有PDF
          const productPdfNeeded = productPdfUrl ? true : false;
          const processPdfNeeded = processPdfUrl ? true : false;
          
          if ((!productPdfNeeded || productPdfLoaded) && (!processPdfNeeded || processPdfLoaded)) {
            console.log('所有PDF已加载完成');
            // 不自动打印，由用户手动点击打印按钮
          }
        }
        
        // 页面加载完成后执行
        window.addEventListener('load', function() {
          // 检查产品图纸PDF
          const productPdfUrl = document.getElementById('pdf-url');
          if (productPdfUrl && productPdfUrl.value) {
            const imgElement = document.getElementById('drawing-img');
            if (imgElement) {
              // 加载PDF.js库
              const script = document.createElement('script');
              script.src = '/pdfjs/pdf.js';
              script.onload = function() {
                // 设置worker路径
                window.pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdfjs/pdf.worker.js';
                
                // 渲染产品图纸PDF
                renderPDFToImage(
                  productPdfUrl.value, 
                  imgElement, 
                  'pdf-loading', 
                  'pdf-error'
                ).then(success => {
                  productPdfLoaded = success;
                  checkAllPdfsAndPrint();
                });
                
                // 渲染工艺流程PDF（如果存在）
                const processPdfUrl = document.getElementById('process-pdf-url');
                if (processPdfUrl && processPdfUrl.value) {
                  const processImgElement = document.getElementById('process-pdf-img');
                  if (processImgElement) {
                    renderPDFToImage(
                      processPdfUrl.value, 
                      processImgElement, 
                      'process-pdf-loading', 
                      'process-pdf-error'
                    ).then(success => {
                      processPdfLoaded = success;
                      checkAllPdfsAndPrint();
                    });
                  } else {
                    processPdfLoaded = true;
                    checkAllPdfsAndPrint();
                  }
                } else {
                  processPdfLoaded = true;
                  checkAllPdfsAndPrint();
                }
              };
              document.head.appendChild(script);
            } else {
              productPdfLoaded = true;
              checkAllPdfsAndPrint();
            }
          } else {
            productPdfLoaded = true;
            
            // 检查工艺流程PDF
            const processPdfUrl = document.getElementById('process-pdf-url');
            if (processPdfUrl && processPdfUrl.value) {
              const processImgElement = document.getElementById('process-pdf-img');
              if (processImgElement) {
                // 加载PDF.js库
                const script = document.createElement('script');
                script.src = '/pdfjs/pdf.js';
                script.onload = function() {
                  // 设置worker路径
                  window.pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdfjs/pdf.worker.js';
                  
                  // 渲染工艺流程PDF
                  renderPDFToImage(
                    processPdfUrl.value, 
                    processImgElement, 
                    'process-pdf-loading', 
                    'process-pdf-error'
                  ).then(success => {
                    processPdfLoaded = success;
                    checkAllPdfsAndPrint();
                  });
                };
                document.head.appendChild(script);
              } else {
                processPdfLoaded = true;
                checkAllPdfsAndPrint();
              }
            } else {
              processPdfLoaded = true;
              checkAllPdfsAndPrint();
            }
          }
        });
        
        // 打印函数
        function printContent() {
          window.print();
        }
      `;
      
      // 确保 HTML 拼接的完整性
      let html = '<!DOCTYPE html><html><head>';
      html += '<meta charset="utf-8">';
      html += '<title>工单打印 - ' + workorder.workorder_no + '</title>';
      html += '<style>' + cssStyle + '</style>';
      html += '</head><body>';
      
      // 工单信息页面
      html += '<div class="container page">';

      // 添加工单信息
      html += `
        <div class="print-header">
          生产工单
          <img class="qrcode" src="${qrCodeDataURL}" alt="工单号二维码">
        </div>
        <div class="print-info">
          <div><strong>工单号：</strong>${workorder.workorder_no}</div>
          <div><strong>产品：</strong>${workorder.product_code} - ${workorder.product_name}</div>
          <div><strong>数量：</strong>${workorder.quantity}</div>
          <div><strong>订单号：</strong>${workorder.order_no || ''}</div>
          <div><strong>计划开始：</strong>${workorder.plan_start}</div>
          <div><strong>工艺流程：</strong>${workorder.process_code_text || ''}</div>
          <div><strong>计划结束：</strong>${workorder.plan_end}</div>
          <div><strong>备注：</strong>${workorder.remark || ''}</div>
        </div>
      `;

      // 添加产品参数项表格、BOM表格和工艺流程明细表格
      html += `
        <div class="tables-container">
          <div class="params-section">
            <h3>产品参数项</h3>
            <table>
              <thead>${paramColumnsHtml}</thead>
              <tbody>${paramValuesHtml}</tbody>
            </table>
          </div>
          
          <div class="bom-section">
            <h3>BOM清单（根据工单数量计算）</h3>
            <table>
              <thead>
                <tr>
                  <th>物料代码</th>
                  <th>物料名称</th>
                  <th>单件用量</th>
                  <th>工单数量</th>
                  <th>总用量</th>
                  <th>备注</th>
                </tr>
              </thead>
              <tbody>${bomItemsHtml}</tbody>
            </table>
          </div>
          
          <div class="process-section">
            <h3>工艺流程明细</h3>
            <table>
              <thead>
                <tr>
                  <th>序号</th>
                  <th>工序</th>
                  <th>待加工数量</th>
                  <th>已加工数量</th>
                  <th>完工数量</th>
                  <th>不良数量</th>
                  <th>操作者</th>
                </tr>
              </thead>
              <tbody>${processDetailsHtml}</tbody>
            </table>
          </div>
        </div>
      `;

      // 添加签名区域
      html += `
        <div class="signatures">
          <div>
            <p><strong>工单制作人：</strong>_________________</p>
          </div>
          <div>
            <p><strong>审核：</strong>_________________</p>
          </div>
        </div>
      `;
      
      html += '</div>'; // 结束第一页容器

      // 添加产品图纸页面
      if (productDrawingPdf) {
        const isLastPage = !processPdf; // 如果没有工艺流程PDF，则这是最后一页
        const pageClass = isLastPage ? 'container last-page' : 'container page';
        
        html += `
          <div class="${pageClass}">
            <input type="hidden" id="pdf-url" value="${productDrawingPdf}">
            <div class="drawing-container">
              <div id="pdf-loading" style="text-align:center;padding:20px;">
                正在加载产品图纸...
              </div>
              <div id="pdf-error" style="display:none;color:red;text-align:center;padding:20px;">
                图纸加载失败，<a href="${productDrawingPdf}" target="_blank">点击此处</a>查看或下载PDF文件
              </div>
              <img id="drawing-img" class="drawing-img" style="display:none;" alt="产品图纸" />
            </div>
          </div>
        `;
      }
      
      // 添加工艺流程PDF页面
      if (processPdf) {
        html += `
          <div class="container last-page">
            <input type="hidden" id="process-pdf-url" value="${processPdf}">
            <div class="drawing-container">
              <div id="process-pdf-loading" style="text-align:center;padding:20px;">
                正在加载工艺流程图...
              </div>
              <div id="process-pdf-error" style="display:none;color:red;text-align:center;padding:20px;">
                工艺流程图加载失败，<a href="${processPdf}" target="_blank">点击此处</a>查看或下载PDF文件
              </div>
              <img id="process-pdf-img" class="drawing-img" style="display:none;" alt="工艺流程图" />
            </div>
          </div>
        `;
      }

      // 添加脚本
      html += '<script>' + printScript + '<'+'/script>';

      // 确保结束标签正确
      html += '</body></html>';
      
      // 设置打印HTML内容
      printHtml.value = html;
      
      // 显示打印对话框
      showPrintDialog.value = true;
      
      // 在下一个tick中设置iframe内容
      setTimeout(() => {
        if (printFrame.value) {
          const doc = printFrame.value.contentDocument;
          if (doc) {
            doc.open();
            doc.write(html);
            doc.close();
          }
        }
      }, 100);
      
    } else {
      ElMessage.error('工单缺少产品信息，无法打印');
    }
  } catch (error) {
    console.error('打印工单失败:', error);
    ElMessage.error('打印工单失败');
  }
}

// 处理打印操作
function handlePrint() {
  if (printFrame.value) {
    try {
      printFrame.value.contentWindow?.print();
      
      // 询问用户是否已成功打印
      setTimeout(() => {
        if (currentPrintWorkOrder.value) {
          ElMessageBox.confirm('工单是否已成功打印？', '打印确认', {
            confirmButtonText: '已打印',
            cancelButtonText: '未打印',
            type: 'info'
          }).then(() => {
            // 更新工单状态为已打印
            updateWorkOrderStatus(currentPrintWorkOrder.value.id);
            handlePrintDialogClose();
          }).catch(() => {
            ElMessage({
              type: 'info',
              message: '工单状态未更新，保持"待打印"状态'
            });
          });
        }
      }, 500);
    } catch (e) {
      console.error('打印失败:', e);
      ElMessage.error('打印失败，请重试');
    }
  }
}

// 关闭打印对话框
function handlePrintDialogClose() {
  showPrintDialog.value = false;
  printHtml.value = '';
  currentPrintWorkOrder.value = null;
}

// 更新工单状态为已打印
async function updateWorkOrderStatus(workorderId: number) {
  try {
    await axios.post(`/api/workorders/${workorderId}/mark-as-printed/`);
    ElMessage.success('工单状态已更新为"已下达"');
    fetchWorkOrders(); // 刷新列表
  } catch (error) {
    console.error('更新工单状态失败:', error);
    ElMessage.error('更新工单状态失败');
  }
}
</script>
<style lang="scss" scoped>
.print-dialog {
  :deep(.el-dialog__body) {
    padding: 0;
    overflow: hidden;
  }
  :deep(.el-dialog__header) {
    padding: 10px 20px;
  }
  :deep(.el-dialog__headerbtn) {
    top: 15px;
  }
}

.print-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f5f7fa;
}

.print-actions {
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #dcdfe6;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.print-instruction {
  font-size: 14px;
  color: #606266;
}

.print-buttons {
  display: flex;
  gap: 10px;
}

.print-frame {
  flex: 1;
  height: calc(100vh - 60px); /* 保持高度减去操作栏 */
  min-height: 800px; /* 设置最小高度确保内容可见 */
  width: 100%;
  border: none;
  overflow: auto; /* 允许在需要时滚动 */
  background-color: white;
}

@media print {
  .print-actions {
    display: none;
  }
}
</style>
