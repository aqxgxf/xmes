import { defineStore } from 'pinia'
import type { WorkOrder, WorkOrderForm } from '@/types/index'
import axios from 'axios'

export const useWorkOrderStore = defineStore('workOrder', {
  state: () => ({
    list: [] as WorkOrder[],
    total: 0,
    loading: false,
    error: '',
    current: null as WorkOrder | null,
  }),
  actions: {
    async fetchList(params?: any) {
      this.loading = true
      try {
        const res = await axios.get('/api/workorders/', { params })
        this.list = res.data.results || res.data
        this.total = res.data.count || this.list.length
        this.error = ''
      } catch (e: any) {
        this.error = e.message || '加载失败'
      } finally {
        this.loading = false
      }
    },
    async fetchOne(id: number) {
      this.loading = true
      try {
        const res = await axios.get(`/api/workorders/${id}/`)
        this.current = res.data
        this.error = ''
      } catch (e: any) {
        this.error = e.message || '加载失败'
      } finally {
        this.loading = false
      }
    },
    async create(data: WorkOrderForm) {
      this.loading = true
      try {
        const res = await axios.post('/api/workorders/', data)
        this.error = ''
        return res.data
      } catch (e: any) {
        this.error = e.message || '创建失败'
        throw e
      } finally {
        this.loading = false
      }
    },
    async update(id: number, data: WorkOrderForm) {
      this.loading = true
      try {
        const res = await axios.put(`/api/workorders/${id}/`, data)
        this.error = ''
        return res.data
      } catch (e: any) {
        this.error = e.message || '更新失败'
        throw e
      } finally {
        this.loading = false
      }
    },
    async remove(id: number) {
      this.loading = true
      try {
        await axios.delete(`/api/workorders/${id}/`)
        this.error = ''
      } catch (e: any) {
        this.error = e.message || '删除失败'
        throw e
      } finally {
        this.loading = false
      }
    },
    async changeStatus(id: number, status: string) {
      this.loading = true
      try {
        await axios.post(`/api/workorders/${id}/change-status/`, { status })
        this.error = ''
      } catch (e: any) {
        this.error = e.message || '状态变更失败'
        throw e
      } finally {
        this.loading = false
      }
    },
    async print(id: number) {
      // 可扩展打印相关API
    }
  }
})
