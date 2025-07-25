<template>
  <div class="shopping-guide">
    <canvas ref="bgCanvas" class="bg-particles"></canvas>
    <div class="guide-content">
      <!-- 登录提醒遮罩 -->
      <div v-if="!isLoggedIn" class="login-overlay">
        <div class="login-reminder">
          <div class="reminder-icon">🔒</div>
          <h3>请先登录</h3>
          <p>您需要登录后才能使用个性化导购助手</p>
          <p class="login-hint">登录后即可享受个性化商品推荐、订单管理和支付服务</p>
          <el-button type="primary" @click="goToLogin">立即登录</el-button>
        </div>
      </div>

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
                <el-button size="small" @click="quickSend('如何使用这个导购助手？')" :disabled="!isLoggedIn">如何使用导购助手</el-button>
                <el-button size="small" @click="quickSend('你能提供哪些服务？')" :disabled="!isLoggedIn">查看服务范围</el-button>
                <el-button size="small" @click="quickSend('联系客服')" :disabled="!isLoggedIn">联系客服</el-button>
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
              ref="inputField"
              v-model="input"
              placeholder="请描述您想找的商品或询问导购助手..."
              @keyup.enter="sendMsg"
              :disabled="isProcessing || !isLoggedIn"
              clearable
          >
            <template #append>
              <el-button
                  :icon="isProcessing ? 'el-icon-loading' : 'el-icon-s-promotion'"
                  @click="sendMsg"
                  :disabled="!input.trim() || isProcessing || !isLoggedIn"
              >发送</el-button>
            </template>
          </el-input>
        </div>
      </div>

      <!-- 侧边快捷功能 -->
      <div class="side-panel">
        <div class="side-card" @click="isLoggedIn && quickSend('帮我查询我的所有订单')" :class="{'disabled': !isLoggedIn}">
          <div class="side-icon">🛒</div>
          <div class="side-title">订单查询</div>
          <div class="side-desc">一键查询我的所有订单</div>
        </div>
        <div class="side-card" @click="isLoggedIn && quickSend('帮我查询我的所有订单的应付金额')" :class="{'disabled': !isLoggedIn}">
          <div class="side-icon">💰</div>
          <div class="side-title">支付查询</div>
          <div class="side-desc">快速查看应付金额</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import axios from 'axios'
// 导入通信服务
import commService from '../services/commService'
import { orderApi } from '../services/api'

const chatBody = ref(null)
const inputField = ref(null)
const messages = ref([
  { role: 'bot', text: '您好，有什么可以帮您？' }
])
const input = ref('')
const isProcessing = ref(false)
const bgCanvas = ref(null)
let animationId = null
const PARTICLE_NUM = 15
const PARTICLE_COLOR = 'rgba(0,0,0,0.5)'
const PARTICLE_RADIUS = [15, 25]
const PARTICLE_SPEED = [0.1, 0.3]
let particles = []
const EMOJIS = ['🛒', '🎁', '💰', '🏷️', '📱', '💻', '👕', '👟', '⭐', '💳', '📦']

// 会话ID
const sessionId = ref(commService.generateSessionId())

// 检查用户是否登录
const isLoggedIn = computed(() => {
  try {
    return !!localStorage.getItem('loginUser')
  } catch (e) {
    return false
  }
})

// 定义emit以便与父组件通信
const emit = defineEmits(['goLogin'])

// 跳转到登录页面
function goToLogin() {
  emit('goLogin')
}

async function sendMsg() {
  const text = input.value.trim()
  if (!text || isProcessing.value || !isLoggedIn.value) return

  // 添加用户消息到聊天窗口
  messages.value.push({ role: 'user', text })
  input.value = ''
  scrollToBottom()
  
  // 设置处理中状态
  isProcessing.value = true
  
  try {
      // 添加思考状态的消息
      const thinkingIndex = messages.value.length
      messages.value.push({ role: 'bot', thinking: true, text: '' })
      scrollToBottom()
      
      try {
      // 调用通信服务的chatWithAgent方法，发送到comm_agent
      const response = await commService.chatWithAgent(text, sessionId.value)
        
        // 替换思考状态为实际回复
        messages.value[thinkingIndex] = {
          role: 'bot',
        text: response.response || response.message || response.text || JSON.stringify(response),
          type: 'text'
        }
      } catch (error) {
        console.error('调用通信服务失败:', error)
        // 处理错误消息
        let errorMessage = '很抱歉，商品推荐服务暂时不可用。请稍后再试。'
        
        // 如果是我们定义的格式化错误对象
        if (error.message) {
          errorMessage = error.message
        }
        
        // 替换思考状态为错误消息
        messages.value[thinkingIndex] = {
          role: 'bot',
          text: errorMessage,
          error: true
      }
    }
  } finally {
    isProcessing.value = false
    scrollToBottom()
    focusInput()
  }
}

function quickSend(text) {
  if (isProcessing.value || !isLoggedIn.value) return
  input.value = text
  sendMsg()
}

async function fetchOrders() {
  try {
    // 直接发送消息给agent
    await sendMsg('帮我查询我的所有订单')
  } finally {
    isProcessing.value = false
    scrollToBottom()
  }
}

async function fetchTotal() {
  try {
    // 直接发送消息给agent
    await sendMsg('帮我查询我的所有订单的应付金额')
  } finally {
    isProcessing.value = false
    scrollToBottom()
  }
}

// 自动聚焦输入框
function focusInput() {
  nextTick(() => {
    if (inputField.value) {
      inputField.value.focus()
    }
  })
}

// 清除聊天记录
const clearChat = () => {
  messages.value = [
    { role: 'bot', text: '您好，有什么可以帮您？' }
  ]
  // 重新生成会话ID
  sessionId.value = commService.generateSessionId()
  focusInput()
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

// 组件挂载时滚动到底部和聚焦输入框
onMounted(() => {
  resizeCanvas()
  createParticles()
  animateParticles()
  window.addEventListener('resize', () => {
    resizeCanvas()
    createParticles()
  })
  scrollToBottom()
  focusInput()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animationId)
})

function randomBetween(a, b) {
  return a + Math.random() * (b - a)
}

function resizeCanvas() {
  if (!bgCanvas.value) return
  bgCanvas.value.width = window.innerWidth
  bgCanvas.value.height = window.innerHeight
}

function createParticles() {
  const w = window.innerWidth
  const h = window.innerHeight
  particles = Array.from({ length: PARTICLE_NUM }, () => ({
    x: Math.random() * w,
    y: Math.random() * h,
    r: randomBetween(PARTICLE_RADIUS[0], PARTICLE_RADIUS[1]),
    dx: randomBetween(-PARTICLE_SPEED[1], PARTICLE_SPEED[1]),
    dy: randomBetween(-PARTICLE_SPEED[1], PARTICLE_SPEED[1]),
    emoji: EMOJIS[Math.floor(Math.random() * EMOJIS.length)],
    opacity: randomBetween(0.1, 0.3),
    rotation: Math.random() * 360
  }))
}

function animateParticles() {
  const ctx = bgCanvas.value.getContext('2d')
  const w = bgCanvas.value.width
  const h = bgCanvas.value.height
  ctx.clearRect(0, 0, w, h)
  
  for (const p of particles) {
    p.x += p.dx
    p.y += p.dy
    p.rotation += 0.2
    // 边界反弹
    if (p.x < -p.r) p.x = w + p.r
    if (p.x > w + p.r) p.x = -p.r
    if (p.y < -p.r) p.y = h + p.r
    if (p.y > h + p.r) p.y = -p.r
    
    ctx.save()
    ctx.translate(p.x, p.y)
    ctx.rotate(p.rotation * Math.PI / 180)
    ctx.font = `${p.r * 2}px Arial`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.globalAlpha = p.opacity
    ctx.fillText(p.emoji, 0, 0)
    ctx.restore()
  }
  
  animationId = requestAnimationFrame(animateParticles)
}
</script>

<style scoped>
html, body, #app {
  margin: 0 !important;
  padding: 0 !important;
}

.shopping-guide {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  min-height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #f5f7fa;
  padding-top: 0 !important;
  margin-top: 0 !important;
}

.guide-content {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  padding-top: 0 !important;
  margin-top: 0 !important;
}

.chat-container {
  max-width: 900px;
  width: 900px;
  height: 600px;
  min-height: 600px;
  max-height: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  position: relative;
  z-index: 1;
  border: 1px solid #ebeef5;
  overflow: hidden;
  top: 100px;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  position: relative;
}

.chat-header::after {
  content: none;
}

@keyframes scanLine {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.chat-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  letter-spacing: 0;
  text-shadow: none;
  position: relative;
  display: inline-block;
}

.chat-header h2::before {
  content: '';
  display: none;
}

@keyframes pulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.clear-btn {
  color: #409eff;
}

.clear-btn:hover {
  color: #66b1ff;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  scrollbar-width: thin;
  scrollbar-color: rgba(144, 147, 153, 0.3) rgba(245, 247, 250, 0.2);
  min-height: 0;
}

.chat-body::-webkit-scrollbar {
  width: 6px;
}

.chat-body::-webkit-scrollbar-track {
  background: rgba(245, 247, 250, 0.2);
}

.chat-body::-webkit-scrollbar-thumb {
  background-color: rgba(144, 147, 153, 0.3);
  border-radius: 3px;
  border: 1px solid rgba(245, 247, 250, 0.2);
}

.chat-input {
  padding: 20px 24px;
  border-top: 1px solid #ebeef5;
  background: #ffffff;
  position: relative;
}

.chat-input::before {
  content: none;
}

.chat-input .el-input__inner {
  background: #ffffff;
  border: 1px solid #dcdfe6;
  color: #606266;
  transition: all 0.3s ease;
}

.chat-input .el-input__inner:focus {
  border-color: #409eff;
  box-shadow: 0 0 5px rgba(64, 158, 255, 0.2);
}

.chat-input .el-input-group__append button {
  background: #409eff;
  border: none;
  color: white;
  transition: all 0.3s ease;
  padding-right: 30px;
  padding-left: 10px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.chat-input .el-input-group__append button .el-icon-s-promotion,
.chat-input .el-input-group__append button .el-icon-loading {
  margin-right: 8px;
}

.chat-input .el-input-group__append button:hover:not(:disabled) {
  background: #66b1ff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.welcome-message {
  display: flex;
  padding: 25px;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 12px;
  border: 1px solid #ebeef5;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  animation: fadeIn 0.6s ease;
  position: relative;
  overflow: hidden;
}

.welcome-message::before {
  content: none;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.welcome-content h3 {
  margin-top: 0;
  color: #303133;
  font-size: 18px;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.welcome-hint {
  color: #606266;
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
  background: #ffffff;
  border: 1px solid #dcdfe6;
  color: #606266;
  transition: all 0.3s ease;
}

.quick-actions .el-button:hover {
  background: #f5f7fa;
  border-color: #c6e2ff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
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
  background: #409eff;
  color: #fff;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.3);
}

.ai-avatar::before {
  content: none;
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
  background: #67c23a;
  color: #fff;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 8px rgba(103, 194, 58, 0.3);
}

.user-avatar::before {
  content: none;
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
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  position: relative;
  z-index: 1;
}

.user-message .message-content {
  background: #f0f9eb;
  color: #606266;
  border-top-right-radius: 2px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e1f3d8;
}

.ai-message .message-content {
  background: #ecf5ff;
  color: #606266;
  border-top-left-radius: 2px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #d9ecff;
}

.thinking-dots {
  display: flex;
  padding: 10px 0;
}

.thinking-dots span {
  width: 8px;
  height: 8px;
  margin: 0 3px;
  background: #409eff;
  border-radius: 50%;
  display: inline-block;
  animation: dot-flashing 1.2s infinite alternate;
  box-shadow: 0 0 5px rgba(64, 158, 255, 0.4);
}

.thinking-dots span:nth-child(2) {
  animation-delay: 0.2s;
  background: #66b1ff;
  box-shadow: 0 0 5px rgba(102, 177, 255, 0.4);
}

.thinking-dots span:nth-child(3) {
  animation-delay: 0.4s;
  background: #a0cfff;
  box-shadow: 0 0 5px rgba(160, 207, 255, 0.4);
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
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
  border: 1px solid #ebeef5;
  position: relative;
  margin-bottom: 10px;
  padding: 15px;
}

.product-card::before {
  content: none;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  border-color: #dcdfe6;
}

.product-details {
  flex: 1;
  position: relative;
  z-index: 1;
}

.product-details h4 {
  margin: 0 0 6px;
  font-size: 17px;
  color: #303133;
  letter-spacing: 0.3px;
}

.product-meta {
  margin-bottom: 12px;
}

.product-stock {
  color: #909399;
  font-size: 14px;
}

.product-price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
  text-shadow: none;
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
  top: 150px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  z-index: 10;
}

.side-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 15px;
  width: 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #ebeef5;
  transition: all 0.3s ease;
}

.side-card:hover {
  transform: translateY(-5px);
  background: #f5f7fa;
  border-color: #c6e2ff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.side-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
  filter: grayscale(0.5);
  border-color: #dcdfe6;
  box-shadow: none;
}

.side-icon {
  font-size: 32px;
  margin-bottom: 10px;
  filter: none;
}

.side-title {
  color: #303133;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}

.side-desc {
  color: #909399;
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
  
  /* 小屏幕上调整发送按钮的内边距 */
  .chat-input .el-input-group__append button {
    padding-right: 10px;
    padding-left: 8px;
  }
  
  .chat-input .el-input-group__append button .el-icon-s-promotion,
  .chat-input .el-input-group__append button .el-icon-loading {
    margin-right: 5px;
  }
}

.bg-particles {
  position: fixed;
  left: 0;
  top: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: none;
}

/* 登录提醒遮罩 */
.login-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.login-reminder {
  background: #ffffff;
  padding: 30px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 90%;
}

.reminder-icon {
  font-size: 60px;
  color: #409eff;
  margin-bottom: 20px;
}

.login-reminder h3 {
  color: #303133;
  font-size: 22px;
  margin-bottom: 10px;
}

.login-reminder p {
  color: #606266;
  font-size: 16px;
  margin-bottom: 25px;
  line-height: 1.6;
}

.login-hint {
  color: #909399 !important;
  font-size: 14px !important;
  margin-bottom: 25px;
  background-color: #f0f9eb;
  border-radius: 4px;
  padding: 10px;
  border-left: 3px solid #67c23a;
}

.login-reminder .el-button {
  background: #409eff;
  border: none;
  color: white;
  padding: 12px 25px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.login-reminder .el-button:hover {
  background: #66b1ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}
</style> 