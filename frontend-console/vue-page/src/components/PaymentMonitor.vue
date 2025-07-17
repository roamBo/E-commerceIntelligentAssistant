<template>
  <!-- 支付监控组件 - 不显示任何UI，仅在后台监控支付状态 -->
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import paymentService from '../services/paymentService';

// 定义事件
const emit = defineEmits(['payment-status-changed']);

// 轮询控制器
const pollController = ref(null);

// 当前用户ID
const userId = ref(null);

// 监控状态
const isMonitoring = ref(false);

// 获取当前登录用户ID
const getCurrentUserId = () => {
  try {
    const loginUserStr = localStorage.getItem('loginUser');
    if (loginUserStr) {
      const user = JSON.parse(loginUserStr);
      // 尝试获取用户ID（可能存储在不同字段）
      return user.id || user.userID || user.userId || user.user_id;
    }
  } catch (error) {
    console.error('获取用户ID失败:', error);
  }
  return null;
};

// 处理支付状态变化
const handlePaymentStatusChange = (payment, changeType) => {
  console.log(`支付监控: 检测到支付状态变化 (${changeType})`, payment);
  
  // 检查状态变化类型
  if (changeType === 'PENDING_TO_SUCCESS') {
    console.log('支付监控: 检测到订单支付成功，触发界面显示');
    
    // 发出事件通知父组件显示支付界面
    emit('payment-status-changed', {
      type: 'PAYMENT_SUCCESS',
      payment: payment
    });
  } else if (changeType === 'NEW_PAYMENT') {
    // 检查新支付记录的状态
    const status = (payment.status || '').toLowerCase();
    if (status === 'success') {
      console.log('支付监控: 检测到新的已支付订单，触发界面显示');
      emit('payment-status-changed', {
        type: 'PAYMENT_SUCCESS',
        payment: payment
      });
    }
  } else if (changeType === 'STATUS_CHANGED') {
    // 检查是否是其他状态变为SUCCESS
    const status = (payment.status || '').toLowerCase();
    if (status === 'success') {
      console.log('支付监控: 检测到订单状态变为已支付，触发界面显示');
      emit('payment-status-changed', {
        type: 'PAYMENT_SUCCESS',
        payment: payment
      });
    }
  }
};

// 启动监控
const startMonitoring = () => {
  // 获取当前登录用户ID
  const currentUserId = getCurrentUserId();
  if (!currentUserId) {
    console.warn('支付监控: 未找到用户ID，无法启动监控');
    return;
  }
  
  userId.value = currentUserId;
  console.log(`支付监控: 开始监控用户 ${userId.value} 的支付状态`);
  
  // 停止之前的监控（如果有）
  stopMonitoring();
  
  // 开始新的轮询
  pollController.value = paymentService.pollPaymentStatusChanges(
    userId.value,
    handlePaymentStatusChange,
    3000 // 每3秒轮询一次
  );
  
  isMonitoring.value = true;
};

// 停止监控
const stopMonitoring = () => {
  if (pollController.value) {
    pollController.value.stop();
    pollController.value = null;
    isMonitoring.value = false;
    console.log('支付监控: 已停止监控');
  }
};

// 监听用户登录状态变化
watch(() => localStorage.getItem('loginUser'), (newValue) => {
  if (newValue) {
    // 用户登录，启动监控
    startMonitoring();
  } else {
    // 用户登出，停止监控
    stopMonitoring();
  }
});

// 组件挂载时启动监控
onMounted(() => {
  startMonitoring();
});

// 组件卸载前停止监控
onBeforeUnmount(() => {
  stopMonitoring();
});

// 导出方法供父组件调用
defineExpose({
  startMonitoring,
  stopMonitoring
});
</script> 