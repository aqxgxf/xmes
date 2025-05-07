<template>
  <el-card style="width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:18px;font-weight:bold;">BOM明细管理</span>
      <div style="display:flex;gap:8px;align-items:center;">
        <el-select v-model="searchBom" filterable clearable placeholder="筛选BOM" style="width:220px;margin-right:8px;" @change="fetchData">
          <el-option v-for="item in bomList" :key="item.id" :label="item.name + ' (v' + item.version + ') ' + item.product_name" :value="item.id" />
        </el-select>
        <el-button type="primary" @click="openAddDialog">新增明细</el-button>
        <el-upload
          :show-file-list="false"
          :before-upload="beforeImport"
          :http-request="handleImport"
          accept=".xlsx,.xls,.csv"
        >
          <el-button type="success">导入</el-button>
        </el-upload>
      </div>
    </div>
    <el-table :data="list" style="width: 100%; margin-top: 12px" :loading="loading">
      <el-table-column prop="bom_name" label="BOM" min-width="160" />
      <el-table-column prop="material_name" label="物料" min-width="120" />
      <el-table-column prop="quantity" label="用量" min-width="100" />
      <el-table-column prop="remark" label="备注" min-width="120" />
      <el-table-column label="操作" min-width="140">
        <template #default="scope">
          <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="table-pagination">
      <el-pagination
        background
        layout="sizes, prev, pager, next, jumper, ->, total"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        :page-sizes="[5, 10, 20, 50, 100]"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @close="closeDialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" label-position="left">
        <el-form-item label="BOM" prop="bom">
          <el-select v-model="form.bom" filterable placeholder="请选择BOM" style="width:320px">
            <el-option v-for="item in bomList" :key="item.id" :label="item.name + ' (v' + item.version + ') ' + item.product_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="物料" prop="material">
          <el-select v-model="form.material" filterable placeholder="请选择物料" style="width:320px">
            <el-option v-for="item in materialList" :key="item.id" :label="item.name+ '（' + item.code + '）'" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="用量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="0" :step="1" style="width:320px" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" style="width:320px" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
const loading = ref(false)
const list = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchBom = ref()
const dialogVisible = ref(false)
const dialogTitle = ref('新增BOM明细')
const form = reactive({
  id: null,
  bom: '',
  material: '',
  quantity: 1,
  remark: ''
})
const formRef = ref()
const bomList = ref<any[]>([])
const materialList = ref<any[]>([])
const rules = {
  bom: [{ required: true, message: '请选择BOM', trigger: 'change' }],
  material: [{ required: true, message: '请选择物料', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入用量', trigger: 'blur' }]
}
function fetchBomList() {
  axios.get('/api/boms/', { params: { page_size: 1000 } }).then(res => {
    bomList.value = res.data.results || res.data
  })
}
function fetchMaterialList() {
  axios.get('/api/products/', { params: { page_size: 1000 } }).then(res => {
    materialList.value = res.data.results || res.data
  })
}
function fetchData() {
  loading.value = true
  const params: any = {
    page: currentPage.value,
    page_size: pageSize.value
  }
  if (searchBom.value) {
    params.bom = searchBom.value
  }
  axios.get('/api/bom-items/', { params }).then(res => {
    list.value = res.data.results || res.data
    total.value = res.data.count || res.data.length
  }).finally(() => loading.value = false)
}
function openAddDialog() {
  dialogTitle.value = '新增BOM明细'
  Object.assign(form, { id: null, bom: searchBom.value || '', material: '', quantity: 1, remark: '' })
  dialogVisible.value = true
}
function openEditDialog(row: any) {
  dialogTitle.value = '编辑BOM明细'
  Object.assign(form, { ...row, bom: row.bom, material: row.material })
  dialogVisible.value = true
}
function closeDialog() {
  dialogVisible.value = false
  form.id = null
  form.bom = searchBom.value || ''
  form.material = ''
  form.quantity = 1
  form.remark = ''
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
function submit() {
  (formRef.value as any).validate(async (valid: boolean) => {
    if (!valid) return
    if (!form.bom) {
      ElMessage.error('请选择BOM')
      return
    }
    const data = {
      bom: form.bom,
      material: form.material,
      quantity: form.quantity,
      remark: form.remark
    }
    // console.log('Submitting data:', data)
    try {
      const config = {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      }
      if (form.id) {
        // const response = await axios.put(`/api/bom-items/${form.id}/`, data, config)
        // console.log('Update Response:', response.data)
        ElMessage.success('修改成功')
        dialogVisible.value = false
        closeDialog()
      } else {
        const response = await axios.post('/api/bom-items/', data, config)
        // console.log('Create Response:', response.data)
        ElMessage.success('新增成功')
        dialogVisible.value = false
        closeDialog()
      }
      await fetchData()
    } catch (e: any) {
      // console.error('Full error:', e)
      // console.error('Error response:', e.response)
      // console.error('Error data:', e.response?.data)
      // console.error('Error status:', e.response?.status)
      // console.error('Error headers:', e.response?.headers)
      
      let errorMessage = '保存失败'
      if (e.response?.data) {
        if (typeof e.response.data === 'string') {
          const match = e.response.data.match(/IntegrityError.*?at.*?\n(.*?)(?:\n|$)/)
          if (match) {
            errorMessage = match[1].trim()
          } else {
            errorMessage = '服务器内部错误，请稍后重试'
          }
        } else if (e.response.data.detail) {
          errorMessage = e.response.data.detail
        } else if (e.response.data.material) {
          errorMessage = e.response.data.material[0]
        } else if (e.response.data.bom) {
          errorMessage = e.response.data.bom[0]
        } else if (e.response.data.quantity) {
          errorMessage = e.response.data.quantity[0]
        }
      }
      ElMessage.error(errorMessage)
    }
  })
}
function remove(row: any) {
  ElMessageBox.confirm('确定要删除该BOM明细吗？', '提示', { type: 'warning' })
    .then(async () => {
      await axios.delete(`/api/bom-items/${row.id}/`)
      ElMessage.success('删除成功')
      fetchData()
    })
}
function handlePageChange(val: number) {
  currentPage.value = val
  fetchData()
}
function handleSizeChange(val: number) {
  pageSize.value = val
  currentPage.value = 1
  fetchData()
}
onMounted(() => {
  fetchBomList()
  fetchMaterialList()
  fetchData()
})
// 导入相关
function beforeImport(file: File) {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!["xlsx", "xls", "csv"].includes(ext!)) {
    ElMessage.error('仅支持Excel或CSV文件')
    return false
  }
  return true
}
async function handleImport(option: any) {
  const formData = new FormData()
  formData.append('file', option.file)
  try {
    const res = await axios.post('/api/bom-items/import/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success(res.data?.msg || '导入成功')
    fetchData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.msg || '导入失败')
  }
}
</script>
<style>
@import '/src/style.css';
</style>
