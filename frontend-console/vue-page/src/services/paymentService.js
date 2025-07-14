import axios from 'axios';

/**
 * 支付服务 - 负责与支付API通信
 */

// 创建API客户端实例
const apiClient = axios.create({
  baseURL: 'http://10.172.66.224:8084/payment/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// 请求拦截器添加认证信息
apiClient.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const loginUser = localStorage.getItem('loginUser');
    if (loginUser) {
      try {
        const user = JSON.parse(loginUser);
        if (user.token) {
          config.headers.Authorization = `Bearer ${user.token}`;
        }
      } catch (e) {
        console.error('解析用户信息出错', e);
      }
    }
    return config;
  },
  error => Promise.reject(error)
);

// 支付服务
const paymentService = {
  /**
   * 获取所有支付记录
   * @returns {Promise} 支付记录列表
   */
  getAllPayments: async () => {
    try {
      const response = await apiClient.get('/payments');
      return response.data;
    } catch (error) {
      console.error('获取支付记录失败:', error);
      throw {
        message: '获取支付记录失败，请稍后再试',
        originalError: error
      };
    }
  },
  
  /**
   * 根据ID获取支付记录
   * @param {string} paymentId - 支付ID
   * @returns {Promise} 支付记录详情
   */
  getPaymentById: async (paymentId) => {
    try {
      const response = await apiClient.get(`/payments/${paymentId}`);
      return response.data;
    } catch (error) {
      console.error(`获取支付记录 ${paymentId} 失败:`, error);
      throw {
        message: '获取支付记录失败，请稍后再试',
        originalError: error
      };
    }
  },
  
  /**
   * 根据订单ID获取支付记录
   * @param {string} orderId - 订单ID
   * @returns {Promise} 支付记录详情
   */
  getPaymentByOrderId: async (orderId) => {
    try {
      const response = await apiClient.get(`/payments/order/${orderId}`);
      return response.data;
    } catch (error) {
      console.error(`获取订单 ${orderId} 的支付记录失败:`, error);
      throw {
        message: '获取支付记录失败，请稍后再试',
        originalError: error
      };
    }
  },
  
  /**
   * 创建支付记录
   * @param {Object} paymentData - 支付数据
   * @returns {Promise} 创建的支付记录
   */
  createPayment: async (paymentData) => {
    try {
      const response = await apiClient.post('/payments', paymentData);
      return response.data;
    } catch (error) {
      console.error('创建支付记录失败:', error);
      throw {
        message: '创建支付记录失败，请稍后再试',
        originalError: error
      };
    }
  },
  
  /**
   * 更新支付状态
   * @param {string} paymentId - 支付ID
   * @param {string} status - 新状态
   * @returns {Promise} 更新后的支付记录
   */
  updatePaymentStatus: async (paymentId, status) => {
    try {
      const response = await apiClient.put(`/payments/${paymentId}/status`, { status });
      return response.data;
    } catch (error) {
      console.error(`更新支付记录 ${paymentId} 状态失败:`, error);
      throw {
        message: '更新支付状态失败，请稍后再试',
        originalError: error
      };
    }
  },
  
  /**
   * 获取模拟支付数据（开发测试用）
   * @returns {Object} 模拟支付数据
   */
  getMockPaymentData: () => {
    return {
      id: '1ee9e569-db88-4846-99a0-5b5248245d80',
      orderId: 'ORD_TEST_001',
      userId: 'USER_001',
      amount: 99.99,
      status: 'PENDING',
      createAt: '2025-07-08T16:14:31.7168652',
      updateAt: '2025-07-08T16:14:31.7178644',
      // 为了兼容现有UI，添加一些额外信息
      method: 'alipay',
      transactionId: '202306151432156789123456',
      productDetails: {
        name: '智能音箱 Pro',
        quantity: 1,
        unitPrice: 99.99
      }
    };
  }
};

export default paymentService; 