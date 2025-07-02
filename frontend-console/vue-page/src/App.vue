<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import HomePage from './components/HomePage.vue'
import OrderManager from './components/OrderManager.vue'
import ShoppingGuide from './components/ShoppingGuide.vue'
import PaymentSystem from './components/PaymentSystem.vue'

const currentPage = ref('home')
</script>

<template>
  <div class="app-container">
    <Sidebar @change="currentPage = $event" />
    <main class="main-content">
      <HomePage v-if="currentPage === 'home'" @change="currentPage = $event" />
      <OrderManager v-if="currentPage === 'order'" />
      <ShoppingGuide v-if="currentPage === 'guide'" />
      <PaymentSystem v-if="currentPage === 'payment'" />
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.app-container {
  width: 100%;
  height: 100%;
  display: flex;
  overflow: hidden;
}

.main-content {
  flex: 1;
  height: 100%;
  overflow: hidden;
}
</style>
