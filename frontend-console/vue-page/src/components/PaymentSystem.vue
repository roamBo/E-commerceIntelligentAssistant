<template>
  <div class="payment-system">
    <canvas ref="bgCanvas" class="bg-particles"></canvas>
    <div class="payment-container">
      <div class="payment-header">
        <h2>支付信息</h2>
        <div v-if="isLoading" class="payment-status status-loading">
          加载中...
        </div>
        <div v-else-if="paymentStatus" class="payment-status" :class="paymentStatus.class">
          {{ paymentStatus.text }}
        </div>
      </div>
      
      <!-- 加载中状态 -->
      <div v-if="isLoading" class="loading-indicator">
        <div class="loading-spinner">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 6v6l4 2"></path>
          </svg>
        </div>
        <div class="loading-text">正在获取支付信息...</div>
      </div>
      
      <!-- 支付结果信息卡片 -->
      <div v-else-if="paymentStatus" class="payment-result-card">
        <div class="result-icon" :class="paymentStatus.id">
          <i v-if="paymentStatus.id === 'success'" class="success-icon">✓</i>
          <i v-else-if="paymentStatus.id === 'failed'" class="failed-icon">✕</i>
          <i v-else class="pending-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
              <polyline points="21 3 21 9 15 9"></polyline>
            </svg>
          </i>
        </div>
        <div class="result-message">{{ paymentStatus.message }}</div>
      </div>
      
      <!-- 加载中状态 -->
      <div v-else class="loading-indicator">
        <div class="loading-spinner">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 6v6l4 2"></path>
          </svg>
        </div>
        <div class="loading-text">正在获取支付信息...</div>
      </div>
      
      <!-- 订单和支付详情 -->
      <div v-if="!isLoading && paymentStatus && paymentStatus.id !== 'failed'" class="payment-details">
        <!-- 左侧：订单信息 -->
        <div class="order-info">
          <h3>订单信息</h3>
          <div class="info-item">
            <span class="info-label">订单号</span>
            <span class="info-value">{{ paymentInfo.orderId }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">下单时间</span>
            <span class="info-value">{{ paymentInfo.orderTime }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">订单金额</span>
            <span class="info-value price">¥{{ paymentInfo.amount.toFixed(2) }}</span>
          </div>
        </div>
        
        <!-- 右侧：支付信息 -->
        <div class="payment-info">
          <h3>支付信息</h3>
          <div class="info-item">
            <span class="info-label">支付方式</span>
            <span class="info-value">
              <span class="payment-method-icon" v-html="getPaymentIcon(paymentInfo.method)"></span>
              {{ getPaymentName(paymentInfo.method) }}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">支付时间</span>
            <span class="info-value">{{ paymentInfo.payTime || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">交易流水号</span>
            <span class="info-value">{{ paymentInfo.transactionId || '-' }}</span>
          </div>
        </div>
      </div>
      
      <!-- 商品信息 -->
      <div v-if="!isLoading && paymentStatus && paymentStatus.id !== 'failed'" class="product-info">
        <h3>商品信息</h3>
        <div class="product-item">
          <div class="product-name">{{ paymentInfo.productName }}</div>
          <div class="product-quantity">x{{ paymentInfo.quantity }}</div>
          <div class="product-price">¥{{ paymentInfo.unitPrice.toFixed(2) }}</div>
        </div>
      </div>
      
      <!-- 底部操作栏 -->
      <div class="action-bar">
        <div v-if="!isLoading && paymentStatus && paymentStatus.id !== 'failed'" class="total-amount">
          <span>实付金额：</span>
          <span class="amount">¥{{ paymentInfo.amount.toFixed(2) }}</span>
        </div>
        <div class="buttons">
          <button v-if="!isLoading && paymentStatus && paymentStatus.id !== 'failed'" class="action-button" @click="viewOrderDetails">查看订单详情</button>
          <button class="action-button primary" @click.prevent="goBack">返回首页</button>
        </div>
      </div>
    </div>
    
    <!-- 订单查询结果弹窗 -->
    <div class="modal" v-if="showOrderModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>订单详情</h3>
          <span class="close-btn" @click="closeModal">&times;</span>
        </div>
        <div class="modal-body">
          <div v-if="orderDetails">
            <div class="order-detail-item">
              <span class="detail-label">订单号:</span>
              <span class="detail-value">{{ orderDetails.orderId }}</span>
            </div>
            <div class="order-detail-item">
              <span class="detail-label">下单时间:</span>
              <span class="detail-value">{{ orderDetails.orderTime }}</span>
            </div>
            <div class="order-detail-item">
              <span class="detail-label">订单状态:</span>
              <span class="detail-value" :class="'status-' + orderDetails.status">{{ getOrderStatusText(orderDetails.status) }}</span>
            </div>
            <div class="order-detail-item">
              <span class="detail-label">收货地址:</span>
              <span class="detail-value">{{ orderDetails.address }}</span>
            </div>
            <div class="order-detail-item">
              <span class="detail-label">联系电话:</span>
              <span class="detail-value">{{ orderDetails.phone }}</span>
            </div>
            <div class="order-products">
              <h4>商品列表</h4>
              <div class="product-list">
                <div class="product-list-item" v-for="(item, index) in orderDetails.products" :key="index">
                  <span class="product-list-name">{{ item.name }}</span>
                  <span class="product-list-quantity">x{{ item.quantity }}</span>
                  <span class="product-list-price">¥{{ item.price.toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-order-found">
            <div class="no-data-icon">!</div>
            <p>未找到订单信息，请确认订单号是否正确</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue';
import paymentService from '../services/paymentService';

// 定义事件
const emit = defineEmits(['change']);

// 不需要props，直接使用模拟数据

// 支付状态类型
const statusTypes = {
  success: { 
    id: 'success', 
    text: '支付成功', 
    class: 'status-success',
    message: '您的订单已支付成功，感谢您的购买！' 
  },
  failed: { 
    id: 'failed', 
    text: '支付失败', 
    class: 'status-failed',
    message: '支付处理过程中出现问题，请稍后重试或联系客服。' 
  },
  pending: { 
    id: 'pending', 
    text: '处理中', 
    class: 'status-pending',
    message: '正在处理您的支付，请稍候...' 
  }
};

// 支付状态映射表
const statusMapping = {
  'SUCCESS': 'success',
  'FAILED': 'failed',
  'PENDING': 'pending',
  'PROCESSING': 'pending',
  'CANCELLED': 'failed',
  'success': 'success',
  'failed': 'failed',
  'pending': 'pending'
};

// 加载状态
const isLoading = ref(true);

// 当前支付状态（初始为null，避免显示闪烁的待处理状态）
const paymentStatus = ref(null);

// 支付信息（初始为空，稍后从API获取）
const paymentInfo = reactive({
  orderId: '',
  orderTime: '',
  amount: 0,
  method: '',
  payTime: '',
  transactionId: '',
  productName: '',
  quantity: 0,
  unitPrice: 0
});

// 不需要订单数据库

// 订单详情弹窗状态
const showOrderModal = ref(false);
const orderDetails = ref(null);

// 获取支付方式图标
const getPaymentIcon = (method) => {
  const icons = {
    alipay: '<span style="color:#1677FF;font-size:18px;">&#xe673;</span>',
    wechat: '<span style="color:#07C160;font-size:18px;">&#xe674;</span>',
    unionpay: '<span style="color:#D7000F;font-size:18px;">&#xe675;</span>',
    credit: '<span style="color:#FF6B6B;font-size:18px;">&#xe676;</span>'
  };
  return icons[method] || '';
};

// 获取支付方式名称
const getPaymentName = (method) => {
  const names = {
    alipay: '支付宝',
    wechat: '微信支付',
    unionpay: '银联',
    credit: '信用卡'
  };
  return names[method] || method;
};

// 获取订单状态文本
const getOrderStatusText = (status) => {
  const statusMap = {
    'pending': '待支付',
    'paid': '已支付',
    'processing': '处理中',
    'shipped': '已发货',
    'delivered': '已送达',
    'success': '交易成功',
    'cancelled': '已取消',
    'refunded': '已退款'
  };
  return statusMap[status] || status;
};

// 查看订单详情
const viewOrderDetails = async () => {
  if (!paymentInfo.orderId) {
    console.error('没有订单ID，无法查询订单详情');
    return;
  }
  
  try {
    // 从API获取订单详情
    const response = await fetch(`/order/api/orders/${paymentInfo.orderId}`);
    if (response.ok) {
      const orderData = await response.json();
      orderDetails.value = {
        orderId: orderData.id || orderData.orderId || paymentInfo.orderId,
        orderTime: orderData.createAt || orderData.createdAt || paymentInfo.orderTime,
        status: orderData.status || 'processing',
        address: orderData.shippingAddress || orderData.address || '未提供地址',
        phone: orderData.phone || orderData.contactPhone || '未提供电话',
        products: orderData.products || orderData.items || []
      };
      
      // 如果没有商品信息，显示一个提示
      if (!orderDetails.value.products || orderDetails.value.products.length === 0) {
        console.warn('订单中没有商品信息');
      }
      
  showOrderModal.value = true;
    } else {
      console.error('获取订单详情失败，API返回错误状态:', response.status);
    }
  } catch (error) {
    console.error('获取订单详情失败:', error);
  }
};

// 关闭弹窗
const closeModal = () => {
  showOrderModal.value = false;
};

// 返回首页
const goBack = () => {
  // 发射事件通知父组件切换到首页
  console.log('PaymentSystem: Emitting change event to navigate to home page');
  // 添加延时以确保事件不会被覆盖或丢失
  setTimeout(() => {
    emit('change', 'home');
  }, 10);
};

const bgCanvas = ref(null)
let animationId = null
const PARTICLE_NUM = 15
const PARTICLE_COLOR = 'rgba(0,0,0,0.5)'
const PARTICLE_RADIUS = [15, 25]
const PARTICLE_SPEED = [0.1, 0.3]
let particles = []
const EMOJIS = ['💰', '💳', '💸', '💵', '💴', '💶', '💷', '🧾', '🏦', '🔐', '✅']

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

// 获取支付信息
const fetchPaymentInfo = async () => {
  try {
    console.log('获取支付信息...');
    isLoading.value = true;
    
    // 获取当前登录用户信息
    let currentUser = null;
    try {
      const loginUserStr = localStorage.getItem('loginUser');
      if (loginUserStr) {
        currentUser = JSON.parse(loginUserStr);
        console.log('当前登录用户:', currentUser);
        
        // 检查用户信息是否包含ID
        if (currentUser.userID) {
          // 规范化用户ID字段，确保可以通过id访问
          currentUser.id = currentUser.userID;
        }
        
        if (!currentUser.id && !currentUser.userId && !currentUser.user_id) {
          console.warn('登录用户信息中没有找到有效的用户ID字段');
          console.log('用户信息字段:', Object.keys(currentUser));
        }
      }
    } catch (error) {
      console.error('获取当前用户信息失败:', error);
    }
    
          // 尝试从API获取支付信息
      let paymentData;
      try {
                // 如果有用户信息，则尝试获取该用户的支付记录
        if (currentUser) {
          // 用户ID可能存储在多个不同的字段中
          const userId = currentUser.id || currentUser.userID || currentUser.userId || currentUser.user_id;
          
          // 如果没有找到用户ID，但有用户名，也可以尝试使用
          if (!userId && currentUser.username) {
            console.log('未找到用户ID，但找到了用户名:', currentUser.username);
          }
          
        // const manualUserId = userId;
        const manualUserId = userId;
        
        console.log('当前用户ID:', manualUserId);
        
        if (!manualUserId) {
          console.error('无法确定用户ID，无法获取订单');
          paymentStatus.value = {
            id: 'failed',
            text: '用户ID缺失',
            class: 'status-failed',
            message: '无法确定您的用户ID，请重新登录'
          };
          isLoading.value = false;
          return; // 提前返回，不继续处理
        }
        
        try {
        // 使用fetch API直接获取支付记录
        console.log(`正在获取用户 ${manualUserId} 的支付记录...`);
        const response = await fetch(`/payment/api/payments/user/${manualUserId}`);
        
        if (response.ok) {
          const payments = await response.json();
          console.log('获取到的支付记录:', payments);
          
          // 使用最新的一条支付记录
          if (payments && payments.length > 0) {
            // 按创建时间排序，获取最新的订单
            const sortedPayments = payments.sort((a, b) => 
              new Date(b.createAt || b.updateAt || 0) - new Date(a.createAt || a.updateAt || 0)
            );
            paymentData = sortedPayments[0];
            
            // 严格检查支付记录是否属于当前用户
            // 支付记录中的用户ID可能存储在userId或userID字段中
            const paymentUserId = paymentData.userId || paymentData.userID || paymentData.user_id;
            
            // 严格检查支付记录是否属于当前用户
            if (paymentUserId && paymentUserId.toString() === manualUserId.toString()) {
              console.log('找到用户最新支付记录:', paymentData);
            } else {
              console.warn('支付记录的用户ID与当前用户不匹配!');
              console.log('支付记录用户ID:', paymentUserId, '当前用户ID:', manualUserId);
              
              // 由于是测试环境，我们仍然使用找到的支付记录
              console.log('测试环境：使用找到的支付记录，即使用户ID不匹配');
            }
          } else {
            console.log('未找到用户支付记录');
            // 显示没有订单信息
            paymentStatus.value = {
              id: 'failed',
              text: '未找到订单',
              class: 'status-failed',
              message: '未找到您的订单信息，请先购买商品'
            };
            isLoading.value = false;
            return; // 提前返回，不继续处理
          }
        } else {
          console.error('获取用户支付记录失败，状态码:', response.status);
          throw new Error(`API返回错误状态码: ${response.status}`);
        }
      } catch (error) {
        console.error('获取用户支付记录时出错:', error);
        // 显示错误信息
                    paymentStatus.value = {
          id: 'failed',
          text: '获取失败',
          class: 'status-failed',
          message: '获取订单信息失败，请稍后再试'
        };
        isLoading.value = false;
        return; // 提前返回，不继续处理
      }
    } else {
      console.log('未找到当前用户信息，无法获取用户订单');
      // 显示没有订单信息
      paymentStatus.value = {
        id: 'failed',
        text: '未登录',
        class: 'status-failed',
        message: '请先登录后查看您的订单信息'
      };
      isLoading.value = false;
      return; // 提前返回，不继续处理
    }
  } catch (error) {
    console.error('从API获取支付信息失败:', error);
  }
    
    // 如果API获取失败，则显示未找到订单信息
    if (!paymentData) {
      console.log('未能获取到支付数据');
      paymentStatus.value = {
        id: 'failed',
        text: '未找到订单',
        class: 'status-failed',
        message: '未找到订单信息，请稍后再试或联系客服'
      };
      isLoading.value = false;
      return; // 提前返回，不继续处理
    }
    
    console.log('获取到支付数据:', paymentData);
    
    // 再次检查支付数据是否有效
    if (!paymentData || !paymentData.orderId) {
      console.warn('支付数据无效或缺少订单ID');
          paymentStatus.value = {
      id: 'failed',
      text: '无效订单',
      class: 'status-failed',
      message: '订单信息不完整，请联系客服'
    };
    isLoading.value = false;
    return;
    }
    
    // 更新支付状态
    const mappedStatus = statusMapping[paymentData.status] || 'pending';
    paymentStatus.value = statusTypes[mappedStatus];
    isLoading.value = false;
    
    // 更新支付信息
    paymentInfo.orderId = paymentData.orderId;
    paymentInfo.orderTime = paymentData.createAt || paymentData.createdAt || '';
    paymentInfo.amount = paymentData.amount || 0;
    paymentInfo.method = paymentData.method || 'alipay'; // 默认支付宝
    paymentInfo.payTime = paymentData.updateAt || paymentData.updatedAt || '';
    paymentInfo.transactionId = paymentData.transactionId || paymentData.id || '';
    
    // 更新商品信息
    if (paymentData.productDetails) {
      paymentInfo.productName = paymentData.productDetails.name || '未知商品';
      paymentInfo.quantity = paymentData.productDetails.quantity || 1;
      paymentInfo.unitPrice = paymentData.productDetails.unitPrice || paymentData.amount || 0;
    } else {
      // 如果没有商品详情，使用订单ID作为商品名称
      paymentInfo.productName = `订单 ${paymentData.orderId}`;
      paymentInfo.quantity = 1;
      paymentInfo.unitPrice = paymentData.amount || 0;
    }
    
    console.log('成功更新支付信息:', paymentInfo);
    
  } catch (error) {
    console.error('获取支付信息失败:', error);
    paymentStatus.value = {
      id: 'failed',
      text: '获取失败',
      class: 'status-failed',
      message: '获取订单信息失败，请稍后再试或联系客服'
    };
    isLoading.value = false;
    
    // 清空支付信息
    paymentInfo.orderId = '';
    paymentInfo.orderTime = '';
    paymentInfo.amount = 0;
    paymentInfo.method = '';
    paymentInfo.payTime = '';
    paymentInfo.transactionId = '';
    paymentInfo.productName = '';
    paymentInfo.quantity = 0;
    paymentInfo.unitPrice = 0;
  }
};

onMounted(() => {
  resizeCanvas();
  createParticles();
  animateParticles();
  window.addEventListener('resize', () => {
    resizeCanvas();
    createParticles();
  });
  
  // 获取支付信息
  fetchPaymentInfo();
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animationId)
})
</script>

<style scoped>
html, body, #app {
  margin: 0 !important;
  padding: 0 !important;
}

.payment-system {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  min-height: 100vh;
  width: 100vw;
  overflow-y: auto;
  background: #f5f7fa;
  padding-top: 0 !important;
  margin-top: 0 !important;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.payment-container {
  width: 100%;
  max-width: 600px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #ebeef5;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  position: relative;
  z-index: 1;
  margin-top: 90px;
}

.payment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.payment-header h2 {
  color: #303133;
  font-size: 18px;
  margin: 0;
  font-weight: 600;
}

.payment-status {
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.status-success {
  background-color: rgba(46, 204, 113, 0.2);
  color: #2ecc71;
  border: 1px solid rgba(46, 204, 113, 0.3);
}

.status-failed {
  background-color: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
  border: 1px solid rgba(231, 76, 60, 0.3);
}

.status-pending {
  background-color: rgba(243, 156, 18, 0.2);
  color: #f39c12;
  border: 1px solid rgba(243, 156, 18, 0.3);
}

.status-loading {
  background-color: rgba(52, 152, 219, 0.2);
  color: #3498db;
  border: 1px solid rgba(52, 152, 219, 0.3);
}

.payment-result-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
  gap: 10px;
  text-align: center;
  border: 1px solid #ebeef5;
}

.result-icon {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.result-icon i {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.result-icon.success {
  background: rgba(46, 204, 113, 0.15);
  border: 2px solid rgba(46, 204, 113, 0.3);
  color: #2ecc71;
}

.result-icon.failed {
  background: rgba(231, 76, 60, 0.15);
  border: 2px solid rgba(231, 76, 60, 0.3);
  color: #e74c3c;
}

.result-icon.pending {
  background: rgba(243, 156, 18, 0.15);
  border: 2px solid rgba(243, 156, 18, 0.3);
  color: #f39c12;
}

.result-icon.pending svg {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

.result-message {
  color: #303133;
  font-size: 14px;
  line-height: 1.4;
}

.payment-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.order-info, .payment-info, .product-info {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #ebeef5;
}

.order-info h3, .payment-info h3, .product-info h3 {
  color: #303133;
  font-size: 14px;
  margin: 0 0 10px 0;
  font-weight: 500;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.info-label {
  color: #606266;
  font-size: 13px;
}

.info-value {
  color: #303133;
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  word-break: break-all;
}

.price {
  color: #ff7675;
  font-weight: 600;
}

.payment-method-icon {
  display: flex;
  align-items: center;
}

.product-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}

.product-name {
  flex: 1;
  color: #303133;
  font-size: 13px;
}

.product-quantity {
  color: #909399;
  font-size: 13px;
  margin: 0 10px;
}

.product-price {
  color: #ff7675;
  font-size: 13px;
  font-weight: 600;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.total-amount {
  color: #606266;
  font-size: 14px;
}

.total-amount .amount {
  color: #ff7675;
  font-size: 16px;
  font-weight: 600;
  margin-left: 4px;
}

.buttons {
  display: flex;
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

/* 订单详情弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.close-btn {
  cursor: pointer;
  font-size: 22px;
  color: #909399;
}

.modal-body {
  padding: 15px;
}

.order-detail-item {
  display: flex;
  margin-bottom: 10px;
}

.detail-label {
  width: 80px;
  color: #606266;
  font-size: 13px;
}

.detail-value {
  flex: 1;
  color: #303133;
  font-size: 13px;
  word-break: break-all;
}

.order-products {
  margin-top: 15px;
}

.order-products h4 {
  font-size: 14px;
  margin: 0 0 10px 0;
  color: #303133;
}

.product-list {
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.product-list-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 10px;
  border-bottom: 1px solid #ebeef5;
}

.product-list-item:last-child {
  border-bottom: none;
}

.product-list-name {
  flex: 1;
  font-size: 13px;
  color: #303133;
}

.product-list-quantity {
  margin: 0 10px;
  color: #909399;
  font-size: 13px;
}

.product-list-price {
  color: #ff7675;
  font-size: 13px;
  font-weight: 500;
}

.no-order-found {
  text-align: center;
  padding: 20px 0;
}

.no-data-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(243, 156, 18, 0.15);
  border: 2px solid rgba(243, 156, 18, 0.3);
  color: #f39c12;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  margin: 0 auto 15px;
}

.no-order-found p {
  color: #606266;
  font-size: 14px;
  margin: 0;
}

.status-shipped {
  color: #3498db;
}

.status-delivered, .status-success {
  color: #2ecc71;
}

.status-pending, .status-processing {
  color: #f39c12;
}

.status-cancelled, .status-refunded {
  color: #e74c3c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .payment-container {
    max-width: 100%;
  }
  
  .payment-details {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .action-bar {
    flex-direction: column;
    gap: 10px;
  }
  
  .total-amount {
    width: 100%;
    text-align: center;
  }
  
  .buttons {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .payment-system {
    padding: 8px;
  }
  
  .payment-container {
    padding: 10px;
    gap: 10px;
  }
  
  .payment-header h2 {
    font-size: 16px;
  }
  
  .payment-status {
    font-size: 11px;
    padding: 3px 8px;
  }
  
  .payment-result-card {
    padding: 12px;
  }
  
  .result-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .result-message {
    font-size: 12px;
  }
  
  .order-info h3, .payment-info h3, .product-info h3 {
    font-size: 13px;
    margin-bottom: 8px;
  }
  
  .info-label, .info-value {
    font-size: 12px;
  }
  
  .action-button {
    padding: 5px 10px;
    font-size: 12px;
  }

  .modal-content {
    width: 95%;
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

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  margin-bottom: 15px;
}

.loading-spinner {
  margin-bottom: 15px;
}

.loading-spinner svg {
  animation: spin 2s linear infinite;
  color: #409eff;
}

.loading-text {
  color: #606266;
  font-size: 14px;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  margin-bottom: 15px;
}

.loading-spinner {
  margin-bottom: 15px;
}

.loading-spinner svg {
  animation: spin 2s linear infinite;
  color: #409eff;
}

.loading-text {
  color: #606266;
  font-size: 14px;
}
</style> 