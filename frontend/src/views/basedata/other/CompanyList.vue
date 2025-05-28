<template>
  <div class="company-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">客户管理</h2>
          <div class="search-actions">
            <el-input v-model="companyStore.search" placeholder="搜索名称/代码/联系人" clearable @input="handleSearch">
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="openAddDialog">
              <el-icon>
                <Plus />
              </el-icon> 新增客户
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-empty v-if="!companyStore.loading && companyStore.companies.length === 0" description="暂无客户数据"
        :image-size="200">
        <template #image>
          <div class="empty-wrapper">
            <el-icon class="empty-icon">
              <OfficeBuilding />
            </el-icon>
            <div v-if="companyStore.error" class="error-message">
              {{ companyStore.error }}
            </div>
          </div>
        </template>
        <el-button type="primary" @click="openAddDialog">创建客户</el-button>
        <el-button v-if="companyStore.error" @click="companyStore.fetchCompanies()">重试加载</el-button>
      </el-empty>

      <el-table v-else :data="companyStore.filteredCompanies" v-loading="companyStore.loading" border stripe
        style="width: 100%">
        <el-table-column prop="name" label="客户名称" min-width="150" />
        <el-table-column prop="code" label="客户代码" min-width="120" />
        <el-table-column prop="address" label="地址" min-width="200" />
        <el-table-column prop="contact" label="联系人" min-width="120" />
        <el-table-column prop="phone" label="联系电话" min-width="120" />
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
      <div class="pagination-container" v-if="companyStore.companies.length > 0">
        <el-pagination v-model:current-page="companyStore.currentPage" v-model:page-size="companyStore.pageSize"
          :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" :total="companyStore.total"
          @size-change="companyStore.handleSizeChange" @current-change="companyStore.handleCurrentChange" background />
      </div>
    </el-card>

    <!-- 添加客户对话框 -->
    <company-form-dialog v-model:visible="showAddDialog" title="新增客户" :form="formData.form" :rules="formData.rules"
      :loading="companyStore.submitting" @save="saveCompany" @close="closeAddDialog" />

    <!-- 编辑客户对话框 -->
    <company-form-dialog v-model:visible="showEditDialog" title="编辑客户" :form="formData.form" :rules="formData.rules"
      :loading="companyStore.submitting" @save="updateCompany" @close="closeEditDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, OfficeBuilding } from '@element-plus/icons-vue'
import { useCompanyForm } from '../../../composables/useCompanyForm'
import { useCompanyStore } from '../../../stores/companyStore'
import CompanyFormDialog from '../../../components/basedata/CompanyFormDialog.vue'
import type { Company } from '../../../types'

// 使用Store
const companyStore = useCompanyStore()

// 使用表单逻辑组合式函数
const formData = useCompanyForm()
const { form, rules, resetForm, loadFormData } = formData

// 对话框状态
const showAddDialog = ref(false)
const showEditDialog = ref(false)

// 搜索处理
const handleSearch = () => {
  companyStore.currentPage = 1
  if (companyStore.search === '') {
    companyStore.fetchCompanies()
  }
}

// 对话框操作
const openAddDialog = () => {
  resetForm()
  showAddDialog.value = true
}

const closeAddDialog = () => {
  showAddDialog.value = false
}

const openEditDialog = (row: Company) => {
  resetForm()
  loadFormData(row)
  showEditDialog.value = true
}

const closeEditDialog = () => {
  showEditDialog.value = false
}

// 保存客户
const saveCompany = async () => {
  try {
    await companyStore.createCompany(form)
    ElMessage.success('新增客户成功')
    closeAddDialog()
  } catch (error: any) {
    const errorMsg = companyStore.handleApiError(error, '保存客户失败')
    ElMessage.error(errorMsg)
  }
}

const updateCompany = async () => {
  if (!form.id) return

  try {
    await companyStore.updateCompany(form.id, form)
    ElMessage.success('更新客户成功')
    closeEditDialog()
  } catch (error: any) {
    const errorMsg = companyStore.handleApiError(error, '更新客户失败')
    ElMessage.error(errorMsg)
  }
}

// 删除客户
const confirmDelete = (row: Company) => {
  ElMessageBox.confirm(
    `确定要删除客户 "${row.name}" 吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await companyStore.deleteCompany(row.id)
      ElMessage.success('删除客户成功')
    } catch (error: any) {
      const errorMsg = companyStore.handleApiError(error, '删除客户失败')
      ElMessage.error(errorMsg)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 页面初始化
onMounted(() => {
  companyStore.initialize()
})
</script>

<style lang="scss" scoped>
@use '../../../assets/styles/common.scss' as *;

.company-container {
  .search-input {
    width: 240px;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }

  .empty-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .empty-icon {
    font-size: 60px;
    color: #909399;
    margin-bottom: 20px;
  }

  .error-message {
    color: #f56c6c;
    max-width: 300px;
    text-align: center;
    margin: 10px 0;
  }
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  .search-actions {
    display: flex;
    gap: 10px;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
