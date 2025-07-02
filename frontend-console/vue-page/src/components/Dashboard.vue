<template>
  <el-card class="dashboard-card" shadow="hover">
    <transition name="fade">
      <h2 v-if="show" class="dashboard-title">欢迎使用电商智能助手 Agent 仪表盘</h2>
    </transition>
    <p>请选择左侧功能进行体验。</p>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const show = ref(false)
onMounted(() => {
  setTimeout(() => { show.value = true }, 300)
})
</script>

<style scoped>
.dashboard-card {
  background: linear-gradient(120deg, #e0e7ef 0%, #f8fafc 100%);
  border: none;
}
.dashboard-title {
  font-size: 2.2em;
  letter-spacing: 2px;
  margin-bottom: 18px;
  animation: popIn 0.8s;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.6s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
@keyframes popIn {
  0% { transform: scale(0.8); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
</style> 