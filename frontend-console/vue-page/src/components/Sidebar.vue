<template>
  <header class="top-navbar">
    <div class="logo-title">
      <img src="" alt="logo" class="logo-img" />
      <span class="logo-text">智能助手</span>
    </div>
    <nav class="nav-menu">
      <div
        v-for="item in menuItems"
        :key="item.index"
        class="nav-item"
        @mouseenter="hoverIndex = item.index"
        @mouseleave="hoverIndex = null"
      >
        <span class="nav-label">{{ item.label }}</span>
        <transition name="dropdown-fade">
          <div v-if="hoverIndex === item.index && item.children" class="dropdown-list">
            <div v-for="child in item.children" :key="child.label" class="dropdown-item">
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
      { label: '订单查询', icon: 'el-icon-search' },
      { label: '订单修改', icon: 'el-icon-edit' },
      { label: '异常预警', icon: 'el-icon-warning' }
    ]
  },
  {
    index: 'guide',
    label: '个性化导购助手',
    children: [
      { label: '商品推荐', icon: 'el-icon-goods' },
      { label: '用户分析', icon: 'el-icon-user' }
    ]
  }
]
</script>

<style scoped>
.top-navbar {
  width: 100vw;
  height: 64px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(79,140,255,0.08);
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
  align-items: center;
  margin-right: 48px;
}
.logo-img {
  width: 38px;
  height: 38px;
  margin-right: 10px;
}
.logo-text {
  font-size: 1.5em;
  font-weight: bold;
  color: #3358c5;
  letter-spacing: 2px;
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
  color: #222;
  cursor: pointer;
  height: 64px;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}
.nav-item:hover .nav-label {
  color: #4f8cff;
}
.nav-label {
  padding: 0 8px;
  font-weight: 500;
}
.dropdown-list {
  position: absolute;
  top: 64px;
  left: 0;
  background: #fff;
  box-shadow: 0 8px 32px 0 rgba(79,140,255,0.12);
  border-radius: 12px;
  min-width: 180px;
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  animation: dropdownIn 0.25s;
}
@keyframes dropdownIn {
  0% { opacity: 0; transform: translateY(10px) scale(0.98); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}
.dropdown-item {
  display: flex;
  align-items: center;
  padding: 8px 24px;
  color: #3358c5;
  font-size: 1em;
  transition: background 0.2s, color 0.2s;
  cursor: pointer;
}
.dropdown-item:hover {
  background: #f4f8ff;
  color: #4f8cff;
}
.dropdown-item i {
  margin-right: 10px;
  font-size: 1.2em;
}
.dropdown-fade-enter-active, .dropdown-fade-leave-active {
  transition: opacity 0.2s;
}
.dropdown-fade-enter-from, .dropdown-fade-leave-to {
  opacity: 0;
}
</style> 