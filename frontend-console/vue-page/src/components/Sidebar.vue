<template>
  <header class="top-navbar">
    <div 
      class="logo-title" 
      :class="{ 'active': activeIndex === 'home' }"
      @click="handleLogoClick" 
      role="button"
    >
      <span class="logo-text">智能电商助手</span>
      <div v-if="activeIndex === 'home'" class="active-indicator">
        <div class="tech-line"></div>
      </div>
    </div>
    <nav class="nav-menu">
      <div
        v-for="item in menuItems"
        :key="item.index"
        class="nav-item"
        :class="{ 'active': activeIndex === item.index }"
        @mouseenter="hoverIndex = item.index"
        @mouseleave="hoverIndex = null"
        @click="handleMenuClick(item)"
      >
        <span class="nav-label">{{ item.label }}</span>
        <div v-if="activeIndex === item.index" class="active-indicator">
          <div class="tech-line"></div>
        </div>
        <transition name="dropdown-fade">
          <div v-if="hoverIndex === item.index && item.children" class="dropdown-list">
            <div 
              v-for="child in item.children" 
              :key="child.label" 
              class="dropdown-item"
              @click.stop="handleSubmenuClick(item.index, child.label)"
            >
              <i :class="child.icon"></i>
              <span>{{ child.label }}</span>
            </div>
          </div>
        </transition>
      </div>
    </nav>
    <div class="login-icon" @click="handleLoginClick" title="点击登录">
      <svg width="28" height="28" viewBox="0 0 1024 1024" fill="none"><path d="M512 512c105.9 0 192-86.1 192-192S617.9 128 512 128 320 214.1 320 320s86.1 192 192 192zm0 64c-123.7 0-384 62.2-384 186.7V896c0 17.7 14.3 32 32 32h704c17.7 0 32-14.3 32-32v-133.3C896 638.2 635.7 576 512 576z" fill="#64ffda"/></svg>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const hoverIndex = ref(null)
const activeIndex = ref(null)

const menuItems = [
  {
    index: 'order',
    label: '订单智能管家'
  },
  {
    index: 'guide',
    label: '个性化导购助手'
  },
  {
    index: 'payment',
    label: '智能支付系统(测试)'
  }
]

const emit = defineEmits(['change', 'login'])

const handleMenuClick = (item) => {
  activeIndex.value = item.index
  emit('change', item.index)
}

const handleLogoClick = () => {
  activeIndex.value = 'home'
  emit('change', 'home')
}

const handleLoginClick = () => {
  emit('login')
}

onMounted(() => {
  activeIndex.value = 'home'
})
</script>

<style scoped>
.top-navbar {
  width: 100%;
  height: 64px;
  background: rgba(10, 25, 47, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(100, 255, 218, 0.1);
  display: flex;
  align-items: center;
  padding: 0 40px;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 2000;
}

.logo-title {
  display: flex;
  flex-direction: column;
  margin-right: 48px;
  position: relative;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.logo-title:hover {
  background: rgba(100, 255, 218, 0.1);
}

.logo-title:hover .logo-text {
  text-shadow: 0 0 20px rgba(100, 255, 218, 0.5);
}

.logo-title.active .logo-text {
  text-shadow: 0 0 20px rgba(100, 255, 218, 0.5);
}

.logo-text {
  font-size: 1.5em;
  font-weight: bold;
  color: #64ffda;
  text-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
  letter-spacing: 2px;
}

.tech-line {
  width: 80%;
  height: 2px;
  background: transparent;
  margin: 2px auto 0;
  position: relative;
  overflow: hidden;
}

.tech-line::before {
  content: '';
  position: absolute;
  width: 80px;
  height: 100%;
  background: linear-gradient(90deg, 
    rgba(100, 255, 218, 0), 
    rgba(100, 255, 218, 1), 
    rgba(100, 255, 218, 0));
  left: 0;
  top: 0;
  animation: movingLight 3s linear infinite;
}

@keyframes movingLight {
  0% {
    left: -80px;
  }
  100% {
    left: 100%;
  }
}

.nav-menu {
  display: flex;
  align-items: center;
  height: 100%;
}

.nav-item {
  position: relative;
  margin: 0 24px;
  font-size: 1.1em;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  height: 64px;
  display: flex;
  align-items: center;
  transition: color 0.3s;
}

.nav-item:hover .nav-label {
  color: #64ffda;
}

.nav-item.active .nav-label {
  color: #64ffda;
  text-shadow: 0 0 10px rgba(100, 255, 218, 0.5);
}

.nav-label {
  padding: 0 8px;
  font-weight: 500;
  position: relative;
}

.nav-label::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: #64ffda;
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.nav-item:hover .nav-label::after {
  transform: scaleX(1);
}

.active-indicator {
  position: absolute;
  bottom: 0;
  display: flex;
  justify-content: center;
  padding-bottom: 5px;
}

.nav-item .active-indicator {
  width: auto;
  left: 8px;
  right: 8px;
}

.nav-item .active-indicator .tech-line {
  width: 100%;
}

.logo-title .active-indicator {
  bottom: -5px;
  width: auto;
  left: 0;
  right: 0;
}

.logo-title .active-indicator .tech-line {
  width: 100%;
}

.dropdown-list {
  position: absolute;
  top: 64px;
  left: 0;
  background: rgba(10, 25, 47, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(100, 255, 218, 0.1);
  box-shadow: 0 8px 32px rgba(100, 255, 218, 0.2);
  border-radius: 12px;
  min-width: 180px;
  padding: 16px 0;
  display: flex;
  flex-direction: column;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 8px 24px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1em;
  transition: all 0.3s;
  cursor: pointer;
}

.dropdown-item:hover {
  background: rgba(100, 255, 218, 0.1);
  color: #64ffda;
}

.dropdown-item i {
  margin-right: 10px;
  font-size: 1.2em;
}

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: all 0.3s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@media (max-width: 992px) {
  .top-navbar {
    padding: 0 20px;
  }
  
  .logo-title {
    margin-right: 20px;
  }
  
  .nav-item {
    margin: 0 15px;
    font-size: 1em;
  }
}

@media (max-width: 768px) {
  .top-navbar {
    height: 56px;
    padding: 0 15px;
  }
  
  .logo-title {
    margin-right: 15px;
  }
  
  .logo-text {
    font-size: 1.3em;
  }
  
  .nav-item {
    margin: 0 10px;
    font-size: 0.9em;
  }
  
  .dropdown-list {
    min-width: 160px;
  }
  
  .dropdown-item {
    padding: 6px 16px;
    font-size: 0.9em;
  }
}

@media (max-width: 480px) {
  .top-navbar {
    padding: 0 10px;
  }
  
  .logo-title {
    margin-right: 10px;
  }
  
  .logo-text {
    font-size: 1.1em;
  }
  
  .nav-item {
    margin: 0 5px;
    font-size: 0.85em;
  }
  
  .dropdown-list {
    min-width: 140px;
    left: -20px;
  }
  
  .dropdown-item {
    padding: 5px 12px;
  }
  
  .dropdown-item i {
    margin-right: 5px;
  }
}

.login-icon {
  margin-left: auto;
  color: #64ffda;
  font-size: 1.7em;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 50%;
  transition: background 0.2s;
  display: flex;
  align-items: center;
}
.login-icon:hover {
  background: rgba(100,255,218,0.12);
  color: #fff;
}
</style> 