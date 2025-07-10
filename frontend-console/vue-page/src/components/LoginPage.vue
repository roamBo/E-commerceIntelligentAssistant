<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="login-title">用户登录</h2>
      <el-form :model="form" :rules="rules" ref="loginForm" label-width="0" @keyup.enter.native="onLogin" tabindex="0">
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
    <!-- 註冊彈窗 -->
    <el-dialog v-model="registerDialog" title="注册新用户" width="400px">
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="0" @keyup.enter.native="onRegisterSubmit" tabindex="0">
        <el-form-item prop="username">
          <el-input v-model="registerForm.username" placeholder="用戶名" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="registerForm.password" placeholder="密码" show-password />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="registerForm.email" placeholder="电子邮件" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerDialog = false">取消</el-button>
        <el-button type="primary" @click="onRegisterSubmit" :loading="registerLoading">注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/services/api'
const form = ref({ username: '', password: '' })
const rules = {
  username: [ { required: true, message: '请输入用户名', trigger: 'blur' } ],
  password: [ { required: true, message: '请输入密码', trigger: 'blur' } ]
}
const loading = ref(false)
const loginForm = ref(null)
const user = ref(null)

// 檢查 localStorage 是否已有登入用戶
if (localStorage.getItem('loginUser')) {
  try {
    user.value = JSON.parse(localStorage.getItem('loginUser'))
  } catch (e) {
    user.value = null
  }
}

const emit = defineEmits(['login', 'register', 'forgot', 'showUser'])

// 註冊相關
const registerDialog = ref(false)
const registerForm = ref({ username: '', password: '', email: '' })
const registerFormRef = ref(null)
const registerLoading = ref(false)
const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  email: [{ required: true, message: '请输入电子邮件', trigger: 'blur' }]
}

const onLogin = () => {
  if (user.value) {
    // 已登入，顯示用戶資訊
    emit('showUser', user.value)
    return
  }
  loginForm.value.validate(async valid => {
    if (valid) {
      loading.value = true
      try {
        const loginUser = await api.userApi.login(form.value.username, form.value.password)
        loading.value = false
        user.value = loginUser
        localStorage.setItem('loginUser', JSON.stringify(loginUser))
        emit('login', loginUser)
        ElMessage.success('登入成功')
      } catch (err) {
        loading.value = false
        ElMessage.error(err.message || '登入失败')
      }
    }
  })
}
const onRegister = () => {
  registerDialog.value = true
}
const onRegisterSubmit = () => {
  registerFormRef.value.validate(async valid => {
    if (valid) {
      registerLoading.value = true
      try {
        await api.userApi.register(
          registerForm.value.username,
          registerForm.value.password,
          registerForm.value.email
        )
        registerLoading.value = false
        ElMessage.success('注册成功，请登入')
        registerDialog.value = false
        registerForm.value = { username: '', password: '', email: '' }
      } catch (err) {
        registerLoading.value = false
        ElMessage.error(err.message || '注册失败')
      }
    }
  })
}
const onForgot = () => {
  ElMessage.warning('请联系管理员或客服重置密码。')
}

const logout = () => {
  user.value = null
  localStorage.removeItem('loginUser')
}
</script>

<style scoped>
html, body, #app {
  margin: 0 !important;
  padding: 0 !important;
}

.login-page {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #0a192f 60%, #64ffda 100%);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  margin-top: 0 !important;
  padding-top: 0 !important;
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
  margin-top: 160px;
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
.login-actions .el-link--info {
  color: #409EFF !important;
}
/* 強制所有 el-input 欄位寬度固定 */
.el-input,
.el-input__inner {
  width: 100% !important;
  min-width: 0 !important;
  max-width: 100% !important;
  box-sizing: border-box;
}
</style> 