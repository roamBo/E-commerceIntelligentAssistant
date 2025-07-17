<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import HomePage from './components/HomePage.vue'
import OrderManager from './components/OrderManager.vue'
import ShoppingGuide from './components/ShoppingGuide.vue'
import PaymentSystem from './components/PaymentSystem.vue'
import LoginPage from './components/LoginPage.vue'
import UserInfo from './components/UserInfo.vue'
import PaymentMonitor from './components/PaymentMonitor.vue'

const currentPage = ref('home')
const loginUser = ref(null)
const showPaymentNotification = ref(false)
const paymentChangeData = ref(null)
const paymentMonitorRef = ref(null)

// 初始化時檢查 localStorage
if (localStorage.getItem('loginUser')) {
  try {
    loginUser.value = JSON.parse(localStorage.getItem('loginUser'))
  } catch (e) {
    loginUser.value = null
  }
}

// 组件挂载后启动支付监控
onMounted(() => {
  console.log('App: 组件挂载完成，准备启动支付监控');
  
  // 确保支付监控组件已经挂载
  setTimeout(() => {
    if (paymentMonitorRef.value) {
      console.log('App: 启动支付监控');
      paymentMonitorRef.value.startMonitoring();
    } else {
      console.error('App: 支付监控组件未找到');
      
      // 尝试再次查找组件
      setTimeout(() => {
        if (paymentMonitorRef.value) {
          console.log('App: 第二次尝试启动支付监控');
          paymentMonitorRef.value.startMonitoring();
        } else {
          console.error('App: 支付监控组件仍未找到，无法启动监控');
        }
      }, 2000);
    }
  }, 1000);
});

const handleSidebarChange = (page) => {
  console.log('App: Changing page to', page)
  if (!page) {
    console.error('App: Invalid page name received:', page)
    return
  }
  // 确保页面名称有效
  const validPages = ['home', 'order', 'guide', 'payment', 'login']
  if (!validPages.includes(page)) {
    console.error('App: Unknown page name:', page)
    return
  }
  // 设置当前页面
  currentPage.value = page
  console.log('App: Current page set to', currentPage.value)
}
const handleSidebarLogin = () => {
  currentPage.value = 'login'
}
const handleLoginSuccess = () => {
  currentPage.value = 'home'
}

const onLogin = (user) => {
  loginUser.value = user
}
const onShowUser = (user) => {
  loginUser.value = user
}
const onLogout = () => {
  loginUser.value = null
  localStorage.removeItem('loginUser')
}
const handleGoLogin = () => {
  currentPage.value = 'login'
}

// 处理支付状态变化事件
const handlePaymentStatusChanged = (data) => {
  console.log('App: 收到支付状态变化事件', data);
  
  if (data.type === 'PAYMENT_SUCCESS') {
    // 保存支付数据
    paymentChangeData.value = data.payment;
    
    // 显示支付成功通知
    showPaymentNotification.value = true;
    
    // 3秒后自动切换到支付界面
    setTimeout(() => {
      // 隐藏通知
      showPaymentNotification.value = false;
      
      // 切换到支付界面
      currentPage.value = 'payment';
      
      console.log('App: 自动切换到支付界面');
    }, 3000);
  }
};

// 立即切换到支付界面
const goToPaymentNow = () => {
  showPaymentNotification.value = false;
  currentPage.value = 'payment';
};

// 关闭通知但不切换页面
const closeNotification = () => {
  showPaymentNotification.value = false;
};
</script>

<template>
  <div class="app-container">
    <Sidebar :currentPage="currentPage" @change="handleSidebarChange" @login="handleSidebarLogin" />
    <main class="main-content">
      <LoginPage v-if="currentPage === 'login' && !loginUser" @login="onLogin" @showUser="onShowUser" />
      <UserInfo v-if="currentPage === 'login' && loginUser" :user="loginUser" @logout="onLogout" />
      <HomePage v-if="currentPage === 'home'" @change="handleSidebarChange" />
      <OrderManager v-if="currentPage === 'order'" @goLogin="handleGoLogin" />
      <ShoppingGuide v-if="currentPage === 'guide'" @goLogin="handleGoLogin" />
      <PaymentSystem v-if="currentPage === 'payment'" @change="handleSidebarChange" />
      
      <!-- 支付监控组件 - 不可见 -->
      <PaymentMonitor ref="paymentMonitorRef" @payment-status-changed="handlePaymentStatusChanged" />
      
      <!-- 支付状态变化通知 -->
      <div v-if="showPaymentNotification" class="payment-notification">
        <div class="notification-content">
          <div class="notification-icon success">✓</div>
          <div class="notification-message">
            <h3>支付成功通知</h3>
            <p>您的订单已支付成功！</p>
            <p v-if="paymentChangeData" class="order-info">订单号: {{ paymentChangeData.orderId }}</p>
          </div>
          <div class="notification-actions">
            <button @click="goToPaymentNow" class="action-button primary">查看详情</button>
            <button @click="closeNotification" class="action-button">关闭</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.app-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.main-content {
  flex: 1;
  height: calc(100% - 64px);
  overflow: hidden;
  margin-top: 64px;
}

.main-content > * {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 支付通知样式 */
.payment-notification {
  position: fixed;
  bottom:20px;
  right:20px;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.notification-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: 400px;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.notification-icon.success {
  background: rgba(46, 204, 113, 0.15);
  border: 2px solid rgba(46, 204, 113, 0.3);
  color: #2ecc71;
}

.notification-message {
  flex: 1;
}

.notification-message h3 {
  font-size: 16px;
  margin-bottom: 4px;
  color: #333;
}

.notification-message p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.notification-message .order-info {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}

.notification-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-button {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #dcdfe6;
  background: #ffffff;
  color: #606266;
}

.action-button:hover {
  background: #f2f6fc;
}

.action-button.primary {
  background: #409eff;
  color: white;
  border: none;
}

.action-button.primary:hover {
  background: #66b1ff;
}

@media (max-width: 768px) {
  .main-content {
    width: 100%;
    overflow-y: auto;
  }
  
  .payment-notification {
    bottom:10px;
    right: 10px;
    left: 10px;
  }
  
  .notification-content {
    width: 100%;
    max-width: none;
  }
}

@media (max-width: 480px) {
  .main-content {
    height: calc(100% - 56px);
    margin-top: 56px;
  }
  
  .notification-content {
    flex-direction: column;
    text-align: center;
    padding: 12px;
  }
  
  .notification-actions {
    flex-direction: row;
    width: 100%;
    margin-top: 8px;
  }
  
  .action-button {
    flex: 1;
  }
}
</style>
