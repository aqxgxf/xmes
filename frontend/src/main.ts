import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './style.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import axios from 'axios'

// 自动为 axios 请求添加 CSRF Token，兼容 Django 默认 CSRF 方案
axios.interceptors.request.use(config => {
  // 只为修改类请求自动加 token
  if (['post', 'put', 'patch', 'delete'].includes((config.method || '').toLowerCase())) {
    if (config.headers) {
      const match = document.cookie.match(/csrftoken=([^;]+)/)
      if (match) {
        // 兼容 Axios v1/v2 headers 类型
        (config.headers as any)['X-CSRFToken'] = match[1]
      }
    }
  }
  return config
})

const app = createApp(App)
app.use(router)
app.use(ElementPlus, { locale: zhCn })
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.mount('#app')
