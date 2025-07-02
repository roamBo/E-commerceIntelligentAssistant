<template>
  <el-card class="guide-card" shadow="hover">
    <h2>个性化导购助手</h2>
    <p>根据用户行为实时推荐商品，提升转化率15%-20%。</p>
    <el-button type="success" @click="showRecs = !showRecs">{{ showRecs ? '收起推荐' : '一键推荐商品' }}</el-button>
    <transition-group name="list" tag="div">
      <div v-for="item in recs" v-if="showRecs" :key="item.id" class="rec-item">
        <el-card shadow="never" class="rec-card">
          <b>{{ item.name }}</b>
          <p style="margin:0;">{{ item.desc }}</p>
        </el-card>
      </div>
    </transition-group>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
const showRecs = ref(false)
const recs = ref([
  { id: 1, name: '智能蓝牙耳机', desc: 'AI降噪，舒适佩戴' },
  { id: 2, name: '健康手环', desc: '实时监测，健康管理' },
  { id: 3, name: '智能家居套装', desc: '一站式智能生活体验' }
])
</script>

<style scoped>
.guide-card {
  min-height: 220px;
}
.rec-item {
  margin-top: 18px;
  animation: fadeInUp 0.6s;
}
.rec-card {
  background: #f4f8ff;
  border-radius: 12px;
  margin-bottom: 8px;
}
.list-enter-active, .list-leave-active {
  transition: all 0.5s;
}
.list-enter-from, .list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
@keyframes fadeInUp {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style> 