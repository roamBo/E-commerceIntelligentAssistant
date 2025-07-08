<template>
  <div class="user-info-bg">
    <div class="user-info-card">
      <div class="user-header">
        <img class="avatar" :src="`https://api.dicebear.com/7.x/identicon/svg?seed=${user.username}`" alt="avatar" />
        <div class="user-basic">
          <div class="user-welcome">你好，<span class="user-name">{{ user.username }}</span></div>
          <div class="user-email">{{ user.email }}</div>
        </div>
      </div>
      <div class="user-detail">
        <div class="user-id-row"><span class="label">用户ID：</span>{{ user.userID }}</div>
      </div>
      <el-button type="danger" class="logout-btn" @click="onLogout">退出登录</el-button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})
const emit = defineEmits(['logout'])
const onLogout = () => {
  emit('logout')
}
</script>

<style scoped>
.user-info-bg {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #0a192f 60%, #64ffda 100%);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 120px;
}
.user-info-card {
  background: rgba(255,255,255,0.98);
  border-radius: 20px;
  box-shadow: 0 12px 40px rgba(10,25,47,0.18), 0 1.5px 8px rgba(100,255,218,0.08);
  padding: 40px 36px 32px 36px;
  min-width: 360px;
  max-width: 96vw;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  font-family: 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
  position: relative;
  z-index: 2;
}
.user-header {
  display: flex;
  align-items: center;
  width: 100%;
  margin-bottom: 22px;
}
.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #f0f0f0;
  margin-right: 24px;
  box-shadow: 0 2px 8px rgba(100,255,218,0.10);
}
.user-basic {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.user-welcome {
  font-size: 1.4em;
  font-weight: bold;
  color: #0a192f;
  margin-bottom: 4px;
}
.user-name {
  color: #64ffda;
}
.user-email {
  font-size: 1em;
  color: #888;
}
.user-detail {
  margin-bottom: 28px;
  width: 100%;
}
.user-id-row {
  font-size: 1.08em;
  color: #222;
  background: #f6f8fa;
  border-radius: 8px;
  padding: 10px 16px;
  margin-top: 2px;
  margin-bottom: 2px;
}
.label {
  color: #888;
  margin-right: 6px;
}
.logout-btn {
  align-self: flex-end;
  margin-top: 10px;
  font-weight: bold;
  letter-spacing: 1px;
}
</style> 