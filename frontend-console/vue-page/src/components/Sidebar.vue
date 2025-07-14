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
          <circle cx="32" cy="32" r="6" fill="#00e6e6" class="logo-dot-pulse" filter="url(#glow)"/>
          <defs>
            <linearGradient id="outerGradient" x1="0" y1="0" x2="64" y2="64">
              <stop offset="0%" stop-color="#00e6e6"/>
              <stop offset="100%" stop-color="#1de9b6"/>
            </linearGradient>
            <linearGradient id="innerGradient" x1="64" y1="0" x2="0" y2="64">
              <stop offset="0%" stop-color="#fff"/>
              <stop offset="100%" stop-color="#00e6e6"/>
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
    <div class="login-icon" @click="handleLoginClick" title="點擊登入">
      <svg width="28" height="28" viewBox="0 0 1024 1024" fill="none"><path d="M512 512c105.9 0 192-86.1 192-192S617.9 128 512 128 320 214.1 320 320s86.1 192 192 192zm0 64c-123.7 0-384 62.2-384 186.7V896c0 17.7 14.3 32 32 32h704c17.7 0 32-14.3 32-32v-133.3C896 638.2 635.7 576 512 576z" fill="#00e6e6"/></svg>
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

// 監聽 currentPage 變化，自動切換高亮
watch(() => props.currentPage, (newVal) => {
  activeIndex.value = newVal
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Noto+Sans+SC:wght@400;700;900&display=swap');

:root {
  --main-font: 'Inter', 'Noto Sans SC', sans-serif;
  --logo-font: 'Inter', 'Noto Sans SC', sans-serif;
  --menu-font: 'Inter', 'Noto Sans SC', sans-serif;
  --accent-color: #00e6e6;
}

.top-navbar {
  width: 100%;
  height: 72px;
  background: rgba(30, 41, 59, 0.25);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.18);
  display: flex;
  align-items: center;
  padding: 0 48px;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 2000;
  font-family: var(--main-font);
  margin: 16px auto 0 auto;
  right: 0;
  max-width: 1200px;
}

.logo-title {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-right: 48px;
  position: relative;
  cursor: pointer;
  padding: 6px 16px;
  border-radius: 12px;
  transition: background 0.3s;
}

.logo-title:hover {
  background: rgba(0, 230, 230, 0.08);
}

.logo-title.active .logo-text {
  text-shadow: 0 0 16px var(--accent-color);
}

.animated-logo {
  display: inline-block;
  vertical-align: middle;
  width: 38px;
  height: 38px;
  margin-right: 12px;
}

.logo-text {
  font-size: 1.4em;
  font-weight: 600;
  color: var(--accent-color);
  text-shadow: 0 0 8px var(--accent-color);
  letter-spacing: 2px;
  font-family: var(--logo-font);
  text-transform: uppercase;
  background: none;
  -webkit-background-clip: unset;
  -webkit-text-fill-color: unset;
  filter: none;
}

.tech-line {
  width: 100%;
  height: 2.5px;
  background: transparent;
  margin: 6px auto 0 auto;
  position: relative;
  overflow: hidden;
  border-radius: 2px;
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
  left: -80px;
  top: 0;
  animation: movingLight 3s linear infinite;
  border-radius: 2px;
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
  margin: 0 32px;
  font-size: 1.1em;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  height: 72px;
  display: flex;
  align-items: center;
  transition: color 0.3s;
  font-weight: 500;
  letter-spacing: 1.5px;
  font-family: var(--menu-font);
  text-transform: uppercase;
}

.nav-item:hover .nav-label,
.nav-item.active .nav-label {
  color: var(--accent-color);
  text-shadow: 0 0 8px var(--accent-color);
}

/* 強化 active 狀態發光效果 */
.nav-item.active .nav-label {
  color: rgba(100,255,218,1);
  text-shadow: 0 0 15px rgba(100, 255, 218, 0.7);
  font-weight: 600;
  transform: scale(1.05);
}

.nav-label {
  padding: 0 10px;
  font-weight: 500;
  position: relative;
  transition: all 0.3s;
  font-size: 1.1em;
}

.active-indicator {
  position: absolute;
  bottom: 0;
  display: flex;
  justify-content: center;
  padding-bottom: 7px;
  left: 0;
  right: 0;
}

.nav-item .active-indicator {
  width: 100%;
}

.logo-title .active-indicator {
  bottom: -7px;
  width: 100%;
  left: 0;
  right: 0;
}

.dropdown-list {
  position: absolute;
  top: 72px;
  left: 0;
  background: rgba(30, 41, 59, 0.25);
  backdrop-filter: blur(16px) saturate(180%);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.18);
  min-width: 180px;
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  font-family: var(--main-font);
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 10px 28px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1em;
  transition: all 0.3s;
  cursor: pointer;
  letter-spacing: 0.5px;
  font-family: var(--main-font);
  border-radius: 8px;
}

.dropdown-item:hover {
  background: rgba(0,230,230,0.08);
  color: var(--accent-color);
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

.login-icon {
  margin-left: auto;
  color: var(--accent-color);
  font-size: 1.7em;
  cursor: pointer;
  padding: 10px 14px;
  border-radius: 50%;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  background: rgba(0,230,230,0.08);
  box-shadow: 0 2px 8px 0 rgba(0,230,230,0.08);
}
.login-icon:hover {
  background: rgba(0,230,230,0.18);
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

@media (max-width: 1200px) {
  .top-navbar {
    max-width: 100%;
    padding: 0 24px;
  }
  .logo-title {
    margin-right: 24px;
  }
  .nav-item {
    margin: 0 18px;
  }
}
@media (max-width: 768px) {
  .top-navbar {
    height: 60px;
    padding: 0 10px;
    border-radius: 10px;
  }
  .logo-title {
    margin-right: 10px;
    padding: 4px 8px;
  }
  .logo-text {
    font-size: 1.1em;
  }
  .nav-item {
    margin: 0 8px;
    font-size: 0.95em;
  }
  .dropdown-list {
    min-width: 120px;
    padding: 8px 0;
  }
  .dropdown-item {
    padding: 6px 12px;
    font-size: 0.95em;
  }
}
@media (max-width: 480px) {
  .top-navbar {
    height: 48px;
    padding: 0 2px;
    border-radius: 6px;
  }
  .logo-title {
    margin-right: 4px;
    padding: 2px 4px;
  }
  .logo-text {
    font-size: 0.9em;
  }
  .nav-item {
    margin: 0 2px;
    font-size: 0.85em;
  }
  .dropdown-list {
    min-width: 80px;
    left: -10px;
  }
  .dropdown-item {
    padding: 4px 6px;
    font-size: 0.85em;
  }
  .login-icon {
    padding: 6px 6px;
    font-size: 1.2em;
  }
}
</style> 