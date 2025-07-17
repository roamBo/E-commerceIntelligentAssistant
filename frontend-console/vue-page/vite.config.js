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
    proxy: {
      '/api/agents': {
        target: 'http://10.172.66.224:8084',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: (proxy, options) => {
          // 打印代理请求和响应信息，帮助调试
          proxy.on('error', (err, req, res) => {
            console.log('代理错误:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('发送请求到:', proxyReq.path);
            
            // 打印请求体内容（如果有）
            if (req.body) {
              console.log('请求体内容:', req.body);
            }
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('收到响应:', proxyRes.statusCode);
            
            // 尝试记录响应体
            let responseBody = '';
            proxyRes.on('data', function(chunk) {
              responseBody += chunk;
            });
            proxyRes.on('end', function() {
              try {
                console.log('响应体内容:', responseBody);
              } catch (e) {
                console.log('无法解析响应体');
              }
            });
          });
        }
      },
      // 支付服务代理配置
      '/payment/api': {
        target: 'http://10.172.66.224:8084',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('支付服务代理错误:', err);
          });
        }
      },
      // 订单服务代理配置
      '/order/api': {
        target: 'http://10.172.66.224:8084',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('订单服务代理错误:', err);
          });
        }
      }
    },
    cors: true
  }
})
