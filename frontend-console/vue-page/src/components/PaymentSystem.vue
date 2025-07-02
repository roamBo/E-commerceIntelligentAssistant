<template>
  <div class="payment-system">
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
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

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

// 查看订单详情
const viewOrderDetails = () => {
  console.log('查看订单详情', paymentInfo.orderId);
  // 实际项目中可以跳转到订单详情页
};

// 返回首页
const goBack = () => {
  console.log('返回首页');
  // 实际项目中可以跳转到首页
};
</script>

<style scoped>
.payment-system {
  height: 100%;
  background: linear-gradient(135deg, #1a2035 0%, #101425 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
}

.payment-container {
  width: 100%;
  max-width: 700px;
  background: rgba(30, 40, 60, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 25px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.payment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 15px;
}

.payment-header h2 {
  color: #fff;
  font-size: 22px;
  margin: 0;
  font-weight: 600;
}

.payment-status {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 14px;
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
  background: rgba(35, 45, 65, 0.5);
  border-radius: 12px;
  padding: 25px;
  gap: 15px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.result-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
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
  color: #fff;
  font-size: 16px;
  line-height: 1.5;
}

.payment-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.order-info, .payment-info, .product-info {
  background: rgba(35, 45, 65, 0.5);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.order-info h3, .payment-info h3, .product-info h3 {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  margin: 0 0 15px 0;
  font-weight: 500;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.info-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

.info-value {
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
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
  padding: 10px 0;
}

.product-name {
  flex: 1;
  color: #fff;
  font-size: 14px;
}

.product-quantity {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0 15px;
}

.product-price {
  color: #ff7675;
  font-size: 14px;
  font-weight: 600;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.total-amount {
  color: rgba(255, 255, 255, 0.8);
  font-size: 15px;
}

.total-amount .amount {
  color: #ff7675;
  font-size: 18px;
  font-weight: 600;
  margin-left: 5px;
}

.buttons {
  display: flex;
  gap: 10px;
}

.action-button {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
}

.action-button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.action-button.primary {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border: none;
}

.action-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .payment-details {
    grid-template-columns: 1fr;
  }
  
  .action-bar {
    flex-direction: column;
    gap: 15px;
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
</style> 