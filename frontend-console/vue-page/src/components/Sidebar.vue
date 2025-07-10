<template>
  <header class="top-navbar">
    <div 
      class="logo-title" 
      :class="{ 'active': activeIndex === 'home' }"
      @click="handleLogoClick" 
      role="button"
    >
      <div class="animated-logo">
        <svg width="38" height="38" viewBox="0 0 64 64">
          <circle cx="32" cy="32" r="28" stroke="url(#outerGradient)" stroke-width="4" fill="none" class="logo-ring-outer"/>
          <circle cx="32" cy="32" r="20" stroke="url(#innerGradient)" stroke-width="2.5" fill="none" class="logo-ring-inner"/>
          <circle cx="32" cy="32" r="6" fill="#64ffda" class="logo-dot-pulse" filter="url(#glow)"/>
          <defs>
            <linearGradient id="outerGradient" x1="0" y1="0" x2="64" y2="64">
              <stop offset="0%" stop-color="#64ffda"/>
              <stop offset="100%" stop-color="#1de9b6"/>
            </linearGradient>
            <linearGradient id="innerGradient" x1="64" y1="0" x2="0" y2="64">
              <stop offset="0%" stop-color="#fff"/>
              <stop offset="100%" stop-color="#64ffda"/>
            </linearGradient>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
        </svg>
      </div>
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
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  currentPage: {
    type: String,
    default: 'home'
  }
})

const hoverIndex = ref(null)
const activeIndex = ref(props.currentPage)

const menuItems = [
  {
    index: 'guide',
    label: '个性化导购助手'
  },
  {
    index: 'order',
    label: '订单智能管家'
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
  activeIndex.value = props.currentPage
})

// 监听currentPage变化，自动切换高亮
watch(() => props.currentPage, (newVal) => {
  activeIndex.value = newVal
})
</script>

<style scoped>
/* 导入更加独特的字体 */
@import url('https://fonts.googleapis.com/css2?family=Audiowide&family=Bungee+Inline&family=Bungee+Shade&family=Chakra+Petch:wght@400;600;700&family=Russo+One&family=Teko:wght@400;500;600&family=ZCOOL+KuaiLe&family=ZCOOL+QingKe+HuangYou&family=Noto+Sans+SC:wght@400;700;900&display=swap');

:root {
  --main-font: 'Chakra Petch', 'Noto Sans SC', sans-serif;
  --logo-font: 'Audiowide', 'ZCOOL KuaiLe', sans-serif;
  --menu-font: 'Teko', 'ZCOOL QingKe HuangYou', sans-serif;
  --accent-font: 'Russo One', cursive;
}

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
  font-family: var(--main-font);
}

.logo-title {
  display: flex;
  flex-direction: row;
  align-items: center;
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

.animated-logo {
  display: inline-block;
  vertical-align: middle;
  width: 38px;
  height: 38px;
  margin-right: 10px;
}

.logo-text {
  font-size: 1.6em;
  font-weight: 700;
  color: #64ffda;
  text-shadow: 0 0 15px rgba(100, 255, 218, 0.5);
  letter-spacing: 2px;
  margin-right: 0;
  font-family: var(--logo-font);
  text-transform: uppercase;
  background: linear-gradient(to right, #64ffda, #1de9b6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 8px rgba(100, 255, 218, 0.3));
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
  font-size: 1.3em;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  height: 64px;
  display: flex;
  align-items: center;
  transition: color 0.3s;
  font-weight: 500;
  letter-spacing: 1px;
  font-family: var(--menu-font);
  text-transform: uppercase;
}

.nav-item:hover .nav-label {
  color: #64ffda;
  transform: scale(1.05);
}

.nav-item.active .nav-label {
  color: #64ffda;
  text-shadow: 0 0 15px rgba(100, 255, 218, 0.7);
  font-weight: 600;
  transform: scale(1.05);
}

.nav-label {
  padding: 0 8px;
  font-weight: 500;
  position: relative;
  transition: all 0.3s ease;
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
  font-family: var(--main-font);
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 8px 24px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1em;
  transition: all 0.3s;
  cursor: pointer;
  letter-spacing: 0.5px;
  font-family: var(--main-font);
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

.logo-ring-outer {
  stroke-dasharray: 180;
  stroke-dashoffset: 0;
  transform-origin: 50% 50%;
  animation: ring-rotate-outer 2s linear infinite;
}
@keyframes ring-rotate-outer {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.logo-ring-inner {
  stroke-dasharray: 120;
  stroke-dashoffset: 0;
  transform-origin: 50% 50%;
  animation: ring-rotate-inner 4s linear infinite reverse;
}
@keyframes ring-rotate-inner {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.logo-dot-pulse {
  animation: dot-pulse 1.2s ease-in-out infinite alternate;
  filter: url(#glow);
}
@keyframes dot-pulse {
  0% { r: 6; opacity: 1; }
  70% { r: 10; opacity: 0.7; }
  100% { r: 6; opacity: 1; }
}
</style> 