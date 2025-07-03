<template>
  <div class="payment-system">
    <canvas ref="bgCanvas" class="bg-particles"></canvas>
    <div class="payment-container">
      <div class="payment-header">
        <h2>支付信息</h2>
        <div class="payment-status" :class="paymentStatus.class">
          {{ paymentStatus.text }}
        </div>
      </div>
      
      <!-- 支付结果信息卡片 -->
      <div class="payment-result-card">
        <div class="result-icon" :class="paymentStatus.id">
          <i v-if="paymentStatus.id === 'success'" class="success-icon">✓</i>
          <i v-else-if="paymentStatus.id === 'failed'" class="failed-icon">✕</i>
          <i v-else class="pending-icon">⟳</i>
        </div>
        <div class="result-message">{{ paymentStatus.message }}</div>
      </div>
      
      <!-- 订单和支付详情 -->
      <div class="payment-details">
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
      <div class="product-info">
        <h3>商品信息</h3>
        <div class="product-item">
          <div class="product-name">{{ paymentInfo.productName }}</div>
          <div class="product-quantity">x{{ paymentInfo.quantity }}</div>
          <div class="product-price">¥{{ paymentInfo.unitPrice.toFixed(2) }}</div>
        </div>
      </div>
      
      <!-- 底部操作栏 -->
      <div class="action-bar">
        <div class="total-amount">
          <span>实付金额：</span>
          <span class="amount">¥{{ paymentInfo.amount.toFixed(2) }}</span>
        </div>
        <div class="buttons">
          <button class="action-button" @click="viewOrderDetails">查看订单详情</button>
          <button class="action-button primary" @click="goBack">返回首页</button>
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
import { ref, reactive, defineEmits, onMounted, onBeforeUnmount } from 'vue';

// 定义事件
const emit = defineEmits(['change']);

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

// 当前支付状态（这里设为成功，实际应从API获取）
const paymentStatus = ref(statusTypes.success);

// 支付信息（模拟数据，实际应从API获取）
const paymentInfo = reactive({
  orderId: 'ORD98765432',
  orderTime: '2023-06-15 14:30:22',
  amount: 2499.00,
  method: 'alipay',
  payTime: '2023-06-15 14:32:15',
  transactionId: '202306151432156789123456',
  productName: '智能音箱 Pro',
  quantity: 1,
  unitPrice: 2499.00
});

// 模拟订单数据库
const orderDatabase = [
  {
    orderId: 'ORD98765432',
    orderTime: '2023-06-15 14:30:22',
    status: 'success',
    address: '北京市海淀区中关村南大街5号',
    phone: '138****1234',
    products: [
      {
        name: '智能音箱 Pro',
        quantity: 1,
        price: 2499.00
      }
    ]
  },
  {
    orderId: 'ORD87654321',
    orderTime: '2023-06-10 09:15:33',
    status: 'shipped',
    address: '上海市浦东新区张江高科技园区',
    phone: '139****5678',
    products: [
      {
        name: '智能手表',
        quantity: 1,
        price: 1299.00
      },
      {
        name: '蓝牙耳机',
        quantity: 2,
        price: 499.00
      }
    ]
  }
];

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
const viewOrderDetails = () => {
  // 模拟API查询订单
  const order = orderDatabase.find(o => o.orderId === paymentInfo.orderId);
  orderDetails.value = order || null;
  showOrderModal.value = true;
};

// 关闭弹窗
const closeModal = () => {
  showOrderModal.value = false;
};

// 返回首页
const goBack = () => {
  // 发射事件通知父组件切换到首页
  emit('change', 'home');
};

const bgCanvas = ref(null)
let animationId = null
const PARTICLE_NUM = 30
const PARTICLE_COLOR = 'rgba(120,180,255,0.18)'
const PARTICLE_RADIUS = [8, 18]
const PARTICLE_SPEED = [0.1, 0.4]
let particles = []

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
    color: PARTICLE_COLOR
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
    // 边界反弹
    if (p.x < -p.r) p.x = w + p.r
    if (p.x > w + p.r) p.x = -p.r
    if (p.y < -p.r) p.y = h + p.r
    if (p.y > h + p.r) p.y = -p.r
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.r, 0, 2 * Math.PI)
    ctx.fillStyle = p.color
    ctx.fill()
  }
  animationId = requestAnimationFrame(animateParticles)
}

onMounted(() => {
  resizeCanvas()
  createParticles()
  animateParticles()
  window.addEventListener('resize', () => {
    resizeCanvas()
    createParticles()
  })
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animationId)
})
</script>

<style scoped>
.payment-system {
  height: 100%;
  background: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 15px;
  box-sizing: border-box;
  overflow-y: auto;
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
</style> 