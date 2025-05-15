import { ref } from 'vue'
import type { Ref } from 'vue'

/**
 * 通用分页逻辑组合式函数
 * @param fetchFunction 获取数据的函数，会在分页参数变化时调用
 * @param initialPageSize 初始每页数量，默认10
 * @param initialPage 初始页码，默认1
 */
export function usePagination(
  fetchFunction: () => Promise<void> | void,
  initialPageSize = 10,
  initialPage = 1
) {
  const currentPage = ref(initialPage)
  const pageSize = ref(initialPageSize)
  const total = ref(0)

  // 处理每页数量变化
  const handleSizeChange = (val: number) => {
    pageSize.value = val
    fetchFunction()
  }

  // 处理页码变化
  const handleCurrentChange = (val: number) => {
    currentPage.value = val
    fetchFunction()
  }

  return {
    currentPage,
    pageSize,
    total,
    handleSizeChange,
    handleCurrentChange
  }
}
