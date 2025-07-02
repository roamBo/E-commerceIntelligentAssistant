<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import OrderManager from './components/OrderManager.vue'
import ShoppingGuide from './components/ShoppingGuide.vue'
import PaymentSystem from './components/PaymentSystem.vue'

const currentPage = ref('dashboard')
</script>

<template>
  <el-container style="height: 100vh;">
    <el-aside width="200px">
      <Sidebar @change="currentPage = $event" />
    </el-aside>
    <el-main>
      <Dashboard v-if="currentPage === 'dashboard'" />
      <OrderManager v-if="currentPage === 'order'" />
      <ShoppingGuide v-if="currentPage === 'guide'" />
      <PaymentSystem v-if="currentPage === 'payment'" />
    </el-main>
  </el-container>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
