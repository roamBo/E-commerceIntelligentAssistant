<template>
  <div class="home-container">
    <!-- 主标语区域 -->
    <div class="hero-section">
      <!-- 添加装饰元素 -->
      <div class="hero-decoration dot-grid"></div>
      <div class="hero-decoration wave"></div>
      <div class="hero-decoration circle"></div>
      <div class="hero-decoration square"></div>
      <div class="hero-decoration triangle"></div>
      
      <div class="slogan-wrapper">
        <h2 class="sub-heading">你梦想的智能助手</h2>
        <h1 class="main-heading">让你的购物体验更上一层楼</h1>
      </div>
      
      <!-- 三大优势 - 修改为灵动布局 -->
      <div class="advantages-container">
        <div class="advantage-item advantage-item-1">
          <div class="advantage-icon">
            <div class="gear-wrapper">
            <span class="emoji-icon">⚙️</span>
            </div>
          </div>
          <h4>智能化处理</h4>
          <p>超快上手</p>
        </div>
        <div class="advantage-item advantage-item-2">
          <div class="advantage-icon">
            <span class="emoji-icon">📊</span>
          </div>
          <h4>数据分析</h4>
          <p>全新体验</p>
        </div>
        <div class="advantage-item advantage-item-3">
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
      <!-- 添加装饰元素 -->
      <div class="features-decoration blob-1"></div>
      <div class="features-decoration blob-2"></div>
      <div class="features-decoration dots-pattern"></div>
      
      <div class="section-header">
        <div class="section-title-decoration"></div>
        <h2>依照需求选择功能</h2>
        <p>为您的购物提供全方位的智能解决方案</p>
      </div>
      
      <div class="feature-cards">
        <div class="feature-card fly-in-bottom" :class="{ 'in-view': inView }" ref="orderCard" @click.prevent="navigateTo('order', $event)">
          <div class="card-highlight"></div>
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
            <el-button type="primary" class="action-button" @click.stop.prevent="navigateTo('order', $event)">立即查询</el-button>
          </div>
        </div>
        <div class="feature-card fly-in-bottom" :class="{ 'in-view': inView }" ref="guideCard" @click.prevent="navigateTo('guide', $event)">
          <div class="card-highlight"></div>
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
            <el-button type="primary" class="action-button" @click.stop.prevent="navigateTo('guide', $event)">立即使用</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 解决方案区域 -->
    <div class="solutions-section">
      <!-- 添加装饰元素 -->
      <div class="solutions-decoration wave-line"></div>
      <div class="solutions-decoration dots-grid"></div>
      
      <div class="solution-item solution-1 fly-in-bottom" :class="{ 'in-view': solution1Visible }" ref="solution1">
        <div class="solution-icon">01</div>
        <h3>智能化管理</h3>
        <p>无需复杂操作，智能系统自动处理订单流程，让购物更轻松高效。</p>
        <div class="solution-highlight"></div>
      </div>
      <div class="solution-item solution-2 fly-in-bottom" :class="{ 'in-view': solution2Visible }" ref="solution2">
        <div class="solution-icon">02</div>
        <h3>数据分析</h3>
        <p>深度分析用户行为，提供精准的营销策略和商品推荐。</p>
        <div class="solution-highlight"></div>
      </div>
      <div class="solution-item solution-3 fly-in-bottom" :class="{ 'in-view': solution3Visible }" ref="solution3">
        <div class="solution-icon">03</div>
        <h3>全天候服务</h3>
        <p>AI助手24小时在线，随时解答问题，提供专业支持。</p>
        <div class="solution-highlight"></div>
      </div>
      <div class="solution-item solution-4 fly-in-bottom" :class="{ 'in-view': solution4Visible }" ref="solution4">
        <div class="solution-icon">04</div>
        <h3>安全支付系统</h3>
        <p>多渠道支付集成，智能风控机制，确保交易数据安全，提供便捷支付体验。</p>
        <div class="solution-highlight"></div>
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
const solution1Visible = ref(false);
const solution2Visible = ref(false);
const solution3Visible = ref(false);
const solution4Visible = ref(false);
const orderCard = ref(null);
const guideCard = ref(null);
const solution1 = ref(null);
const solution2 = ref(null);
const solution3 = ref(null);
const solution4 = ref(null);

// 导航到指定页面
const navigateTo = (page, e) => {
  console.log('HomePage: Navigating to', page);
  // 阻止事件冒泡，防止多次触发
  if (e) {
    e.stopPropagation();
    e.preventDefault();
  }
  // 添加延时以确保事件不会被覆盖或丢失
  setTimeout(() => {
    emits('change', page);
  }, 10);
};

onMounted(() => {
  // 功能卡片的观察器
  const featureObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        inView.value = true;
      }
    });
  }, { threshold: 0.3 });

  // 为每个解决方案卡片创建独立的观察器，添加延迟效果
  const solutionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // 根据当前观察到的元素ID来设置对应的可见状态，并添加延迟
        const elementId = entry.target.id;
        switch(elementId) {
          case 'solution1':
            setTimeout(() => {
              solution1Visible.value = true;
            }, 0); // 第一个卡片立即显示
            break;
          case 'solution2':
            setTimeout(() => {
              solution2Visible.value = true;
            }, 200); // 第二个卡片延迟200ms
            break;
          case 'solution3':
            setTimeout(() => {
              solution3Visible.value = true;
            }, 400); // 第三个卡片延迟400ms
            break;
          case 'solution4':
            setTimeout(() => {
              solution4Visible.value = true;
            }, 600); // 第四个卡片延迟600ms
            break;
        }
      }
    });
  }, { threshold: 0.2 });

  // 观察功能卡片
  if (orderCard.value) featureObserver.observe(orderCard.value);
  if (guideCard.value) featureObserver.observe(guideCard.value);
  
  // 为每个解决方案卡片添加ID并单独观察
  if (solution1.value) {
    solution1.value.id = 'solution1';
    solutionObserver.observe(solution1.value);
  }
  if (solution2.value) {
    solution2.value.id = 'solution2';
    solutionObserver.observe(solution2.value);
  }
  if (solution3.value) {
    solution3.value.id = 'solution3';
    solutionObserver.observe(solution3.value);
  }
  if (solution4.value) {
    solution4.value.id = 'solution4';
    solutionObserver.observe(solution4.value);
  }

  // 清理 observer
  onBeforeUnmount(() => {
    featureObserver.disconnect();
    solutionObserver.disconnect();
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
  position: relative;
  overflow: hidden;
}

/* 添加hero section的背景装饰元素 */
.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 10% 10%, rgba(64, 158, 255, 0.06) 0%, transparent 25%),
    radial-gradient(circle at 90% 90%, rgba(103, 194, 58, 0.06) 0%, transparent 25%),
    radial-gradient(circle at 50% 50%, rgba(245, 108, 108, 0.03) 0%, transparent 30%);
  z-index: 0;
}

.hero-section::after {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.05) 0%, rgba(103, 194, 58, 0.05) 100%);
  top: -150px;
  right: -150px;
  animation: floatCircle 15s infinite linear;
  z-index: 0;
}

@keyframes floatCircle {
  0% {
    transform: rotate(0deg) translateX(0) translateY(0);
  }
  25% {
    transform: rotate(90deg) translateX(30px) translateY(30px);
  }
  50% {
    transform: rotate(180deg) translateX(0) translateY(60px);
  }
  75% {
    transform: rotate(270deg) translateX(-30px) translateY(30px);
  }
  100% {
    transform: rotate(360deg) translateX(0) translateY(0);
  }
}

/* 装饰性元素 */
.hero-decoration {
  position: absolute;
  z-index: 0;
  opacity: 0.6;
}

.hero-decoration.dot-grid {
  width: 200px;
  height: 200px;
  background-image: radial-gradient(rgba(103, 194, 58, 0.3) 1px, transparent 1px);
  background-size: 16px 16px;
  left: 5%;
  bottom: 15%;
  border-radius: 8px;
  transform: rotate(-15deg);
}

.hero-decoration.wave {
  width: 150px;
  height: 50px;
  right: 10%;
  top: 20%;
  background-image: 
    linear-gradient(90deg, rgba(64, 158, 255, 0) 0%, rgba(64, 158, 255, 0.2) 50%, rgba(64, 158, 255, 0) 100%);
  filter: blur(20px);
  animation: waveMove 8s infinite ease-in-out;
}

@keyframes waveMove {
  0%, 100% {
    transform: translateX(-30px) translateY(0);
  }
  50% {
    transform: translateX(30px) translateY(20px);
  }
}

.hero-decoration.circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 2px solid rgba(64, 158, 255, 0.1);
  left: 15%;
  top: 20%;
  animation: float 12s infinite ease-in-out;
}

.hero-decoration.square {
  width: 80px;
  height: 80px;
  border: 2px solid rgba(103, 194, 58, 0.1);
  right: 20%;
  bottom: 20%;
  animation: rotateAndFloat 20s infinite linear;
}

@keyframes rotateAndFloat {
  0% {
    transform: rotate(0deg) translateY(0);
  }
  25% {
    transform: rotate(90deg) translateY(-15px);
  }
  50% {
    transform: rotate(180deg) translateY(0);
  }
  75% {
    transform: rotate(270deg) translateY(15px);
  }
  100% {
    transform: rotate(360deg) translateY(0);
  }
}

.hero-decoration.triangle {
  width: 0;
  height: 0;
  border-left: 50px solid transparent;
  border-right: 50px solid transparent;
  border-bottom: 80px solid rgba(245, 108, 108, 0.05);
  position: absolute;
  left: 30%;
  top: 60%;
  animation: float 18s infinite ease-in-out reverse;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.slogan-wrapper, .advantages {
  position: relative;
  z-index: 1;
}

.features-section {
  min-height: auto;
  padding: 80px 20px; /* 增加上下内边距使区域更宽敞 */
  background: #fff;
  position: relative;
  overflow: hidden;
}

/* 添加features section的装饰元素 */
.features-decoration {
  position: absolute;
  z-index: 0;
  pointer-events: none;
}

.features-decoration.blob-1 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle at center, rgba(64, 158, 255, 0.05) 0%, transparent 70%);
  border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
  top: -50px;
  left: -100px;
  animation: blob-morph 15s ease-in-out infinite alternate;
}

.features-decoration.blob-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle at center, rgba(103, 194, 58, 0.05) 0%, transparent 70%);
  border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
  bottom: -100px;
  right: -150px;
  animation: blob-morph 20s ease-in-out infinite alternate-reverse;
}

.features-decoration.dots-pattern {
  width: 200px;
  height: 200px;
  background-image: radial-gradient(rgba(64, 158, 255, 0.2) 1px, transparent 1px);
  background-size: 20px 20px;
  top: 30%;
  right: 10%;
  opacity: 0.2;
  transform: rotate(15deg);
}

@keyframes blob-morph {
  0% {
    border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
    transform: rotate(0deg);
  }
  50% {
    border-radius: 60% 40% 50% 70% / 60% 40% 60% 40%;
    transform: rotate(5deg);
  }
  100% {
    border-radius: 40% 60% 30% 70% / 50% 60% 30% 60%;
    transform: rotate(0deg);
  }
}

/* 改进section标题 */
.section-header {
  text-align: center;
  margin-bottom: 60px;
  position: relative;
  z-index: 1;
}

.section-title-decoration {
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  margin: 0 auto 25px;
  border-radius: 2px;
  position: relative;
}

.section-title-decoration::before,
.section-title-decoration::after {
  content: '';
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  top: -1px;
  background: #409EFF;
}

.section-title-decoration::before {
  left: -3px;
}

.section-title-decoration::after {
  right: -3px;
  background: #67C23A;
}

.section-header h2 {
  font-size: 36px;
  color: #2c3e50;
  margin-bottom: 20px;
  position: relative;
}

.section-header p {
  color: #666;
  font-size: 18px;
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto;
}

/* 改进功能卡片设计 */
.feature-cards {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.feature-card {
  background: #fff;
  border-radius: 16px;
  padding: 35px 30px;
  width: 300px;
  text-align: center;
  transition: all 0.7s cubic-bezier(0.23, 1, 0.32, 1);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.08);
  opacity: 0;
  pointer-events: none;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.feature-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: rgba(64, 158, 255, 0.2);
}

.card-highlight {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.feature-card:hover .card-highlight {
  opacity: 1;
}

.feature-icon {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1) 0%, rgba(103, 194, 58, 0.1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 30px;
  position: relative;
  transition: all 0.3s ease;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2) 0%, rgba(103, 194, 58, 0.2) 100%);
}

.feature-card h3 {
  font-size: 24px;
  color: #2c3e50;
  margin-bottom: 25px;
  transition: color 0.3s ease;
  text-align: center;
}

.feature-card:hover h3 {
  color: #409EFF;
}

.feature-list {
  list-style: none;
  padding: 0 10px;
  margin: 0 0 35px;
  text-align: left;
}

.feature-list li {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  color: #666;
  position: relative;
  padding-left: 10px;
  transition: transform 0.3s ease, color 0.3s ease;
}

.feature-card:hover .feature-list li {
  transform: translateX(5px);
  color: #444;
}

.feature-list li i {
  color: #67C23A;
  margin-right: 10px;
  transition: transform 0.3s ease;
}

.feature-card:hover .feature-list li i {
  transform: scale(1.2);
}

.feature-action {
  margin-top: 30px;
  text-align: center;
}

.action-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 22px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.action-button::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: -100%;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0));
  transition: left 0.5s ease;
}

.feature-card:hover .action-button::after {
  left: 100%;
}

.solutions-section {
  min-height: auto;
  padding: 80px 20px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto 80px;
  position: relative;
}

/* 解决方案区域的装饰元素 */
.solutions-decoration {
  position: absolute;
  z-index: 0;
  pointer-events: none;
}

.solutions-decoration.wave-line {
  width: 100%;
  height: 50px;
  background: linear-gradient(90deg, 
    rgba(64, 158, 255, 0) 0%, 
    rgba(64, 158, 255, 0.1) 20%, 
    rgba(103, 194, 58, 0.1) 80%, 
    rgba(103, 194, 58, 0) 100%);
  top: -25px;
  left: 0;
  filter: blur(20px);
  transform: scaleX(0.8);
}

.solutions-decoration.dots-grid {
  width: 150px;
  height: 150px;
  background-image: 
    radial-gradient(rgba(64, 158, 255, 0.15) 1px, transparent 1px),
    radial-gradient(rgba(103, 194, 58, 0.1) 1px, transparent 1px);
  background-size: 15px 15px, 30px 30px;
  background-position: 0 0, 15px 15px;
  bottom: -50px;
  right: -20px;
  opacity: 0.5;
  transform: rotate(-10deg);
}

.solution-item {
  padding: 35px;
  background: #fff;
  border-radius: 16px;
  position: relative;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.7s cubic-bezier(0.23, 1, 0.32, 1);
  z-index: 1;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  opacity: 0;
  pointer-events: none;
}

.solution-item.in-view {
  opacity: 1;
  transform: translate(0) !important;
  pointer-events: auto;
  /* 入场动画完成后，重置过渡时间，让悬浮效果更快速响应 */
  transition: opacity 0.7s cubic-bezier(0.23, 1, 0.32, 1),
              transform 0.7s cubic-bezier(0.23, 1, 0.32, 1),
              box-shadow 0.3s ease,
              border-color 0.3s ease;
}

.solution-item:hover {
  transform: translateY(-10px) !important;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: rgba(64, 158, 255, 0.2);
  /* 为悬浮效果单独设置更短的过渡时间 */
  transition: transform 0.3s ease, 
              box-shadow 0.3s ease,
              border-color 0.3s ease !important;
}

/* 解决方案卡片的飞入效果 */
.solution-item.fly-in-bottom {
  transform: translateY(100px);
}

/* 移除延迟效果，让每个卡片独立触发 */
.solution-item {
  transition-duration: 0.5s;
  transition-timing-function: cubic-bezier(0.23, 1, 0.32, 1);
}

/* 为每个卡片设置不同的初始位置，增强错开效果 */
.solution-1.fly-in-bottom {
  transform: translateY(100px);
}
.solution-2.fly-in-bottom {
  transform: translateY(120px);
}
.solution-3.fly-in-bottom {
  transform: translateY(140px);
}
.solution-4.fly-in-bottom {
  transform: translateY(160px);
}

.solution-highlight {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 3px;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  transition: width 0.3s ease; /* 从默认的0.3s保持不变，确保响应迅速 */
}

.solution-item:hover .solution-highlight {
  width: 100%;
}

.solution-icon {
  position: relative;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1) 0%, rgba(103, 194, 58, 0.1) 100%);
  color: #409EFF;
  font-size: 28px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.solution-item:hover .solution-icon {
  transform: scale(1.1) rotate(5deg);
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2) 0%, rgba(103, 194, 58, 0.2) 100%);
  color: #2c3e50;
  transition: all 0.3s ease; /* 确保图标的变换效果响应迅速 */
}

.solution-item h3 {
  font-size: 24px;
  color: #2c3e50;
  margin-bottom: 15px;
  position: relative;
  z-index: 1;
  transition: color 0.3s ease;
}

.solution-item:hover h3 {
  color: #409EFF;
  transition: color 0.3s ease; /* 确保标题颜色变化响应迅速 */
}

.solution-item p {
  color: #666;
  line-height: 1.6;
  position: relative;
  z-index: 1;
  transition: color 0.3s ease;
}

.solution-item:hover p {
  color: #444;
  transition: color 0.3s ease; /* 确保段落文本颜色变化响应迅速 */
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
  position: relative;
  z-index: 1;
}

.main-heading::after {
  content: '';
  position: absolute;
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  bottom: -12px;
  left: 0;
  border-radius: 2px;
}

/* 新的优势圆圈布局样式 */
.advantages-container {
  position: relative;
  width: 100%;
  height: 350px; /* 增加高度以适应上移的元素 */
  margin-top: 60px; /* 增加顶部边距 */
}

.advantage-item {
  position: absolute;
  text-align: center;
  opacity: 0;
}

.advantage-icon {
  border-radius: 50%;
  background: #fff !important;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 10px 20px rgba(0,0,0,0.05);
  position: relative;
}

.advantage-item-1 {
  right: 65%;
  top: 10%;
  animation: fadeInAdvantage1 0.7s ease forwards, floatItem1 6s ease-in-out infinite alternate;
  animation-delay: 0.1s, 0.8s;
}

.advantage-item-2 {
  right: 15%;
  top: -30%;
  animation: fadeInAdvantage2 0.7s ease forwards, floatItem2 7s ease-in-out infinite alternate;
  animation-delay: 0.4s, 1.1s;
}

.advantage-item-3 {
  right: 40%;
  top: 35%;
  animation: fadeInAdvantage3 0.7s ease forwards, floatItem3 5s ease-in-out infinite alternate;
  animation-delay: 0.7s, 1.4s;
}

@keyframes fadeInAdvantage1 {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes fadeInAdvantage2 {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes fadeInAdvantage3 {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 不同大小的圆圈 - 放大尺寸 */
.advantage-item-1 .advantage-icon {
  width: 140px;
  height: 140px;
}

.advantage-item-2 .advantage-icon {
  width: 130px;
  height: 130px;
}

.advantage-item-3 .advantage-icon {
  width: 100px;
  height: 100px;
}

.advantage-icon::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(64, 158, 255, 0.05);
  border-radius: 50%;
  transform: scale(1.2);
  z-index: -1;
}

.advantage-icon .emoji-icon {
  line-height: 1;
}

/* 不同大小的emoji图标 - 放大尺寸 */
.advantage-item-1 .emoji-icon {
  font-size: 82px;
  display: inline-block;
  position: relative;
  z-index: 2;
}

.gear-wrapper {
  animation: gearRotate 4s linear infinite;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.advantage-item-2 .emoji-icon {
  font-size: 62px;
  animation: dataJump 2s ease-in-out infinite;
  display: inline-block;
}

.advantage-item-3 .emoji-icon {
  font-size: 45px;
  animation: robotBounce 1.5s ease infinite;
  display: inline-block;
}

@keyframes gearRotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dataJump {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-5px) scale(1.04);
  }
}

@keyframes robotBounce {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-5px) scale(1.05);
  }
}

@keyframes floatItem1 {
  0%, 100% {
    transform: translateY(0) translateX(0);
  }
  50% {
    transform: translateY(-25px) translateX(15px);
  }
}

@keyframes floatItem2 {
  0%, 100% {
    transform: translateY(0) translateX(0);
  }
  50% {
    transform: translateY(25px) translateX(-15px);
  }
}

@keyframes floatItem3 {
  0%, 100% {
    transform: translateY(0) translateX(0) scale(1);
  }
  50% {
    transform: translateY(-30px) translateX(-20px) scale(1.05);
  }
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

/* 移动端适配 */
@media (max-width: 768px) {
  .advantages-container {
    height: 500px;
    position: relative;
    margin-top: 70px;
  }
  
  .advantage-item-1 {
    right: auto;
    left: 5%;
    top: 0;
  }
  
  .advantage-item-2 {
    right: 5%;
    top: -10%;
  }
  
  .advantage-item-3 {
    right: auto;
    left: 35%;
    top: 60%;
  }
  
  .advantage-item-1 .advantage-icon {
    width: 110px;
    height: 110px;
  }
  
  .advantage-item-2 .advantage-icon {
    width: 100px;
    height: 100px;
  }
  
  .advantage-item-3 .advantage-icon {
    width: 85px;
    height: 85px;
  }
  
  .hero-section {
    min-height: 110vh; /* 移动端增加高度以容纳新布局 */
  }
}

@media (max-width: 1200px) {
  .feature-cards {
    justify-content: center;
  }
  
  .feature-card {
    width: calc(50% - 30px);
    min-width: 280px;
  }
  
  .solutions-section {
    grid-template-columns: repeat(2, 1fr);
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
    padding: 60px 20px;
    margin-bottom: 60px;
  }
  
  .features-section {
    padding: 40px 20px; /* 移动端更紧凑 */
  }
  
  .hero-decoration.dot-grid {
    width: 150px;
    height: 150px;
    left: 5%;
    bottom: 10%;
  }
  
  .hero-decoration.circle {
    width: 80px;
    height: 80px;
    left: 10%;
    top: 15%;
  }
  
  .hero-decoration.square {
    width: 60px;
    height: 60px;
    right: 10%;
    bottom: 15%;
  }
  
  .hero-decoration.triangle {
    border-left: 30px solid transparent;
    border-right: 30px solid transparent;
    border-bottom: 50px solid rgba(245, 108, 108, 0.05);
    left: 25%;
    top: 65%;
  }
  
  .hero-decoration.wave {
    width: 100px;
    height: 40px;
    right: 8%;
    top: 25%;
  }
  
  .solution-item {
    padding: 25px;
  }
  
  .solution-icon {
    width: 50px;
    height: 50px;
    font-size: 22px;
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
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #409EFF 0%, #67C23A 100%);
  border-radius: 50%;
  box-shadow: 0 5px 15px rgba(64, 158, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: bounce 2s infinite;
  z-index: 100;
}

.scroll-indicator:hover {
  transform: translateX(-50%) scale(1.1);
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.5);
}

.scroll-emoji {
  font-size: 24px;
  line-height: 1;
  color: white;
}

@media (max-width: 768px) {
  .home-container::-webkit-scrollbar {
    width: 4px;
  }
  
  .scroll-indicator {
    width: 50px;
    height: 50px;
    bottom: 20px;
  }
  
  .scroll-emoji {
    font-size: 20px;
  }
}

/* 确保动画在低性能设备上不会造成性能问题 */
@media (prefers-reduced-motion: reduce) {
  .hero-section::after,
  .hero-decoration {
    animation: none !important;
  }
  
  .solutions-decoration,
  .scroll-indicator {
    animation: none !important;
  }
  
  .solution-item:hover,
  .solution-item:hover .solution-icon,
  .feature-card:hover {
    transform: none !important;
  }
}

.feature-card:nth-child(1) {
  transition-delay: 0.1s;
}

.feature-card:nth-child(2) {
  transition-delay: 0.3s;
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

.emoji-icon {
  font-size: 40px;
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
</style>