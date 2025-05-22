import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 8088,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8900',
        changeOrigin: true,
        secure: false
      }
    }
  },
  // 生产环境构建相关配置可根据需要补充
})
