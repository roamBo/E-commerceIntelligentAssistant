<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import HomePage from './components/HomePage.vue'
import OrderManager from './components/OrderManager.vue'
import ShoppingGuide from './components/ShoppingGuide.vue'
import PaymentSystem from './components/PaymentSystem.vue'
import LoginPage from './components/LoginPage.vue'

const currentPage = ref('home')

const handleSidebarChange = (page) => {
  currentPage.value = page
}
const handleSidebarLogin = () => {
  currentPage.value = 'login'
}
const handleLoginSuccess = () => {
  currentPage.value = 'home'
}
</script>

<template>
  <div class="app-container">
    <Sidebar @change="handleSidebarChange" @login="handleSidebarLogin" />
    <main class="main-content">
      <HomePage v-if="currentPage === 'home'" @change="currentPage = $event" />
      <OrderManager v-if="currentPage === 'order'" />
      <ShoppingGuide v-if="currentPage === 'guide'" />
      <PaymentSystem v-if="currentPage === 'payment'" @change="currentPage = $event" />
      <LoginPage v-if="currentPage === 'login'" @login="handleLoginSuccess" />
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
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.main-content {
  flex: 1;
  height: calc(100% - 64px);
  overflow: hidden;
  margin-top: 64px;
}

.main-content > * {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@media (max-width: 768px) {
  .main-content {
    width: 100%;
    overflow-y: auto;
  }
}

@media (max-width: 480px) {
  .main-content {
    height: calc(100% - 56px);
    margin-top: 56px;
  }
}
</style>
