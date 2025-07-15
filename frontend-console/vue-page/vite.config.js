import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',  // Docker 必需
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true  // 解决文件监听问题
    }
  }
})
