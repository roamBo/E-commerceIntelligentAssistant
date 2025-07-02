<template>
  <div class="order-manager">
    <div class="order-header">
      <h2>订单智能管家</h2>
      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索订单编号/商品名称"
          prefix-icon="el-icon-search"
          clearable
        />
        <el-button type="primary" class="search-btn">搜索</el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-radio-group v-model="orderStatus" size="medium">
        <el-radio-button label="all">全部订单</el-radio-button>
        <el-radio-button label="pending">待付款</el-radio-button>
        <el-radio-button label="processing">处理中</el-radio-button>
        <el-radio-button label="shipped">已发货</el-radio-button>
        <el-radio-button label="completed">已完成</el-radio-button>
      </el-radio-group>
      
      <div class="date-filter">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          size="medium"
        />
      </div>
    </div>
    
    <div class="order-list">
      <el-empty 
        v-if="filteredOrders.length === 0 && !loading" 
        description="暂无订单数据" 
        :image-size="200">
      </el-empty>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
        <el-skeleton :rows="3" animated style="margin-top: 20px;" />
      </div>
      
      <el-card v-for="order in filteredOrders" :key="order.id" class="order-item" shadow="hover">
        <div class="order-top">
          <div class="order-info">
            <span class="order-id">订单编号: {{ order.id }}</span>
            <span class="order-date">下单时间: {{ order.date }}</span>
          </div>
          <div class="order-status">
            <el-tag :type="getStatusType(order.status)">{{ getStatusText(order.status) }}</el-tag>
          </div>
        </div>
        
        <div class="order-products">
          <div v-for="product in order.products" :key="product.id" class="product-item">
            <div class="product-img">
              <img :src="product.image" :alt="product.name">
            </div>
            <div class="product-info">
              <div class="product-name">{{ product.name }}</div>
              <div class="product-attrs">{{ product.attrs }}</div>
              <div class="product-price">¥{{ product.price.toFixed(2) }} × {{ product.quantity }}</div>
            </div>
          </div>
        </div>
        
        <div class="order-bottom">
          <div class="order-logistics">
            <i class="el-icon-truck"></i>
            <span>物流状态: {{ order.logistics.status }}</span>
            <span class="logistics-company">{{ order.logistics.company }}</span>
            <span class="logistics-number">运单号: {{ order.logistics.trackingNumber }}</span>
          </div>
          <div class="order-amount">
            <span>共{{ getTotalQuantity(order) }}件商品</span>
            <span class="amount">合计: <strong>¥{{ getTotalAmount(order).toFixed(2) }}</strong></span>
          </div>
          <div class="order-actions">
            <el-button size="small" v-if="order.status === 'pending'">付款</el-button>
            <el-button size="small" v-if="order.status === 'shipped'">确认收货</el-button>
            <el-button size="small" type="info" plain>查看详情</el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const searchKeyword = ref('')
const orderStatus = ref('all')
const dateRange = ref([])
const loading = ref(false)

// 真实订单数据应通过API获取
const orders = ref([])

// 模拟API加载
const loadOrders = () => {
  loading.value = true
  // 这里应该是实际的API调用
  setTimeout(() => {
    loading.value = false
    // 数据将由实际API填充
  }, 800)
}

// 初始加载
loadOrders()

// 根据筛选条件过滤订单
const filteredOrders = computed(() => {
  let result = orders.value

  // 根据订单状态筛选
  if (orderStatus.value !== 'all') {
    result = result.filter(order => order.status === orderStatus.value)
  }

  // 根据关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(order => {
      // 搜索订单编号
      if (order.id?.toLowerCase().includes(keyword)) return true
      
      // 搜索商品名称
      for (const product of (order.products || [])) {
        if (product.name?.toLowerCase().includes(keyword)) return true
      }
      
      return false
    })
  }

  // 根据日期范围筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    
    result = result.filter(order => {
      if (!order.date) return false
      const orderDate = new Date(order.date.split(' ')[0])
      return orderDate >= startDate && orderDate <= endDate
    })
  }

  return result
})

// 获取订单状态对应的Tag类型
const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    processing: 'info',
    shipped: 'primary',
    completed: 'success'
  }
  return types[status] || 'info'
}

// 获取订单状态的中文描述
const getStatusText = (status) => {
  const texts = {
    pending: '待付款',
    processing: '处理中',
    shipped: '已发货',
    completed: '已完成'
  }
  return texts[status] || status
}

// 计算订单商品总数量
const getTotalQuantity = (order) => {
  return (order.products || []).reduce((sum, product) => sum + (product.quantity || 0), 0)
}

// 计算订单总金额
const getTotalAmount = (order) => {
  return (order.products || []).reduce((sum, product) => sum + ((product.price || 0) * (product.quantity || 0)), 0)
}
</script>

<style scoped>
.loading-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.order-manager {
  width: 100%;
  height: 100%;
  padding: 24px;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.order-header h2 {
  font-size: 24px;
  color: #303133;
  margin: 0;
}

.search-box {
  display: flex;
  gap: 12px;
}

.search-box .el-input {
  width: 240px;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-item {
  border-radius: 8px;
}

.order-top {
  display: flex;
  justify-content: space-between;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.order-info {
  display: flex;
  gap: 16px;
}

.order-id {
  font-weight: bold;
  color: #303133;
}

.order-date {
  color: #909399;
}

.order-products {
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.product-item {
  display: flex;
  gap: 12px;
}

.product-img {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
}

.product-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  flex: 1;
}

.product-name {
  font-weight: bold;
  margin-bottom: 4px;
}

.product-attrs {
  color: #909399;
  font-size: 13px;
  margin-bottom: 4px;
}

.product-price {
  color: #606266;
}

.order-bottom {
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-logistics {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.logistics-company {
  margin-left: 8px;
}

.logistics-number {
  margin-left: 16px;
}

.order-amount {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.amount {
  color: #303133;
  font-size: 16px;
}

.amount strong {
  color: #f56c6c;
  font-size: 18px;
}

.order-actions {
  display: flex;
  gap: 8px;
}

.filter-controls {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap; /* 允许在小屏幕上换行 */
}

.data-table {
  flex: 1;
  overflow: auto; /* 确保表格内容可滚动 */
}

/* 添加响应式设计 */
@media (max-width: 768px) {
  .order-manager {
    padding: 16px;
  }
  
  .order-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 16px;
  }
  
  .filter-controls {
    width: 100%;
    justify-content: space-between;
  }
  
  .filter-controls .el-select,
  .filter-controls .el-date-picker {
    width: 100% !important;
    margin-bottom: 10px;
  }
  
  .data-table {
    overflow-x: auto; /* 确保表格可以水平滚动 */
  }
  
  /* 调整表格在小屏幕上的显示 */
  :deep(.el-table) {
    width: 100%;
    overflow-x: auto;
  }
  
  :deep(.el-table__body),
  :deep(.el-table__header) {
    min-width: 600px; /* 确保表格有最小宽度 */
  }
}

/* 对于非常小的屏幕 */
@media (max-width: 480px) {
  .order-manager {
    padding: 10px;
  }
  
  .order-header h2 {
    font-size: 20px;
  }
}
</style> 