<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import HomePage from './components/HomePage.vue'
import OrderManager from './components/OrderManager.vue'
import ShoppingGuide from './components/ShoppingGuide.vue'
import PaymentSystem from './components/PaymentSystem.vue'
import LoginPage from './components/LoginPage.vue'
import UserInfo from './components/UserInfo.vue'

const currentPage = ref('home')
const loginUser = ref(null)

// 初始化時檢查 localStorage
if (localStorage.getItem('loginUser')) {
  try {
    loginUser.value = JSON.parse(localStorage.getItem('loginUser'))
  } catch (e) {
    loginUser.value = null
  }
}

const handleSidebarChange = (page) => {
  console.log('App: Changing page to', page)
  currentPage.value = page
}
const handleSidebarLogin = () => {
  currentPage.value = 'login'
}
const handleLoginSuccess = () => {
  currentPage.value = 'home'
}

const onLogin = (user) => {
  loginUser.value = user
}
const onShowUser = (user) => {
  loginUser.value = user
}
const onLogout = () => {
  loginUser.value = null
  localStorage.removeItem('loginUser')
}
const handleGoLogin = () => {
  currentPage.value = 'login'
}
</script>

<template>
  <div class="app-container">
    <Sidebar :currentPage="currentPage" @change="handleSidebarChange" @login="handleSidebarLogin" />
    <main class="main-content">
      <LoginPage v-if="currentPage === 'login' && !loginUser" @login="onLogin" @showUser="onShowUser" />
      <UserInfo v-if="currentPage === 'login' && loginUser" :user="loginUser" @logout="onLogout" />
      <HomePage v-if="currentPage === 'home'" />
      <OrderManager v-if="currentPage === 'order'" @goLogin="handleGoLogin" />
      <ShoppingGuide v-if="currentPage === 'guide'" @goLogin="handleGoLogin" />
      <PaymentSystem v-if="currentPage === 'payment'" @change="handleSidebarChange" />
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
