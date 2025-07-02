<template>
  <div class="shopping-guide">
    <div class="chat-container">
      <div class="chat-header">
        <h2>个性化导购助手</h2>
        <el-button 
          v-if="messages.length > 0" 
          type="text" 
          icon="el-icon-delete" 
          @click="clearChat"
          class="clear-btn"
        >清除对话</el-button>
      </div>
      <div class="chat-body" ref="chatBody">
        <!-- 欢迎消息 -->
        <div class="welcome-message" v-if="messages.length === 0">
          <div class="ai-avatar">
            <span class="emoji-avatar">🤖</span>
          </div>
          <div class="welcome-content">
            <h3>您好！我是您的个性化导购助手</h3>
            <p class="welcome-hint">您可以直接告诉我您需要什么商品，我将帮您完成推荐商品、购买下单、支付和物流跟踪的全流程服务。</p>
            <div class="quick-actions">
              <el-button size="small" @click="quickSend('如何使用这个导购助手？')">如何使用导购助手</el-button>
              <el-button size="small" @click="quickSend('你能提供哪些服务？')">查看服务范围</el-button>
              <el-button size="small" @click="quickSend('联系客服')">联系客服</el-button>
            </div>
          </div>
        </div>
        
        <!-- 聊天消息 -->
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          :class="['message-item', message.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <div v-if="message.role !== 'user'" class="ai-avatar">
            <span class="emoji-avatar">🤖</span>
          </div>
          <div class="message-content">
            <div v-if="message.thinking && message.role !== 'user'" class="thinking-dots">
              <span></span><span></span><span></span>
            </div>
            <div v-else-if="message.type === 'orders'">
              <div class="orders-list">
                <div v-for="(order, i) in message.orders" :key="i" class="product-card">
                  <div class="product-details">
                    <h4>{{ order.name }}</h4>
                    <div class="product-meta">
                      <span class="product-stock">数量: {{ order.count }}</span>
                    </div>
                    <div class="product-price-container">
                      <span class="product-price">¥{{ order.price }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else v-html="formatMessage(message.text)"></div>
          </div>
          <div v-if="message.role === 'user'" class="user-avatar">
            <span class="emoji-avatar">👤</span>
          </div>
        </div>
      </div>
      
      <div class="chat-input">
        <el-input
          v-model="input"
          placeholder="请描述您想找的商品或询问导购助手..."
          @keyup.enter="sendMsg"
          :disabled="isProcessing"
          clearable
        >
          <template #append>
            <el-button 
              :icon="isProcessing ? 'el-icon-loading' : 'el-icon-s-promotion'" 
              @click="sendMsg" 
              :disabled="!input.trim() || isProcessing"
            >发送</el-button>
          </template>
        </el-input>
      </div>
    </div>
    
    <!-- 侧边快捷功能 -->
    <div class="side-panel">
      <div class="side-card" @click="quickSend('帮我查一下我下了什么订单', true)">
        <div class="side-icon">🛒</div>
        <div class="side-title">订单查询</div>
        <div class="side-desc">一键查询我的所有订单</div>
      </div>
      <div class="side-card" @click="quickSend('帮我查一下我要付多少钱')">
        <div class="side-icon">💰</div>
        <div class="side-title">支付查询</div>
        <div class="side-desc">快速查看应付金额</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'

const chatBody = ref(null)
const messages = ref([
  { role: 'bot', text: '您好，有什么可以帮您？' }
])
const input = ref('')
const isProcessing = ref(false)

function sendMsg() {
  const text = input.value.trim()
  if (!text || isProcessing.value) return
  
  handleUserInput(text)
  input.value = ''
  scrollToBottom()
}

function quickSend(text, isOrder) {
  if (isProcessing.value) return
  
  handleUserInput(text, isOrder)
  scrollToBottom()
}

function handleUserInput(text, isOrder) {
  messages.value.push({ role: 'user', text })
  
  // 添加思考状态
  isProcessing.value = true
  
  if (text.includes('订单')) {
    fetchOrders()
  } else if (text.includes('付钱') || text.includes('付多少')) {
    fetchTotal()
  } else {
    setTimeout(() => {
      messages.value.push({ 
        role: 'bot', 
        text: '我们需要集成实际的API来处理您的请求。目前系统正在准备中，暂时无法处理具体业务。请稍后再试，或联系客服获取更多帮助。' 
      })
      isProcessing.value = false
      scrollToBottom()
    }, 600)
  }
}

function fetchOrders() {
  // 模拟获取订单数据
  setTimeout(() => {
    const mockOrders = [
      { name: '高性能笔记本电脑', count: 1, price: 6999 },
      { name: '无线蓝牙耳机', count: 2, price: 499 },
      { name: '智能手表', count: 1, price: 1299 }
    ]
    
    messages.value.push({
      role: 'bot',
      type: 'orders',
      orders: mockOrders
    })
    
    isProcessing.value = false
    scrollToBottom()
  }, 800)
}

function fetchTotal() {
  // 模拟获取订单总额
  setTimeout(() => {
    const total = 6999 + (499 * 2) + 1299
    messages.value.push({ 
      role: 'bot', 
      text: `您所有订单应付总金额为：¥${total}` 
    })
    
    isProcessing.value = false
    scrollToBottom()
  }, 800)
}

// 清除聊天记录
const clearChat = () => {
  messages.value = [
    { role: 'bot', text: '您好，有什么可以帮您？' }
  ]
}

// 格式化消息，处理换行和链接
const formatMessage = (message) => {
  if (!message) return ''
  return message
    .replace(/\n/g, '<br>')
    .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>')
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (chatBody.value) {
    chatBody.value.scrollTop = chatBody.value.scrollHeight
  }
}

// 监听消息变化，自动滚动到底部
watch(messages, () => {
  scrollToBottom()
}, { deep: true })

// 组件挂载时滚动到底部
onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.shopping-guide {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #1a2035 0%, #101425 100%);
  position: relative;
  overflow: hidden;
}

.shopping-guide::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(100, 255, 218, 0.03) 0%, transparent 20%),
    radial-gradient(circle at 90% 80%, rgba(64, 158, 255, 0.03) 0%, transparent 20%),
    radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 40%);
  z-index: 0;
}

.chat-container {
  max-width: 900px;
  width: 100%;
  height: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  background: rgba(22, 28, 45, 0.8);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  position: relative;
  z-index: 1;
  border: 1px solid rgba(100, 255, 218, 0.1);
  overflow: hidden;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid rgba(100, 255, 218, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(16, 20, 37, 0.9);
  position: relative;
}

.chat-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(100, 255, 218, 0.5), transparent);
  animation: scanLine 4s linear infinite;
}

@keyframes scanLine {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.chat-header h2 {
  margin: 0;
  color: #64ffda;
  font-size: 20px;
  letter-spacing: 1px;
  text-shadow: 0 0 10px rgba(100, 255, 218, 0.5);
  position: relative;
  display: inline-block;
}

.chat-header h2::before {
  content: '●';
  color: #64ffda;
  position: absolute;
  left: -20px;
  animation: pulse 2s infinite;
  font-size: 10px;
}

@keyframes pulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.clear-btn {
  color: rgba(100, 255, 218, 0.7);
}

.clear-btn:hover {
  color: #64ffda;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  scrollbar-width: thin;
  scrollbar-color: rgba(100, 255, 218, 0.3) rgba(22, 28, 45, 0.2);
}

.chat-body::-webkit-scrollbar {
  width: 6px;
}

.chat-body::-webkit-scrollbar-track {
  background: rgba(22, 28, 45, 0.2);
}

.chat-body::-webkit-scrollbar-thumb {
  background-color: rgba(100, 255, 218, 0.3);
  border-radius: 3px;
  border: 1px solid rgba(22, 28, 45, 0.2);
}

.chat-input {
  padding: 20px 24px;
  border-top: 1px solid rgba(100, 255, 218, 0.1);
  background: rgba(16, 20, 37, 0.9);
  position: relative;
}

.chat-input::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(100, 255, 218, 0.5), transparent);
}

.chat-input .el-input__inner {
  background: rgba(30, 38, 60, 0.6);
  border: 1px solid rgba(100, 255, 218, 0.2);
  color: #ffffff;
  transition: all 0.3s ease;
}

.chat-input .el-input__inner:focus {
  border-color: rgba(100, 255, 218, 0.6);
  box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
}

.chat-input .el-input-group__append button {
  background: linear-gradient(135deg, #33a3ff 0%, #0063e5 100%);
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.chat-input .el-input-group__append button:hover:not(:disabled) {
  background: linear-gradient(135deg, #44b4ff 0%, #1174f6 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.welcome-message {
  display: flex;
  padding: 25px;
  background: rgba(30, 38, 60, 0.6);
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid rgba(100, 255, 218, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.6s ease;
  position: relative;
  overflow: hidden;
}

.welcome-message::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle at 20% 20%, rgba(100, 255, 218, 0.05) 0%, transparent 25%),
    radial-gradient(circle at 80% 80%, rgba(64, 158, 255, 0.05) 0%, transparent 25%);
  z-index: -1;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.welcome-content h3 {
  margin-top: 0;
  color: #64ffda;
  font-size: 18px;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.welcome-hint {
  color: #81D4FA;
  font-size: 15px;
  line-height: 1.6;
}

.quick-actions {
  margin-top: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-actions .el-button {
  background: rgba(30, 38, 60, 0.6);
  border: 1px solid rgba(100, 255, 218, 0.3);
  color: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
}

.quick-actions .el-button:hover {
  background: rgba(30, 38, 60, 0.8);
  border-color: rgba(100, 255, 218, 0.6);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.ai-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #33a3ff 0%, #0063e5 100%);
  color: #fff;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 15px rgba(64, 158, 255, 0.5);
}

.ai-avatar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
}

.user-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 15px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #64ffda 0%, #00b8a9 100%);
  color: #1a2035;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 15px rgba(100, 255, 218, 0.5);
}

.user-avatar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
}

.ai-avatar i, .user-avatar i {
  font-size: 20px;
  position: relative;
  z-index: 1;
}

.message-item {
  display: flex;
  max-width: 85%;
  animation: fadeInMessage 0.4s ease;
}

@keyframes fadeInMessage {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.user-message {
  justify-content: flex-end;
  align-self: flex-end;
}

.ai-message {
  justify-content: flex-start;
  align-self: flex-start;
}

.message-content {
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  position: relative;
  z-index: 1;
}

.user-message .message-content {
  background: linear-gradient(135deg, rgba(100, 255, 218, 0.15) 0%, rgba(30, 38, 60, 0.5) 100%);
  color: rgba(255, 255, 255, 0.95);
  border-top-right-radius: 2px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(100, 255, 218, 0.1);
}

.ai-message .message-content {
  background: linear-gradient(135deg, rgba(30, 38, 60, 0.5) 0%, rgba(64, 158, 255, 0.15) 100%);
  color: rgba(255, 255, 255, 0.95);
  border-top-left-radius: 2px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(64, 158, 255, 0.1);
}

.thinking-dots {
  display: flex;
  padding: 10px 0;
}

.thinking-dots span {
  width: 8px;
  height: 8px;
  margin: 0 3px;
  background: #64ffda;
  border-radius: 50%;
  display: inline-block;
  animation: dot-flashing 1.2s infinite alternate;
  box-shadow: 0 0 8px rgba(100, 255, 218, 0.6);
}

.thinking-dots span:nth-child(2) {
  animation-delay: 0.2s;
  background: #4db6ff;
  box-shadow: 0 0 8px rgba(77, 182, 255, 0.6);
}

.thinking-dots span:nth-child(3) {
  animation-delay: 0.4s;
  background: #33a3ff;
  box-shadow: 0 0 8px rgba(51, 163, 255, 0.6);
}

@keyframes dot-flashing {
  0% {
    opacity: 0.2;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.product-card {
  display: flex;
  background: rgba(30, 38, 60, 0.7);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  border: 1px solid rgba(100, 255, 218, 0.1);
  position: relative;
  margin-bottom: 10px;
  padding: 15px;
}

.product-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle at 30% 30%, rgba(64, 158, 255, 0.03) 0%, transparent 40%),
    radial-gradient(circle at 70% 70%, rgba(100, 255, 218, 0.03) 0%, transparent 40%);
  z-index: 0;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  border-color: rgba(100, 255, 218, 0.3);
}

.product-details {
  flex: 1;
  position: relative;
  z-index: 1;
}

.product-details h4 {
  margin: 0 0 6px;
  font-size: 17px;
  color: rgba(255, 255, 255, 0.95);
  letter-spacing: 0.3px;
}

.product-meta {
  margin-bottom: 12px;
}

.product-stock {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.product-price {
  color: #64ffda;
  font-size: 18px;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
}

.orders-list {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 侧边面板 */
.side-panel {
  position: absolute;
  right: 20px;
  top: 100px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  z-index: 10;
}

.side-card {
  background: linear-gradient(135deg, rgba(30, 38, 60, 0.8) 0%, rgba(16, 20, 37, 0.8) 100%);
  border-radius: 12px;
  padding: 15px;
  width: 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(100, 255, 218, 0.1);
  transition: all 0.3s ease;
}

.side-card:hover {
  transform: translateY(-5px);
  background: linear-gradient(135deg, rgba(51, 163, 255, 0.2) 0%, rgba(100, 255, 218, 0.2) 100%);
  border-color: rgba(100, 255, 218, 0.3);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.side-icon {
  font-size: 32px;
  margin-bottom: 10px;
  filter: drop-shadow(0 0 10px rgba(100, 255, 218, 0.5));
}

.side-title {
  color: #64ffda;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}

.side-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  text-align: center;
  line-height: 1.4;
}

/* 增强响应式布局 */
@media (max-width: 1200px) {
  .side-panel {
    position: relative;
    right: auto;
    top: auto;
    flex-direction: row;
    justify-content: center;
    gap: 20px;
    margin: 20px auto;
    width: 90%;
    max-width: 900px;
  }
  
  .side-card {
    width: calc(33.33% - 14px);
  }
}

@media (max-width: 768px) {
  .chat-container {
    border-radius: 0;
    max-width: 100%;
  }
  
  .message-item {
    max-width: 95%;
  }
  
  .side-panel {
    flex-direction: column;
    align-items: center;
    width: 100%;
  }
  
  .side-card {
    width: 90%;
    max-width: 300px;
  }
  
  .chat-header {
    padding: 12px 16px;
  }
  
  .chat-header h2 {
    font-size: 18px;
  }
  
  .chat-body {
    padding: 16px;
    gap: 16px;
  }
  
  .chat-input {
    padding: 16px;
  }
  
  .welcome-message {
    flex-direction: column;
    padding: 20px 15px;
  }
  
  .ai-avatar, .user-avatar {
    margin: 0 auto 15px auto;
  }
  
  .quick-actions {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .product-card {
    flex-direction: column;
  }
}

/* 对于更小的屏幕 */
@media (max-width: 480px) {
  .chat-header h2 {
    font-size: 16px;
  }
  
  .chat-body {
    padding: 12px;
    gap: 12px;
  }
  
  .message-content {
    padding: 10px 14px;
    font-size: 13px;
  }
  
  .welcome-content h3 {
    font-size: 16px;
  }
  
  .welcome-hint {
    font-size: 13px;
  }
  
  .quick-actions .el-button {
    font-size: 12px;
    padding: 6px 10px;
  }
  
  .side-panel {
    margin: 15px auto;
  }
  
  .side-card {
    padding: 12px;
  }
  
  .side-title {
    font-size: 14px;
  }
  
  .side-desc {
    font-size: 11px;
  }
}
</style> 