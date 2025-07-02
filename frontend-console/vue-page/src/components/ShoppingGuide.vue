<template>
  <div class="shopping-guide">
    <div class="chat-container">
      <div class="chat-header">
        <h2>个性化导购助手</h2>
        <el-button 
          v-if="chatMessages.length > 0" 
          type="text" 
          icon="el-icon-delete" 
          @click="clearChat"
          class="clear-btn"
        >清除对话</el-button>
      </div>
      <div class="chat-body" ref="chatBody">
        <!-- 欢迎消息 -->
        <div class="welcome-message" v-if="chatMessages.length === 0">
                     <div class="ai-avatar">
            <span class="emoji-avatar">🤖</span>
          </div>
          <div class="welcome-content">
            <h3>您好！我是您的个性化导购助手</h3>
            <p class="welcome-hint">您可以直接告诉我您需要什么商品，我将帮您完成推荐商品、购买下单、支付和物流跟踪的全流程服务。</p>
            <div class="quick-actions">
              <el-button size="small" @click="sendQuickMessage('如何使用这个导购助手？')">如何使用导购助手</el-button>
              <el-button size="small" @click="sendQuickMessage('你能提供哪些服务？')">查看服务范围</el-button>
              <el-button size="small" @click="sendQuickMessage('联系客服')">联系客服</el-button>
            </div>
          </div>
        </div>
        
        <!-- 聊天消息 -->
        <div 
          v-for="(message, index) in chatMessages" 
          :key="index" 
          :class="['message-item', message.isUser ? 'user-message' : 'ai-message']"
        >
          <div v-if="!message.isUser" class="ai-avatar">
            <span class="emoji-avatar">🤖</span>
          </div>
          <div class="message-content">
            <div v-if="message.thinking && !message.isUser" class="thinking-dots">
              <span></span><span></span><span></span>
            </div>
            <div v-else v-html="formatMessage(message.content)"></div>
            
            <!-- 推荐商品卡片列表 -->
            <div v-if="message.products && message.products.length > 0" class="product-recommendations">
              <div 
                v-for="product in message.products" 
                :key="product.id" 
                class="product-card"
              >
                <div class="product-image">
                  <img :src="product.image" :alt="product.name">
                </div>
                <div class="product-details">
                  <h4>{{ product.name }}</h4>
                  <p class="product-description">{{ product.description }}</p>
                  <div class="product-meta" v-if="product.rating">
                    <span class="product-rating">
                      <i class="el-icon-star-on"></i> {{ product.rating }}/5
                    </span>
                    <span class="product-stock">
                      库存: {{ product.stock }}
                    </span>
                  </div>
                  <div class="product-price-container">
                    <span class="product-price">¥{{ product.price.toFixed(2) }}</span>
                    <el-button size="mini" type="primary">查看详情</el-button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 订单详情 -->
            <div v-if="message.orderDetails" class="order-details">
              <h4 class="order-title">订单信息</h4>
              <div class="order-info">
                <div class="order-row">
                  <span class="order-label">商品:</span>
                  <span class="order-value">{{ message.orderDetails.productName }}</span>
                </div>
                <div class="order-row">
                  <span class="order-label">单价:</span>
                  <span class="order-value">¥{{ message.orderDetails.price.toFixed(2) }}</span>
                </div>
                <div class="order-row">
                  <span class="order-label">数量:</span>
                  <span class="order-value">{{ message.orderDetails.quantity }}</span>
                </div>
                <div class="order-row">
                  <span class="order-label">配送:</span>
                  <span class="order-value">{{ message.orderDetails.shipping }}</span>
                </div>
                <div class="order-row">
                  <span class="order-label">地址:</span>
                  <span class="order-value">{{ message.orderDetails.address }}</span>
                </div>
                <div class="order-row">
                  <span class="order-label">支付方式:</span>
                  <span class="order-value">{{ message.orderDetails.payment }}</span>
                </div>
                <div class="order-row total-row">
                  <span class="order-label">总计:</span>
                  <span class="order-value order-total">¥{{ message.orderDetails.total.toFixed(2) }}</span>
                </div>
                <div class="order-row">
                  <span class="order-label">预计送达:</span>
                  <span class="order-value">{{ message.orderDetails.estimatedDelivery }}</span>
                </div>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div v-if="message.actions && message.actions.length > 0" class="action-buttons">
              <el-button 
                v-for="action in message.actions" 
                :key="action.type"
                size="small"
                type="primary"
                plain
                @click="handleAction(action)"
              >{{ action.label }}</el-button>
            </div>
          </div>
          <div v-if="message.isUser" class="user-avatar">
            <span class="emoji-avatar">👤</span>
          </div>
        </div>
      </div>
      
      <div class="chat-input">
        <el-input
          v-model="userInput"
          placeholder="请描述您想找的商品或询问导购助手..."
          @keyup.enter="sendMessage"
          :disabled="isProcessing"
          clearable
        >
          <template #append>
            <el-button 
              :icon="isProcessing ? 'el-icon-loading' : 'el-icon-s-promotion'" 
              @click="sendMessage" 
              :disabled="!userInput.trim() || isProcessing"
            >发送</el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'

const chatBody = ref(null)
const userInput = ref('')
const isProcessing = ref(false)
const chatMessages = ref([])

// 发送快捷消息
const sendQuickMessage = (message) => {
  sendMessage(message);
}

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isProcessing.value) return
  
  // 添加用户消息
  const userMessage = userInput.value
  chatMessages.value.push({
    content: userMessage,
    isUser: true,
    timestamp: new Date().toISOString()
  })
  
  // 清空输入框
  userInput.value = ''
  
  // 添加AI思考状态
  isProcessing.value = true
  chatMessages.value.push({
    content: '',
    isUser: false,
    thinking: true,
    timestamp: new Date().toISOString()
  })
  
  // 滚动到底部
  await scrollToBottom()
  
  // 模拟调用大模型API
  await processUserMessage(userMessage)
}

// 处理用户消息，调用大模型API
const processUserMessage = async (message) => {
  try {
    // 模拟API响应延迟
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 移除思考状态的消息
    const thinkingIndex = chatMessages.value.findIndex(msg => msg.thinking)
    if (thinkingIndex !== -1) {
      chatMessages.value.splice(thinkingIndex, 1)
    }
    
    // TODO: 实际项目中，需要集成以下API:
    // 1. 大模型对话API - 处理用户消息并返回回复
    // 2. 商品推荐API - 根据对话内容获取商品推荐
    // 3. 订单API - 创建、查询和管理订单
    // 4. 支付API - 处理支付流程
    // 5. 物流API - 获取物流信息
    
    // 示例API调用结构
    // const response = await fetch('/api/assistant/chat', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ 
    //     message,
    //     sessionId: sessionId.value,
    //     userId: currentUser.id
    //   })
    // })
    // const data = await response.json()
    // 
    // if (data.success) {
    //   // 添加AI回复消息
    //   chatMessages.value.push({
    //     content: data.content,
    //     isUser: false,
    //     products: data.recommendedProducts || [],
    //     actions: data.actions || [],
    //     orderDetails: data.orderDetails || null,
    //     timestamp: new Date().toISOString()
    //   })
    // }
    
    // 临时响应 - 在实际项目中应替换为API响应
    chatMessages.value.push({
      content: '我们需要集成实际的API来处理您的请求。目前系统正在准备中，暂时无法处理具体业务。请稍后再试，或联系客服获取更多帮助。',
      isUser: false,
      timestamp: new Date().toISOString()
    })
    
    // 滚动到底部
    await scrollToBottom()
  } catch (error) {
    console.error('处理消息失败:', error)
    
    // 移除思考状态的消息
    const thinkingIndex = chatMessages.value.findIndex(msg => msg.thinking)
    if (thinkingIndex !== -1) {
      chatMessages.value.splice(thinkingIndex, 1)
    }
    
    // 添加错误消息
    chatMessages.value.push({
      content: '抱歉，我在处理您的请求时遇到了问题。请稍后再试。',
      isUser: false,
      timestamp: new Date().toISOString()
    })
  } finally {
    isProcessing.value = false
  }
}

// 清除聊天记录
const clearChat = () => {
  chatMessages.value = []
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
watch(chatMessages, () => {
  scrollToBottom()
}, { deep: true })

// 组件挂载时滚动到底部
onMounted(() => {
  scrollToBottom()
})

// 处理操作按钮点击
const handleAction = async (action) => {
  console.log('Action clicked:', action);
  
  // TODO: 实际项目中应该根据action类型调用对应的API
  // 例如：
  // if (action.type === 'purchase') {
  //   try {
  //     const response = await fetch('/api/orders/create', {
  //       method: 'POST',
  //       headers: { 'Content-Type': 'application/json' },
  //       body: JSON.stringify({ productId: action.productId, quantity: 1 })
  //     });
  //     const result = await response.json();
  //     if (result.success) {
  //       // 处理成功响应
  //     } else {
  //       // 处理错误
  //     }
  //   } catch (error) {
  //     console.error('API调用失败:', error);
  //   }
  // }
  
  // 临时实现：生成对应的用户消息
  const actionMessages = {
    'compare': '我想比较这些商品',
    'filter': '我想筛选商品',
    'purchase': '我想购买这个商品',
    'confirm_order': '确认下单',
    'modify_address': '修改地址',
    'change_payment': '更改支付方式',
    'pay_now': '支付订单',
    'cancel_order': '取消订单',
    'track_order': '追踪订单',
    'continue_shopping': '继续购物',
    'view_details': '查看详情',
    'contact_support': '联系客服'
  };
  
  const message = actionMessages[action.type] || '我想了解更多';
  sendMessage(message);
};
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

.product-recommendations {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
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
  transform: translateY(-5px) scale(1.01);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  border-color: rgba(100, 255, 218, 0.3);
}

.product-image {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.product-image::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(30, 38, 60, 0.3) 0%, transparent 100%);
  z-index: 1;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-details {
  flex: 1;
  padding: 15px;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.product-details h4 {
  margin: 0 0 6px;
  font-size: 17px;
  color: rgba(255, 255, 255, 0.95);
  letter-spacing: 0.3px;
}

.product-description {
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  margin: 0 0 12px;
  flex: 1;
  line-height: 1.5;
}

.product-meta {
  margin-bottom: 12px;
}

.product-rating {
  color: #64ffda;
  font-size: 14px;
  margin-right: 10px;
}

.product-stock {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.product-price-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-price {
  color: #64ffda;
  font-size: 18px;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
}

.product-price-container .el-button {
  background: linear-gradient(135deg, #33a3ff 0%, #0063e5 100%);
  border: none;
  transition: all 0.3s ease;
}

.product-price-container .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .product-card {
    flex-direction: column;
  }
  
  .product-image {
    width: 100%;
    height: 180px;
  }
  
  .message-item {
    max-width: 95%;
  }
}

.order-details {
  margin-top: 20px;
  padding: 15px;
  background: rgba(30, 38, 60, 0.7);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(100, 255, 218, 0.1);
}

.order-title {
  margin: 0 0 12px;
  font-size: 18px;
  color: #64ffda;
  letter-spacing: 0.3px;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.order-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.order-value {
  color: rgba(255, 255, 255, 0.95);
  font-size: 14px;
}

.order-total {
  font-weight: bold;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.action-buttons .el-button {
  background: linear-gradient(135deg, #33a3ff 0%, #0063e5 100%);
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.action-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}
</style> 