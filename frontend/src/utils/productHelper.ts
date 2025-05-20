import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

/**
 * 自动应用物料规则并生成物料+BOM（适用于产品新增后自动生成）
 * @param productId 产品ID
 * @returns Promise<void>
 */
export async function applyMaterialRules(productId: number): Promise<void> {
  try {
    // 获取产品详情
    const productResp = await api.get(`/products/${productId}/`)
    const product = productResp.data
    if (!product || !product.category) {
      ElMessage.warning('产品数据不完整，无法获取物料规则')
      return
    }
    // 获取物料规则
    const rulesResp = await api.get('/category-material-rules/', { params: { source_category: product.category } })
    const rules = rulesResp.data.results || rulesResp.data || []
    if (rules.length === 0) {
      ElMessage.warning('当前产品类没有定义BOM物料规则')
      return
    }
    // 只取第一条规则自动生成（如需弹窗选择可扩展）
    const rule = rules[0]
    // --- 新增：延迟并确认参数值写入 ---
    await new Promise(res => setTimeout(res, 200));
    const checkResp = await api.get('/product-param-values/', { params: { product: productId } });
    const paramList = checkResp.data.results || checkResp.data || [];
    if (!Array.isArray(paramList) || paramList.length === 0) {
      ElMessage.error('参数值未写入成功，无法生成物料');
      return;
    }
    // --- end ---
    // 调用后端生成物料和BOM
    const genResp = await api.post('/generate-material/', { rule_id: rule.id, product_id: productId })
    const result = genResp.data
    if (result && result.material) {
      ElMessage.success(`成功${result.material_created ? '创建' : '使用'}物料：${result.material.name}`)
      // 自动生成BOM明细（如BOM和物料都存在，先查重再写入）
      let bomId = null
      if (result.bom) {
        bomId = result.bom.id
      } else {
        if (!product.code) {
          ElMessage.warning('产品代码不存在，无法创建BOM')
          return
        }
        const bomData = {
          product: productId,
          name: `${product.code}-A`,
          version: 'A',
          description: `${product.name}的默认BOM`
        }
        const bomResp = await api.post('/boms/', bomData)
        bomId = bomResp.data.id
      }
      if (bomId && result.material && result.material.id) {
        // 查重
        const bomItemsResp = await api.get('/bom-items/', { params: { bom: bomId, material: result.material.id } })
        const bomItems = bomItemsResp.data.results || bomItemsResp.data || []
        if (!Array.isArray(bomItems) || bomItems.length === 0) {
          const bomItemData = {
            bom: bomId,
            material: result.material.id,
            quantity: 1,
            remark: '自动生成'
          }
          await api.post('/bom-items/', bomItemData)
        }
      }
    }
  } catch (error) {
    console.error('[productHelper] 生成物料失败:', error)
    ElMessage.error('生成物料失败，请重试')
  }
}

/**
 * 自动创建产品工艺流程（工艺流程代码、明细、关联）
 * @param productId 产品ID
 * @returns Promise<void>
 */
export async function createProductProcess(productId: number): Promise<void> {
  try {
    // 获取产品详情
    const productResp = await api.get(`/products/${productId}/`)
    const product = productResp.data
    if (!product || !product.code) {
      ElMessage.warning('产品数据不完整，无法创建工艺流程')
      return
    }
    // 检查是否已有工艺流程
    const existResp = await api.get('/product-process-codes/', { params: { product: productId } })
    const existList = existResp.data.results || existResp.data || []
    if (existList && existList.length > 0) {
      ElMessage.warning('该产品已有工艺流程')
      return
    }
    // 查找或创建工艺流程代码
    const standardCode = `${product.code}-A`
    const codeResp = await api.get('/process-codes/', { params: { code: standardCode, version: 'A' } })
    let codeList = codeResp.data.results || codeResp.data || []
    let processCodeId = null
    const exact = Array.isArray(codeList) ? codeList.find(item => item.code === standardCode && item.version === 'A') : null
    if (exact) {
      processCodeId = exact.id
    } else {
      const processCodeData = {
        code: standardCode,
        name: `${product.name}工艺流程`,
        version: 'A',
        description: `${product.name}的标准工艺流程`
      }
      const createResp = await api.post('/process-codes/', processCodeData)
      processCodeId = createResp.data.id
    }
    if (!processCodeId) {
      ElMessage.error('未能获取有效的工艺流程代码ID')
      return
    }
    // 关联到产品
    const relResp = await api.post('/product-process-codes/', {
      product: productId,
      process_code: processCodeId,
      is_default: true
    });
    const productProcessCodeId = relResp.data.id;
    // 自动生成工艺流程明细（后端带参数替换）
    await api.post(`/product-process-codes/${productProcessCodeId}/auto-generate-details/`);
    ElMessage.success('自动生成工艺流程成功')
  } catch (error) {
    console.error('[productHelper] 自动生成工艺流程失败:', error)
    ElMessage.error('自动生成工艺流程失败')
  }
}

/**
 * 批量保存产品参数值
 * @param productId 产品ID
 * @param paramValues 参数值对象（key为paramId，value为参数值）
 */
export async function saveProductParamValues(productId: number, paramValues: Record<number, string>): Promise<void> {
  try {
    // 调用后端批量删除接口
    await api.post('/product-param-values/bulk-delete/', { product: productId });
    // 批量保存
    const paramArray = Object.entries(paramValues).map(([paramId, value]) => ({
      product: productId,
      param: parseInt(paramId),
      value: value.toString()
    }));
    for (const paramValue of paramArray) {
      await api.post('/product-param-values/', paramValue);
    }
  } catch (error) {
    console.error('[productHelper] 保存参数值失败:', error);
    ElMessage.error('保存产品参数值失败');
    throw error;
  }
}