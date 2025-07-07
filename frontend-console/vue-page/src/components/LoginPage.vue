<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="login-title">用户登录</h2>
      <el-form :model="form" :rules="rules" ref="loginForm" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="el-icon-user" clearable />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" placeholder="密码" prefix-icon="el-icon-lock" show-password clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="login-btn" @click="onLogin" :loading="loading" style="width:100%">登录</el-button>
        </el-form-item>
        <div class="login-actions">
          <el-link type="primary" @click="onRegister">注册</el-link>
          <el-link type="info" @click="onForgot">忘记密码？</el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const form = ref({ username: '', password: '' })
const rules = {
  username: [ { required: true, message: '请输入用户名', trigger: 'blur' } ],
  password: [ { required: true, message: '请输入密码', trigger: 'blur' } ]
}
const loading = ref(false)
const loginForm = ref(null)

const emit = defineEmits(['login', 'register', 'forgot'])

// 數據庫連接資訊（僅示意，實際連接請在後端進行）
// 連接地址: mysql2.sqlpub.com:3307
// 數據庫用戶: login_user
// 數據庫名稱: login_user
// 例如（Node.js後端可用）：
// const mysql = require('mysql2');
// const connection = mysql.createConnection({
//   host: 'mysql2.sqlpub.com',
//   port: 3307,
//   user: 'login_user',
//   password: '你的密碼',
//   database: 'login_user'
// });
// connection.connect();

const onLogin = () => {
  loginForm.value.validate(valid => {
    if (valid) {
      loading.value = true
      setTimeout(() => {
        loading.value = false
        emit('login', form.value)
      }, 1000)
    }
  })
}
const onRegister = () => emit('register')
const onForgot = () => emit('forgot')
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a192f 60%, #64ffda 100%);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 120px;
}
.login-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(10,25,47,0.15);
  padding: 40px 32px 32px 32px;
  min-width: 320px;
  max-width: 90vw;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.login-title {
  color: #0a192f;
  font-size: 2em;
  font-weight: bold;
  margin-bottom: 32px;
  letter-spacing: 2px;
}
.login-btn {
  width: 100%;
  font-size: 1.1em;
  font-weight: bold;
  letter-spacing: 1px;
}
.login-actions {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 8px;
}
</style> 