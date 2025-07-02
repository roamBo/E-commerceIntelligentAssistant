<template>
  <header class="top-navbar">
    <div class="logo-title" @click="$emit('change', 'home')" role="button">
      <span class="logo-text">智能助手</span>
      <div class="tech-line"></div>
    </div>
    <nav class="nav-menu">
      <div
        v-for="item in menuItems"
        :key="item.index"
        class="nav-item"
        @mouseenter="hoverIndex = item.index"
        @mouseleave="hoverIndex = null"
        @click="handleMenuClick(item)"
      >
        <span class="nav-label">{{ item.label }}</span>
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
  </header>
</template>

<script setup>
import { ref } from 'vue'

const hoverIndex = ref(null)
const menuItems = [
  {
    index: 'order',
    label: '订单智能管家',
    children: [
      { label: '订单查询', icon: 'el-icon-search' }
    ]
  },
  {
    index: 'guide',
    label: '个性化导购助手'
  },
  {
    index: 'payment',
    label: '智能支付系统'
  }
]

const emit = defineEmits(['change'])

const handleMenuClick = (item) => {
  // 订单智能管家不响应点击，其他菜单项正常响应
  if (item.index !== 'order') {
    emit('change', item.index)
  }
}

const handleSubmenuClick = (parentIndex, childLabel) => {
  if (parentIndex === 'order' && childLabel === '订单查询') {
    emit('change', 'order')
  }
}
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

.logo-text {
  font-size: 1.5em;
  font-weight: bold;
  color: #64ffda;
  text-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
  letter-spacing: 2px;
}

.tech-line {
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #64ffda, transparent);
  margin-top: 2px;
  animation: scanLine 2s linear infinite;
}

@keyframes scanLine {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
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

/* 添加响应式设计 */
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
    left: -20px; /* 调整下拉菜单位置，避免超出屏幕 */
  }
  
  .dropdown-item {
    padding: 5px 12px;
  }
  
  .dropdown-item i {
    margin-right: 5px;
  }
}
</style> 