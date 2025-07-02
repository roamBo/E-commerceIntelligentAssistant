<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import OrderManager from './components/OrderManager.vue'
import ShoppingGuide from './components/ShoppingGuide.vue'

const currentPage = ref('order')
</script>

<template>
  <div class="app-container">
    <Sidebar @change="currentPage = $event" />
    <main class="main-content">
      <OrderManager v-if="currentPage === 'order'" />
      <ShoppingGuide v-if="currentPage === 'guide'" />
    </main>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  padding-top: 64px;
  background: #f8fafc;
}
.main-content {
  padding: 24px;
  margin: 0 auto;
  max-width: 1200px;
}
</style>
