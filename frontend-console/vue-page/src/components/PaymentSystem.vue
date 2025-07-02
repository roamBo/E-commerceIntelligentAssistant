<template>
  <el-card class="payment-card" shadow="hover">
    <h2>智能支付系统</h2>
    <p>多渠道支付集成，智能风控，交易数据分析。</p>
    <el-button type="primary" @click="handlePayment" class="payment-btn" :loading="loading">模拟支付流程</el-button>
    <transition name="fade">
      <p v-if="showResult" class="payment-result">支付流程模拟完成！</p>
    </transition>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
const loading = ref(false)
const showResult = ref(false)
function handlePayment() {
  loading.value = true
  showResult.value = false
  setTimeout(() => {
    loading.value = false
    showResult.value = true
  }, 1200)
}
</script>

<style scoped>
.payment-btn {
  margin-top: 18px;
  font-size: 1.1em;
}
.payment-result {
  color: #42b983;
  font-weight: bold;
  margin-top: 16px;
  font-size: 1.1em;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style> 