<template>
  <div class="order-manager">
    <div v-if="!loginUser" class="login-tip">
      <el-empty description="请先登录以查看您的订单" :image-size="180" />
      <el-button type="primary" @click="goLogin">去登录</el-button>
    </div>
    <template v-else>
      <div class="order-header">
        <!-- 標題與上方搜尋欄已移除 -->
      </div>

      <div class="filter-bar">
        <el-radio-group v-model="orderStatus" size="medium">
          <el-radio-button label="all">全部订单</el-radio-button>
          <el-radio-button label="PENDING_PAYMENT">待付款</el-radio-button>
          <el-radio-button label="PAID">处理中</el-radio-button>
          <el-radio-button label="DELIVERED">已发货</el-radio-button>
          <el-radio-button label="FINISH">已完成</el-radio-button>
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
        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索订单编号/商品名称"
            prefix-icon="el-icon-search"
            clearable
          />
          <el-button type="primary" class="search-btn" @click="handleSearch">搜索</el-button>
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
          
          <div class="order-address" v-if="order.shippingAddress">
            <i class="el-icon-location"></i>
            <span>收货地址: {{ order.shippingAddress }}</span>
          </div>
          
          <div class="order-bottom">
            <div class="order-logistics">
              <i class="el-icon-truck"></i>
              <span>物流状态: {{ getStatusText(order.status) }}</span>
              <span class="logistics-company">{{ order.logistics.company }}</span>
              <span class="logistics-number">运单号: {{ order.logistics.trackingNumber }}</span>
            </div>
            <div class="order-actions">
              <el-button size="small" v-if="order.status === 'DELIVERED'">确认收货</el-button>
            </div>
            <div class="order-amount order-amount-fixed">
              <span>共{{ getTotalQuantity(order) }}件商品</span>
              <span class="amount">合计: <strong>¥{{ getTotalAmount(order).toFixed(2) }}</strong></span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 创建订单对话框 -->
      <el-dialog
        title="创建新订单"
        :visible.sync="createOrderDialogVisible"
        width="50%"
        :before-close="handleCloseDialog"
      >
        <el-form :model="newOrderForm" label-width="120px" :rules="orderFormRules" ref="orderForm">
          <el-form-item label="用户ID" prop="userId">
            <el-input v-model.number="newOrderForm.userId" type="number"></el-input>
          </el-form-item>
          
          <el-form-item label="收货地址" prop="shippingAddress">
            <el-input v-model="newOrderForm.shippingAddress" type="textarea" :rows="2"></el-input>
          </el-form-item>
          
          <el-form-item label="商品" prop="products">
            <div v-for="(product, index) in newOrderForm.products" :key="index" class="product-form-item">
              <el-row :gutter="10">
                <el-col :span="6">
                  <el-form-item :prop="`products.${index}.productId`" :rules="{ required: true, message: '请输入商品ID', trigger: 'blur' }">
                    <el-input v-model="product.productId" placeholder="商品ID"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item :prop="`products.${index}.productName`" :rules="{ required: true, message: '请输入商品名称', trigger: 'blur' }">
                    <el-input v-model="product.productName" placeholder="商品名称"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="4">
                  <el-form-item :prop="`products.${index}.quantity`" :rules="{ required: true, type: 'number', min: 1, message: '数量必须大于0', trigger: 'blur' }">
                    <el-input-number v-model="product.quantity" :min="1" placeholder="数量"></el-input-number>
                  </el-form-item>
                </el-col>
                <el-col :span="4">
                  <el-form-item :prop="`products.${index}.unitPrice`" :rules="{ required: true, type: 'number', min: 0.01, message: '价格必须大于0', trigger: 'blur' }">
                    <el-input-number v-model="product.unitPrice" :min="0.01" :precision="2" placeholder="单价"></el-input-number>
                  </el-form-item>
                </el-col>
                <el-col :span="4">
                  <el-button type="danger" icon="el-icon-delete" circle @click="removeProduct(index)" v-if="newOrderForm.products.length > 1"></el-button>
                </el-col>
              </el-row>
            </div>
            
            <div class="add-product-btn">
              <el-button type="primary" icon="el-icon-plus" @click="addProduct">添加商品</el-button>
            </div>
          </el-form-item>
          
          <el-form-item label="总金额">
            <span class="calculated-amount">¥{{ calculateNewOrderAmount() }}</span>
          </el-form-item>
        </el-form>
        
        <span slot="footer" class="dialog-footer">
          <el-button @click="handleCloseDialog">取消</el-button>
          <el-button type="primary" @click="submitNewOrder" :loading="submitting">确定</el-button>
        </span>
      </el-dialog>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, getCurrentInstance } from 'vue'
import orderService from '../services/orderService'
import orderModel from '../services/orderModel'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter ? useRouter() : null
const searchKeyword = ref('')
const searchActionKeyword = ref('')
const orderStatus = ref('all')
const dateRange = ref([])
const loading = ref(false)
const submitting = ref(false)
const createOrderDialogVisible = ref(false)

// 登入用戶
const loginUser = ref(null)
if (localStorage.getItem('loginUser')) {
  try {
    loginUser.value = JSON.parse(localStorage.getItem('loginUser'))
  } catch (e) {
    loginUser.value = null
  }
}

const instance = getCurrentInstance()

const goLogin = () => {
  // 若有 router，則跳轉，否則 emit 事件讓父組件切換 currentPage
  if (router) {
    router.push('/login')
  } else if (instance && instance.emit) {
    instance.emit('goLogin')
  }
}

// 订单表单相关
const orderForm = ref(null)
const newOrderForm = reactive({
  userId: 551,
  shippingAddress: '',
  products: [
    {
      productId: '',
      productName: '',
      quantity: 1,
      unitPrice: 0
    }
  ]
})

// 表单验证规则
const orderFormRules = {
  userId: [
    { required: true, message: '请输入用户ID', trigger: 'blur' },
    { type: 'number', message: '用户ID必须为数字', trigger: 'blur' }
  ],
  shippingAddress: [
    { required: true, message: '请输入收货地址', trigger: 'blur' }
  ]
}

// 添加商品
const addProduct = () => {
  newOrderForm.products.push({
    productId: '',
    productName: '',
    quantity: 1,
    unitPrice: 0
  })
}

// 移除商品
const removeProduct = (index) => {
  newOrderForm.products.splice(index, 1)
}

// 计算新订单总金额
const calculateNewOrderAmount = () => {
  return newOrderForm.products.reduce((sum, product) => {
    return sum + (product.quantity || 0) * (product.unitPrice || 0)
  }, 0).toFixed(2)
}

// 显示创建订单对话框
const showCreateOrderDialog = () => {
  createOrderDialogVisible.value = true
}

// 关闭对话框
const handleCloseDialog = () => {
  createOrderDialogVisible.value = false
  // 重置表单
  if (orderForm.value) {
    orderForm.value.resetFields()
  }
  // 重置商品列表
  newOrderForm.products = [
    {
      productId: '',
      productName: '',
      quantity: 1,
      unitPrice: 0
    }
  ]
}

// 提交新订单
const submitNewOrder = async () => {
  if (orderForm.value) {
    orderForm.value.validate(async (valid) => {
      if (valid) {
        submitting.value = true
        try {
          // 创建订单数据
          const orderData = {
            userId: newOrderForm.userId,
            shippingAddress: newOrderForm.shippingAddress,
            products: newOrderForm.products.map(p => ({
              id: p.productId,
              name: p.productName,
              quantity: p.quantity,
              price: p.unitPrice
            }))
          }
          
          await orderService.createOrder(orderData)
          createOrderDialogVisible.value = false
          // 重新加载订单列表
          fetchOrders()
        } catch (error) {
          console.error('创建订单失败:', error)
        } finally {
          submitting.value = false
        }
      }
    })
  }
}

// 订单数据
const orders = ref([])

// 获取订单列表
const fetchOrders = async () => {
  if (!loginUser.value) return
  loading.value = true
  try {
    orders.value = (await orderService.getOrders()).filter(o => o.userId == loginUser.value.userID)
    ElMessage.success({ message: '订单数据读取成功', duration: 1000 })
  } catch (e) {
    ElMessage.error({ message: '订单数据读取失败', duration: 1000 })
  } finally {
    loading.value = false
  }
}

// 初始加载
onMounted(() => {
  if (loginUser.value) fetchOrders()
})

// 根据筛选条件过滤订单
const filteredOrders = computed(() => {
  let result = orders.value
  result = orderService.filterOrdersByStatus(result, orderStatus.value)
  // 用searchActionKeyword进行搜索
  result = orderService.searchOrders(result, searchActionKeyword.value)
  result = orderService.filterOrdersByDateRange(result, dateRange.value)
  return result
})

// 获取订单状态对应的Tag类型
const getStatusType = (status) => {
  switch (status) {
    case 'PENDING_PAYMENT':
      return 'info'
    case 'PAID':
      return 'warning'
    case 'DELIVERED':
      return 'success'
    case 'FINISH':
      return 'success'
    default:
      return 'info'
  }
}

// 获取订单状态的中文描述
const getStatusText = (status) => {
  switch (status) {
    case 'PENDING_PAYMENT':
      return '待付款'
    case 'PAID':
      return '处理中'
    case 'DELIVERED':
      return '已发货'
    case 'FINISH':
      return '已完成'
    default:
      return status
  }
}

// 计算订单商品总数
const getTotalQuantity = (order) => {
  return orderService.calculateTotalQuantity(order)
}

// 计算订单总金额
const getTotalAmount = (order) => {
  return orderService.calculateTotalAmount(order)
}

// 搜索按钮点击事件
const handleSearch = () => {
  searchActionKeyword.value = searchKeyword.value
}
</script>

<style scoped>
html, body, #app {
  margin: 0 !important;
  padding: 0 !important;
}

.user-id {
  color: #409EFF;
  font-weight: bold;
  margin-left: 16px;
}

.loading-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.order-manager {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  min-height: 100vh;
  width: 100vw;
  overflow-y: auto;
  background: #f5f7fa;
  padding-top: 0 !important;
  margin-top: 0 !important;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.order-header h2 {
  font-size: 40px;
  color: #303133;
  margin: 0;
  margin-top: 100px;
}

.search-box {
  display: flex;
  gap: 12px;
}

.search-box .el-input {
  width: 240px;
}

/* CSS 調整 filter-bar 內部排列 */
.filter-bar {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  margin-top: 90px;
}
.filter-bar > .el-radio-group {
  flex: 1 1 0;
  min-width: 220px;
  margin-right: 16px;
}
.date-filter {
  flex: 1 1 0;
  min-width: 240px;
  margin: 0 16px;
  display: flex;
  justify-content: center;
}
.search-box {
  flex: 1 1 0;
  display: flex;
  gap: 8px;
  min-width: 320px;
  margin-left: 16px;
  justify-content: flex-end;
}
@media (max-width: 900px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  .filter-bar > .el-radio-group,
  .date-filter, .search-box {
    margin: 0;
    min-width: 0;
    justify-content: stretch;
  }
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-item {
  border-radius: 8px;
  position: relative;
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

.order-address {
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  gap: 8px;
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

.product-form-item {
  margin-bottom: 15px;
  border-bottom: 1px dashed #ebeef5;
  padding-bottom: 15px;
}

.add-product-btn {
  margin-top: 15px;
}

.calculated-amount {
  font-size: 18px;
  color: #f56c6c;
  font-weight: bold;
}

.login-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

/* 新增右下角固定樣式 */
.order-amount-fixed {
  position: absolute;
  right: 24px;
  bottom: 18px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  z-index: 2;
  background: rgba(255,255,255,0.95);
  border-radius: 8px;
  padding: 8px 16px;
  box-shadow: 0 2px 8px rgba(64,158,255,0.07);
}
</style>