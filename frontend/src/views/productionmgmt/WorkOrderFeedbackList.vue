<template>
  <div class="workorder-feedback-list-container page-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <h2 class="page-title">工单回冲明细查询</h2>
        </div>
      </template>

      <!-- 搜索区域 -->
      <div class="search-section">
        <el-form :inline="true" class="search-form" @submit.prevent="searchFeedbacks">
          <el-form-item label="工单号">
            <el-input
              v-model="searchForm.workorderNo"
              placeholder="请输入工单号"
              clearable
              @keyup.enter.prevent="searchFeedbacks"
            />
          </el-form-item>
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              :shortcuts="dateRangeShortcuts"
            />
          </el-form-item>
          <el-form-item label="工序">
            <el-input
              v-model="searchForm.processName"
              placeholder="请输入工序名称"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click.prevent="searchFeedbacks">
              <el-icon><Search /></el-icon> 查询
            </el-button>
            <el-button @click.prevent="resetSearch">
              <el-icon><Refresh /></el-icon> 重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 数据表格 -->
      <div class="feedback-table-container">
        <el-table
          v-loading="loading"
          :data="feedbacks"
          border
          stripe
          style="width: 100%"
        >
          <el-table-column prop="workorder_no" label="工单号" min-width="120" />
          <el-table-column prop="product_name" label="产品" min-width="150" />
          <el-table-column prop="step_no" label="工序号" width="80" align="center" />
          <el-table-column prop="process_name" label="工序名称" min-width="120" />
          <el-table-column prop="process_content" label="工序内容" min-width="180" :show-overflow-tooltip="true" />
          <el-table-column prop="completed_quantity" label="完成数量" width="100" align="right" />
          <el-table-column prop="defective_quantity" label="不良品数量" width="100" align="right" />
          <el-table-column prop="defective_reason" label="不良原因" min-width="180" :show-overflow-tooltip="true" />
          <el-table-column prop="created_by" label="操作人" width="120" />
          <el-table-column prop="created_at" label="回冲时间" min-width="160" />
          <el-table-column prop="remark" label="备注" min-width="180" :show-overflow-tooltip="true" />
          <el-table-column label="操作" width="120" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                size="small"
                type="primary"
                @click="viewFeedbackDetail(row)"
              >
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            @update:current-page="currentPage = $event"
            @update:page-size="pageSize = $event"
          />
        </div>
      </div>
    </el-card>

    <!-- 回冲详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="回冲明细详情"
      width="700px"
      destroy-on-close
    >
      <el-descriptions v-if="currentFeedback" :column="2" border>
        <el-descriptions-item label="工单号">{{ currentFeedback.workorder_no }}</el-descriptions-item>
        <el-descriptions-item label="产品">{{ currentFeedback.product_name }}</el-descriptions-item>
        <el-descriptions-item label="工序号">{{ currentFeedback.step_no }}</el-descriptions-item>
        <el-descriptions-item label="工序名称">{{ currentFeedback.process_name }}</el-descriptions-item>
        <el-descriptions-item label="完成数量" :span="2">{{ currentFeedback.completed_quantity }}</el-descriptions-item>
        <el-descriptions-item label="不良品数量" :span="2">{{ currentFeedback.defective_quantity }}</el-descriptions-item>
        <el-descriptions-item label="工序内容" :span="2">{{ currentFeedback.process_content || '-' }}</el-descriptions-item>
        <el-descriptions-item label="不良原因" :span="2">{{ currentFeedback.defective_reason || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ currentFeedback.created_by }}</el-descriptions-item>
        <el-descriptions-item label="回冲时间">{{ currentFeedback.created_at }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentFeedback.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'
import type { Feedback } from '../../types/index'

// 搜索表单
const searchForm = reactive({
  workorderNo: '',
  processName: '',
  startDate: '',
  endDate: ''
})

// 日期范围选择器
const dateRange = ref<[string, string] | null>(null)
// 日期范围快捷方式
const dateRangeShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  },
]

// 监听日期范围变化，更新搜索表单
watch(dateRange, (newVal) => {
  if (newVal) {
    searchForm.startDate = newVal[0]
    searchForm.endDate = newVal[1]
  } else {
    searchForm.startDate = ''
    searchForm.endDate = ''
  }
})

// 分页和数据相关状态
const loading = ref(false)
const feedbacks = ref<Feedback[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const currentFeedback = ref<Feedback | null>(null)

// 查询回冲记录
const searchFeedbacks = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (searchForm.workorderNo) {
      params.workorder_no = searchForm.workorderNo
    }

    if (searchForm.processName) {
      params.process_name = searchForm.processName
    }

    if (searchForm.startDate) {
      params.start_date = searchForm.startDate
    }

    if (searchForm.endDate) {
      params.end_date = searchForm.endDate
    }

    // 发送请求
    const response = await axios.get('/api/workorder-feedbacks/', { params })
    
    if (response.data && response.data.results) {
      feedbacks.value = response.data.results
      total.value = response.data.count || 0
    } else if (Array.isArray(response.data)) {
      feedbacks.value = response.data
      total.value = response.data.length
    } else {
      feedbacks.value = []
      total.value = 0
    }
  } catch (error: any) {
    console.error('获取回冲记录失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取回冲记录失败')
    feedbacks.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 重置搜索条件
const resetSearch = () => {
  searchForm.workorderNo = ''
  searchForm.processName = ''
  dateRange.value = null
  searchForm.startDate = ''
  searchForm.endDate = ''
  currentPage.value = 1
  searchFeedbacks()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  searchFeedbacks()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  searchFeedbacks()
}

// 查看回冲详情
const viewFeedbackDetail = (row: Feedback) => {
  currentFeedback.value = row
  dialogVisible.value = true
}

// 页面加载时自动查询
searchFeedbacks()
</script>

<style lang="scss" scoped>
.workorder-feedback-list-container {
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .page-title {
    margin: 0;
    font-size: 18px;
  }
  
  .search-section {
    margin-bottom: 24px;
  }
  
  .feedback-table-container {
    margin-top: 16px;
  }
  
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
}
</style>