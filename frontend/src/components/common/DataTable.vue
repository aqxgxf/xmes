<template>
  <div class="data-table-container">
    <!-- Table toolbar with search, filters, and actions -->
    <div v-if="showToolbar" class="table-toolbar">
      <div class="table-toolbar-left">
        <div v-if="showSearch" class="search-container">
          <el-input 
            v-model="searchQuery" 
            :placeholder="searchPlaceholder" 
            prefix-icon="Search"
            clearable
            @input="handleSearch" 
          />
        </div>
        <slot name="filters"></slot>
      </div>
      <div class="table-toolbar-right">
        <slot name="actions"></slot>
      </div>
    </div>

    <!-- Main data table -->
    <el-table
      ref="tableRef"
      v-loading="loading"
      :data="data"
      :height="props.height || undefined"
      :max-height="props.maxHeight || undefined"
      :border="border"
      :stripe="stripe"
      :row-key="rowKey"
      :size="size"
      :empty-text="emptyText"
      :highlight-current-row="highlightCurrentRow"
      :show-header="showHeader"
      :default-sort="defaultSort"
      @selection-change="handleSelectionChange"
      @row-click="handleRowClick"
      @sort-change="handleSortChange"
    >
      <!-- Selection column -->
      <el-table-column
        v-if="selectable"
        type="selection"
        width="55"
        align="center"
        reserve-selection
      />
      
      <!-- Index column -->
      <el-table-column
        v-if="showIndex"
        type="index"
        width="60"
        :label="indexLabel"
        align="center"
      />
      
      <!-- Custom columns -->
      <slot></slot>
      
      <!-- Actions column -->
      <el-table-column
        v-if="showActions"
        :label="actionsLabel"
        :width="actionsWidth"
        :fixed="actionsFixed ? 'right' : false"
        align="center"
      >
        <template #default="scope">
          <slot name="row-actions" :row="scope.row" :index="scope.$index"></slot>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div v-if="showPagination" class="table-pagination">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="pageSizes"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, computed, defineEmits, defineProps, defineExpose } from 'vue'
import type { ElTable } from 'element-plus'

// Define the sort order type ourselves
type SortOrder = 'ascending' | 'descending' | null

interface Sort {
  prop: string;
  order: SortOrder;
}

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  height: {
    type: [String, Number],
    default: ''
  },
  maxHeight: {
    type: [String, Number],
    default: ''
  },
  border: {
    type: Boolean,
    default: true
  },
  stripe: {
    type: Boolean,
    default: false
  },
  rowKey: {
    type: [String, Function],
    default: 'id'
  },
  size: {
    type: String,
    default: 'default'
  },
  emptyText: {
    type: String,
    default: '暂无数据'
  },
  highlightCurrentRow: {
    type: Boolean,
    default: true
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  defaultSort: {
    type: Object as () => Sort,
    default: () => ({})
  },
  
  // Pagination props
  showPagination: {
    type: Boolean,
    default: true
  },
  total: {
    type: Number,
    default: 0
  },
  initialPageSize: {
    type: Number,
    default: 20
  },
  initialCurrentPage: {
    type: Number,
    default: 1
  },
  pageSizes: {
    type: Array as () => number[],
    default: () => [10, 20, 50, 100]
  },
  
  // Selection props
  selectable: {
    type: Boolean,
    default: false
  },
  
  // Index column props
  showIndex: {
    type: Boolean,
    default: false
  },
  indexLabel: {
    type: String,
    default: '序号'
  },
  
  // Actions column props
  showActions: {
    type: Boolean,
    default: false
  },
  actionsLabel: {
    type: String,
    default: '操作'
  },
  actionsWidth: {
    type: [String, Number],
    default: 150
  },
  actionsFixed: {
    type: Boolean,
    default: true
  },
  
  // Toolbar props
  showToolbar: {
    type: Boolean,
    default: true
  },
  
  // Search props
  showSearch: {
    type: Boolean,
    default: false
  },
  searchPlaceholder: {
    type: String,
    default: '搜索...'
  }
})

const emit = defineEmits([
  'page-change', 
  'size-change', 
  'selection-change', 
  'search', 
  'row-click',
  'sort-change',
  'update:currentPage',
  'update:pageSize'
])

// Table reference
const tableRef = ref<InstanceType<typeof ElTable>>()

// Pagination state
const currentPage = ref(props.initialCurrentPage)
const pageSize = ref(props.initialPageSize)

// Search state
const searchQuery = ref('')

// watch for prop changes
watch(() => props.initialCurrentPage, (val) => {
  currentPage.value = val
})

watch(() => props.initialPageSize, (val) => {
  pageSize.value = val
})

// Handlers
const handleSizeChange = (val: number) => {
  pageSize.value = val
  emit('size-change', val)
  emit('update:pageSize', val)
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  emit('page-change', val)
  emit('update:currentPage', val)
}

const handleSelectionChange = (selection: any[]) => {
  emit('selection-change', selection)
}

const handleSearch = (val: string) => {
  emit('search', val)
}

const handleRowClick = (row: any, column: any, event: Event) => {
  emit('row-click', row, column, event)
}

const handleSortChange = (sortInfo: { column: any, prop: string, order: SortOrder }) => {
  emit('sort-change', sortInfo)
}

// Expose methods
defineExpose({
  // Clear selected rows
  clearSelection: () => {
    if (tableRef.value) {
      tableRef.value.clearSelection()
    }
  },
  // Toggle row selection
  toggleRowSelection: (row: any, selected?: boolean) => {
    if (tableRef.value) {
      tableRef.value.toggleRowSelection(row, selected)
    }
  },
  // Toggle all rows selection
  toggleAllSelection: () => {
    if (tableRef.value) {
      tableRef.value.toggleAllSelection()
    }
  },
  // Manually set current page
  setCurrentPage: (page: number) => {
    currentPage.value = page
  },
  // Manually set page size
  setPageSize: (size: number) => {
    pageSize.value = size
  },
  // Get current pagination state
  getPagination: () => ({
    currentPage: currentPage.value,
    pageSize: pageSize.value,
    total: props.total
  }),
  // Clear search
  clearSearch: () => {
    searchQuery.value = ''
  }
})
</script>

<style scoped>
.data-table-container {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.table-toolbar {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-toolbar-left,
.table-toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-container {
  width: 260px;
}

.table-pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style> 