<template>
  <div class="home-container">
    <!-- 主标语区域 -->
    <div class="hero-section">
      <div class="slogan-wrapper">
        <h2 class="sub-heading">你梦想的智能助手</h2>
        <h1 class="main-heading">让你的购物体验更上一层楼</h1>
      </div>
      
      <!-- 三大优势 -->
      <div class="advantages">
        <div class="advantage-item">
          <div class="advantage-icon">
            <span class="emoji-icon">⚙️</span>
          </div>
          <h4>智能化处理</h4>
          <p>超快上手</p>
        </div>
        <div class="advantage-item">
          <div class="advantage-icon">
            <span class="emoji-icon">📊</span>
          </div>
          <h4>数据分析</h4>
          <p>全新体验</p>
        </div>
        <div class="advantage-item">
          <div class="advantage-icon">
            <span class="emoji-icon">🤖</span>
          </div>
          <h4>AI助手</h4>
          <p>不需烦恼</p>
        </div>
      </div>
    </div>

    <!-- 功能展示区域 -->
    <div class="features-section">
      <div class="section-header">
        <h2>依照需求选择功能</h2>
        <p>为您的购物提供全方位的智能解决方案</p>
      </div>
      
      <div class="feature-cards">
        <div class="feature-card fly-in-bottom" :class="{ 'in-view': inView }" ref="orderCard" @click="$emit('change', 'order')">
          <div class="feature-icon">
            <span class="emoji-icon">🛒</span>
          </div>
          <h3>订单智能管家</h3>
          <ul class="feature-list">
            <li><i class="el-icon-check"></i> 智能订单处理</li>
            <li><i class="el-icon-check"></i> 实时监控预警</li>
            <li><i class="el-icon-check"></i> 自动分类管理</li>
          </ul>
          <div class="feature-action">
            <el-button type="primary" class="action-button" @click.stop="$emit('change', 'order')">立即使用</el-button>
          </div>
        </div>
        <div class="feature-card fly-in-bottom" :class="{ 'in-view': inView }" ref="guideCard" @click="$emit('change', 'guide')">
          <div class="feature-icon">
            <span class="emoji-icon">🤖</span>
          </div>
          <h3>个性化导购助手</h3>
          <ul class="feature-list">
            <li><i class="el-icon-check"></i> AI智能推荐</li>
            <li><i class="el-icon-check"></i> 用户行为分析</li>
            <li><i class="el-icon-check"></i> 精准营销方案</li>
          </ul>
          <div class="feature-action">
            <el-button type="primary" class="action-button" @click.stop="$emit('change', 'guide')">立即使用</el-button>
          </div>
        </div>
        <div class="feature-card fly-in-bottom" :class="{ 'in-view': inView }" ref="paymentCard" @click="$emit('change', 'payment')">
          <div class="feature-icon">
            <span class="emoji-icon">💳</span>
          </div>
          <h3>智能支付系统</h3>
          <ul class="feature-list">
            <li><i class="el-icon-check"></i> 多渠道支付集成</li>
            <li><i class="el-icon-check"></i> 智能风控机制</li>
            <li><i class="el-icon-check"></i> 交易数据分析</li>
          </ul>
          <div class="feature-action">
            <el-button type="primary" class="action-button" @click.stop="$emit('change', 'payment')">立即使用</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 解决方案区域 -->
    <div class="solutions-section">
      <div class="solution-item">
        <span class="solution-number">01</span>
        <h3>智能化管理</h3>
        <p>无需复杂操作，智能系统自动处理订单流程，让购物更轻松高效。</p>
      </div>
      <div class="solution-item">
        <span class="solution-number">02</span>
        <h3>数据分析</h3>
        <p>深度分析用户行为，提供精准的营销策略和商品推荐。</p>
      </div>
      <div class="solution-item">
        <span class="solution-number">03</span>
        <h3>全天候服务</h3>
        <p>AI助手24小时在线，随时解答问题，提供专业支持。</p>
      </div>
    </div>

    <!-- 添加滚动提示箭头 -->
    <div class="scroll-indicator" @click="scrollToNext">
      <span class="scroll-emoji">🚀</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const emits = defineEmits(['change']);
const inView = ref(false);
const orderCard = ref(null);
const guideCard = ref(null);
const paymentCard = ref(null);

onMounted(() => {
  const observer = new window.IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        inView.value = true;
      }
    });
  }, { threshold: 0.3 });

  if (orderCard.value) observer.observe(orderCard.value);
  if (guideCard.value) observer.observe(guideCard.value);
  if (paymentCard.value) observer.observe(paymentCard.value);

  // 清理 observer
  onBeforeUnmount(() => {
    observer.disconnect();
  });
});

const scrollToNext = () => {
  const sections = document.querySelectorAll('.hero-section, .features-section, .solutions-section');
  const scrollPosition = window.scrollY;
  
  for (let section of sections) {
    const sectionTop = section.offsetTop;
    if (sectionTop > scrollPosition + 100) {
      section.scrollIntoView({ behavior: 'smooth' });
      break;
    }
  }
};
</script>

<style scoped>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

.home-container {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  scroll-behavior: smooth;
  background: linear-gradient(135deg, #ffffff 0%, #f5f7fa 100%);
  color: #2c3e50;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

/* 确保每个区块都有合适的高度 - 减少滚动距离 */
.hero-section {
  min-height: 80vh; /* 从70vh增加到80vh */
  padding: 60px 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.features-section {
  min-height: auto; /* 取消最小高度限制，让内容决定高度 */
  padding: 60px 20px; /* 减少上下内边距 */
  background: #fff;
}

.solutions-section {
  min-height: auto; /* 取消最小高度限制，让内容决定高度 */
  padding: 60px 20px; /* 减少上下内边距 */
  margin-bottom: 40px; /* 增加底部边距，避免最后内容太靠近底部 */
}

.slogan-wrapper {
  margin-bottom: 40px; /* 从60px减少到40px */
}

.sub-heading {
  font-size: 24px;
  color: #666;
  margin-bottom: 20px;
  font-weight: normal;
}

.main-heading {
  font-size: 48px;
  color: #2c3e50;
  font-weight: bold;
  margin-bottom: 40px;
}

.advantages {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 40px; /* 从60px减少到40px */
}

.advantage-item {
  text-align: center;
  padding: 20px;
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.7s ease forwards;
}
.advantage-item:nth-child(1) {
  animation-delay: 0.1s;
}
.advantage-item:nth-child(2) {
  animation-delay: 0.4s;
}
.advantage-item:nth-child(3) {
  animation-delay: 0.7s;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.advantage-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 10px 20px rgba(0,0,0,0.05);
}

.advantage-icon .emoji-icon {
  font-size: 38px;
  line-height: 1;
}

.advantage-item h4 {
  font-size: 20px;
  margin: 15px 0 10px;
  color: #2c3e50;
}

.advantage-item p {
  color: #666;
  font-size: 16px;
}

.section-header {
  text-align: center;
  margin-bottom: 40px; /* 从60px减少到40px */
}

.section-header h2 {
  font-size: 36px;
  color: #2c3e50;
  margin-bottom: 20px;
}

.section-header p {
  color: #666;
  font-size: 18px;
}

.feature-cards {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: #fff;
  border-radius: 12px;
  padding: 30px;
  width: 300px;
  text-align: center;
  transition: all 0.7s cubic-bezier(0.23, 1, 0.32, 1);
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  opacity: 0;
  pointer-events: none;
  margin-bottom: 20px;
}

.feature-card:nth-child(1) {
  transition-delay: 0.1s;
}

.feature-card:nth-child(2) {
  transition-delay: 0.3s;
}

.feature-card:nth-child(3) {
  transition-delay: 0.5s;
}

.feature-card.in-view {
  opacity: 1;
  pointer-events: auto;
}

.fly-in-left {
  transform: translateX(-500px);
}
.fly-in-right {
  transform: translateX(500px);
}
.fly-in-bottom {
  transform: translateY(200px);
}
.feature-card.in-view.fly-in-left {
  transform: translateX(0);
}
.feature-card.in-view.fly-in-right {
  transform: translateX(0);
}
.feature-card.in-view.fly-in-bottom {
  transform: translateY(0);
}

.feature-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 30px;
}

.emoji-icon {
  font-size: 40px;
  line-height: 1;
}

.feature-card h3 {
  font-size: 24px;
  color: #2c3e50;
  margin-bottom: 20px;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0 0 30px;
  text-align: left;
}

.feature-list li {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  color: #666;
}

.feature-list li i {
  color: #409EFF;
  margin-right: 10px;
}

.feature-action {
  margin-top: 30px;
}

.action-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 22px;
}

.solution-item {
  padding: 30px;
  background: #fff;
  border-radius: 12px;
  position: relative;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}

.solution-number {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 48px;
  color: #f5f7fa;
  font-weight: bold;
}

.solution-item h3 {
  font-size: 24px;
  color: #2c3e50;
  margin-bottom: 15px;
  position: relative;
  z-index: 1;
}

.solution-item p {
  color: #666;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

@media (max-width: 1200px) {
  .feature-cards {
    justify-content: center;
  }
  
  .feature-card {
    width: calc(50% - 30px);
    min-width: 280px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    min-height: 80vh; /* 移动端也调整为80vh */
  }
  
  .main-heading {
    font-size: 36px;
  }
  
  .advantages {
    flex-direction: column;
    gap: 20px;
  }
  
  .feature-cards {
    flex-direction: column;
    align-items: center;
  }
  
  .feature-card {
    width: 100%;
    max-width: 360px;
  }
  
  .solutions-section {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 40px 20px; /* 移动端更紧凑 */
  }
  
  .features-section {
    padding: 40px 20px; /* 移动端更紧凑 */
  }
}

/* 滚动条整体样式 */
.home-container::-webkit-scrollbar {
  width: 8px;
  background-color: #fffffff6;
}

/* 滚动条轨道样式 */
.home-container::-webkit-scrollbar-track {
  background-color: transparent;
  border-radius: 4px;
}

/* 滚动条滑块样式 */
.home-container::-webkit-scrollbar-thumb {
  background-color: #d0ddea;
  border-radius: 4px;
  transition: all 0.3s ease;
}

/* 滚动条滑块悬停效果 */
.home-container::-webkit-scrollbar-thumb:hover {
  background-color: #337ecc;
}

/* 确保内容区域有合适的内边距 - 调整动画但保持内边距一致 */
.hero-section,
.features-section,
.solutions-section {
  padding: 60px 20px; /* 保持一致的内边距 */
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.6s ease forwards;
}

/* 添加渐入动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 为不同区块设置不同的动画延迟 */
.hero-section {
  animation-delay: 0.2s;
}

.features-section {
  animation-delay: 0.4s;
}

.solutions-section {
  animation-delay: 0.6s;
}

/* 添加滚动提示箭头 */
.scroll-indicator {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 50px;
  background-color: #fff;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: bounce 2s infinite;
  z-index: 100;
}

.scroll-emoji {
  font-size: 24px;
  line-height: 1;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0) translateX(-50%);
  }
  40% {
    transform: translateY(-10px) translateX(-50%);
  }
  60% {
    transform: translateY(-5px) translateX(-50%);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .home-container::-webkit-scrollbar {
    width: 4px;
  }
  
  .scroll-indicator {
    width: 40px;
    height: 40px;
    bottom: 20px;
  }
  
  .scroll-emoji {
    font-size: 20px;
  }
}
</style> 