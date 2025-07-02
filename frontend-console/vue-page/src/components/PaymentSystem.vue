<template>
  <el-card class="pay-card" shadow="hover">
    <h2>支付系统</h2>
    <p>实现AI自主支付闭环，解决支付"最后一公里"问题。</p>
    <el-button type="warning" @click="pay" :disabled="paid" class="pay-btn">{{ paid ? '已支付' : '立即支付' }}</el-button>
    <transition name="fade">
      <p v-if="paid" class="pay-success">支付成功！</p>
    </transition>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
const paid = ref(false)
function pay() {
  paid.value = true
}
</script>

<style scoped>
.pay-btn {
  margin-top: 18px;
  font-size: 1.1em;
}
.pay-success {
  color: #f39c12;
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