<template>
  <div class="bom-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">BOM管理</h2>
          <div class="search-actions">
            <el-input v-model="bomStore.searchQuery" placeholder="搜索BOM名称/产品/版本" clearable @input="handleSearch">
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="openAddDialog">
              <el-icon>
                <Plus />
              </el-icon> 新增BOM
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table :data="bomStore.boms" v-loading="bomStore.loading" border stripe style="width: 100%">
        <el-table-column prop="name" label="BOM代码" min-width="180" />
        <el-table-column prop="product_name" label="产品" min-width="160" />
        <el-table-column prop="version" label="版本" width="100" align="center" />
        <el-table-column prop="description" label="描述" min-width="180" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" @click="openEditDialog(row)">
                <el-icon>
                  <Edit />
                </el-icon> 编辑
              </el-button>
              <el-button size="small" type="danger" @click="confirmDelete(row)">
                <el-icon>
                  <Delete />
                </el-icon> 删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页控件 -->
      <div class="pagination-container">
        <el-pagination v-model:current-page="bomStore.currentPage" v-model:page-size="bomStore.pageSize"
          :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" :total="bomStore.total"
          @size-change="bomStore.handleSizeChange" @current-change="bomStore.handleCurrentChange" background />
      </div>
    </el-card>

    <!-- BOM表单对话框 -->
    <bom-form-dialog v-model:visible="showDialog" :title="currentFormMode === 'add' ? '新增BOM' : '编辑BOM'"
      :loading="bomStore.submitting" :form="formStore.form" :rules="formStore.rules" :products="bomStore.products"
      :version-options="bomStore.versionOptions" @save="saveBom" @close="closeDialog"
      @update:product="handleProductChange" @update:version="handleVersionChange" :product="formStore.form.product"
      :version="formStore.form.version" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'
import { useBomStore } from '../../../stores/bomStore'
import { useBomForm } from '../../../composables/useBomForm'
import BomFormDialog from '../../../components/basedata/BomFormDialog.vue'
import type { Bom } from '../../../types/common'

// 获取Store
const bomStore = useBomStore()

// 使用表单逻辑组合式函数
const formStore = useBomForm(bomStore.products)

// 对话框状态
const showDialog = ref(false)
const currentFormMode = ref<'add' | 'edit'>('add')

// 打开新增对话框
const openAddDialog = () => {
  formStore.resetForm()
  currentFormMode.value = 'add'
  showDialog.value = true
  setTimeout(() => {
    console.log('新增BOM对话框打开')
    // 不需要任何处理，直接依赖组件内的自动生成逻辑
  }, 100)
}

// 打开编辑对话框
const openEditDialog = (bom: Bom) => {
  formStore.fillForm(bom)
  currentFormMode.value = 'edit'
  showDialog.value = true
  setTimeout(() => {
    console.log('编辑BOM对话框打开')
    // 不需要任何处理，直接依赖组件内的自动生成逻辑
  }, 100)
}

// 关闭对话框
const closeDialog = () => {
  showDialog.value = false
}

// 保存BOM
const saveBom = async () => {
  try {
    if (currentFormMode.value === 'add') {
      await bomStore.createBom(formStore.form)
      ElMessage.success('添加BOM成功')
    } else {
      if (!formStore.form.id) return
      await bomStore.updateBom(formStore.form.id, formStore.form)
      ElMessage.success('更新BOM成功')
    }

    closeDialog()
  } catch (error: any) {
    const errorMsg = bomStore.handleApiError(error, '保存BOM失败')
    ElMessage.error(errorMsg)
  }
}

// 确认删除
const confirmDelete = (row: Bom) => {
  if (!row.id) return

  ElMessageBox.confirm(
    `确定要删除BOM "${row.name}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await bomStore.deleteBom(row.id)
      ElMessage.success('删除BOM成功')
    } catch (error: any) {
      const errorMsg = bomStore.handleApiError(error, '删除BOM失败')
      ElMessage.error(errorMsg)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 搜索处理
const handleSearch = () => {
  bomStore.setSearchQuery(bomStore.searchQuery)
}

// 处理产品变更
const handleProductChange = () => {
  console.log('BomList 收到产品变更事件')
  // 所有逻辑移至组件内部
}

// 处理版本变更
const handleVersionChange = () => {
  console.log('BomList 收到版本变更事件')
  // 所有逻辑移至组件内部
}

// 页面初始化
onMounted(() => {
  bomStore.initialize()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.bom-container {
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page-title {
    margin: 0;
    font-size: 18px;
  }

  .search-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
