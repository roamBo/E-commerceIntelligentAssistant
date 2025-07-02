<template>
  <el-card class="order-card" shadow="hover">
    <h2>订单智能管家</h2>
    <p>自动化处理订单全流程（查询/修改/异常预警）。</p>
    <el-button type="primary" @click="handleOrder" class="order-btn" :loading="loading">一键处理订单</el-button>
    <transition name="fade">
      <p v-if="showResult" class="order-result">订单处理完成！</p>
    </transition>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
const loading = ref(false)
const showResult = ref(false)
function handleOrder() {
  loading.value = true
  showResult.value = false
  setTimeout(() => {
    loading.value = false
    showResult.value = true
  }, 1200)
}
</script>

<style scoped>
.order-btn {
  margin-top: 18px;
  font-size: 1.1em;
}
.order-result {
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