import { orderApi, transformOrderData } from './api';
import orderModel from './orderModel';

/**
 * 订单服务 - 处理订单相关业务逻辑
 */
export const orderService = {
  /**
   * 获取订单列表
   * @returns {Promise<Array>} 处理后的订单列表
   */
  getOrders: async () => {
    try {
      const data = await orderApi.getOrders();
      // 适配后端数据结构，防止字段不符导致报错
      return Array.isArray(data)
        ? data.map(order => orderModel.createOrderModel(order))
        : [orderModel.createOrderModel(data)];
    } catch (error) {
      console.error('获取订单列表失败:', error);
      if (error && error.stack) {
        console.error('详细堆栈:', error.stack);
      }
      throw error;
    }
  },

  /**
   * 创建新订单
   * @param {Object} orderData - 订单数据
   * @returns {Promise} 创建的订单
   */
  createOrder: async (orderData) => {
    try {
      const result = await orderApi.createOrder(orderData);
      return orderModel.createOrderModel(result);
    } catch (error) {
      console.error('创建订单失败:', error);
      throw error;
    }
  },

  /**
   * 根据订单ID获取订单详情
   * @param {string} orderId - 订单ID
   * @returns {Promise<Object>} 处理后的订单详情
   */
  getOrderDetails: async (orderId) => {
    try {
      const data = await orderApi.getOrderDetails(orderId);
      return orderModel.createOrderModel(data);
    } catch (error) {
      console.error(`获取订单 ${orderId} 详情失败:`, error);
      throw error; // 不再返回 mock 数据
    }
  },

  /**
   * 更新订单状态
   * @param {string} orderId - 订单ID
   * @param {string} status - 新状态
   * @returns {Promise<Object>} 更新后的订单
   */
  updateOrderStatus: async (orderId, status) => {
    try {
      const data = await orderApi.updateOrderStatus(orderId, status);
      return orderModel.createOrderModel(data);
    } catch (error) {
      console.error(`更新订单 ${orderId} 状态失败:`, error);
      throw error;
    }
  },

  /**
   * 根据状态过滤订单
   * @param {Array} orders - 订单列表
   * @param {string} status - 状态
   * @returns {Array} 过滤后的订单列表
   */
  filterOrdersByStatus: (orders, status) => {
    if (status === 'all') return orders;
    return orders.filter(order => order.status === status);
  },

  /**
   * 根据关键字搜索订单
   * @param {Array} orders - 订单列表
   * @param {string} keyword - 搜索关键字
   * @returns {Array} 搜索结果
   */
  searchOrders: (orders, keyword) => {
    if (!keyword) return orders;
    
    const lowerKeyword = keyword.toLowerCase();
    return orders.filter(order => {
      // 搜索订单编号
      if (order.id?.toLowerCase().includes(lowerKeyword)) return true;
      
      // 搜索商品名称
      for (const product of (order.products || [])) {
        if (product.name?.toLowerCase().includes(lowerKeyword)) return true;
      }
      
      return false;
    });
  },

  /**
   * 根据日期范围过滤订单
   * @param {Array} orders - 订单列表
   * @param {Array} dateRange - 日期范围 [startDate, endDate]
   * @returns {Array} 过滤后的订单列表
   */
  filterOrdersByDateRange: (orders, dateRange) => {
    if (!dateRange || dateRange.length !== 2) return orders;
    
    const startDate = new Date(dateRange[0]);
    const endDate = new Date(dateRange[1]);
    
    return orders.filter(order => {
      if (!order.date) return false;
      const orderDate = new Date(order.date.split(' ')[0]);
      return orderDate >= startDate && orderDate <= endDate;
    });
  },

  /**
   * 计算订单商品总数量
   * @param {Object} order - 订单
   * @returns {number} 商品总数量
   */
  calculateTotalQuantity: (order) => {
    return (order.products || []).reduce((sum, product) => sum + (product.quantity || 0), 0);
  },

  /**
   * 计算订单总金额
   * @param {Object} order - 订单
   * @returns {number} 订单总金额
   */
  calculateTotalAmount: (order) => {
    return orderModel.calculateTotalAmount(order.products || []);
  },

  /**
   * 获取订单状态对应的标签类型
   * @param {string} status - 订单状态
   * @returns {string} 标签类型
   */
  getStatusType: (status) => {
    switch (status) {
      case 'PENDING_PAYMENT':
        return 'warning';
      case 'PAID':
        return 'info';
      case 'DELIVERED':
        return 'primary';
      case 'FINISH':
        return 'success';
      default:
        return 'default';
    }
  },

  /**
   * 获取订单状态的中文描述
   * @param {string} status - 订单状态
   * @returns {string} 中文描述
   */
  getStatusText: (status) => {
    switch (status) {
      case 'PENDING_PAYMENT':
        return '待付款';
      case 'PAID':
        return '处理中';
      case 'DELIVERED':
        return '已发货';
      case 'FINISH':
        return '已完成';
      default:
        return status;
    }
  }
};

export default orderService;