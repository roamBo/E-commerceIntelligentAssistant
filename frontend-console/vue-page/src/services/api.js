import axios from 'axios';
import orderModel from './orderModel';

// API 基础 URL
const API_BASE_URL = 'http://10.172.66.224:8084/order/api';

/**
 * 订单服务 API
 */
export const orderApi = {
  /**
   * 获取订单列表
   * @returns {Promise} 订单列表
   */
  getOrders: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/orders`);
      return response.data;
    } catch (error) {
      console.error('获取订单列表失败:', error);
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
      // 将前端订单数据转换为后端所需格式
      const requestData = orderModel.createOrderRequestData(orderData);
      const response = await axios.post(`${API_BASE_URL}/orders`, requestData);
      return response.data;
    } catch (error) {
      console.error('创建订单失败:', error);
      throw error;
    }
  },

  /**
   * 获取订单详情
   * @param {string} orderId - 订单ID
   * @returns {Promise} 订单详情
   */
  getOrderDetails: async (orderId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/orders/${orderId}`);
      return response.data;
    } catch (error) {
      console.error(`获取订单 ${orderId} 详情失败:`, error);
      throw error;
    }
  },

  /**
   * 更新订单状态
   * @param {string} orderId - 订单ID
   * @param {string} status - 新状态
   * @returns {Promise} 更新后的订单
   */
  updateOrderStatus: async (orderId, status) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/orders/${orderId}/status`, { status });
      return response.data;
    } catch (error) {
      console.error(`更新订单 ${orderId} 状态失败:`, error);
      throw error;
    }
  }
};

/**
 * 将后端订单数据转换为前端显示格式
 * @param {Array} orders - 后端订单数据
 * @returns {Array} 前端格式的订单数据
 */
export const transformOrderData = (orders) => {
  if (!Array.isArray(orders)) {
    orders = [orders]; // 如果不是数组，转换为数组处理
  }

  return orders.map(order => orderModel.createOrderModel(order));
};

/**
 * 获取模拟订单数据
 * @returns {Array} 模拟订单数据
 */
export const getMockOrderData = () => {
  return [
    orderModel.createOrderModel({
      id: 'ORD-10001',
      userId: 551,
      date: '2023-11-01 14:30:22',
      status: 'pending',
      products: [
        {
          id: 'P-007',
          name: '无线鼠标',
          price: 50.00,
          quantity: 2,
          image: 'https://picsum.photos/id/1/200/200',
          attrs: '黑色'
        }
      ],
      logistics: {
        status: '待发货',
        company: '顺丰速运',
        trackingNumber: 'SF123456789'
      },
      shippingAddress: '上海市浦东新区陆家嘴'
    }),
    orderModel.createOrderModel({
      id: 'ORD-10002',
      userId: 551,
      date: '2023-10-25 09:15:37',
      status: 'shipped',
      products: [
        {
          id: 'P-003',
          name: '机械键盘',
          price: 299.00,
          quantity: 1,
          image: 'https://picsum.photos/id/2/200/200',
          attrs: '青轴'
        },
        {
          id: 'P-008',
          name: '鼠标垫',
          price: 20.00,
          quantity: 1,
          image: 'https://picsum.photos/id/3/200/200',
          attrs: '大号'
        }
      ],
      logistics: {
        status: '运输中',
        company: '中通快递',
        trackingNumber: 'ZT987654321'
      },
      shippingAddress: '北京市朝阳区国贸'
    })
  ];
};

/**
 * 用戶服務 API
 */
export const userApi = {
  /**
   * 登入
   * @param {string} username
   * @param {string} password
   * @returns {Promise} 用戶資料或錯誤
   */
  login: async (username, password) => {
    try {
      const response = await axios.get('http://10.172.141.46:3000/api/users');
      const users = response.data;
      const user = users.find(
        u => u.username === username && u.userpassword === password
      );
      if (!user) {
        throw new Error('用戶名或密碼錯誤');
      }
      return user;
    } catch (error) {
      throw error;
    }
  },
  /**
   * 註冊
   * @param {string} username
   * @param {string} password
   * @param {string} email
   * @returns {Promise} 新用戶資料或錯誤
   */
  register: async (username, password, email) => {
    try {
      const response = await axios.post('http://10.172.141.46:3000/api/register', {
        username,
        password,
        email
      });
      return response.data.user;
    } catch (error) {
      throw error.response?.data || error;
    }
  }
};

export default {
  orderApi,
  transformOrderData,
  getMockOrderData,
  userApi // 新增這行
}; 