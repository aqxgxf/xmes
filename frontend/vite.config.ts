import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [vue()],
  server: {
    port: mode === 'test' ? 9001 : 8088,
    proxy: {
      '/api': {
        target: mode === 'test' ? 'http://localhost:8001' : 'http://127.0.0.1:8900',
        changeOrigin: true,
        secure: false,
        rewrite: path => path.replace(/^\/api/, '/api')
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  // 生产环境构建相关配置可根据需要补充
}))
