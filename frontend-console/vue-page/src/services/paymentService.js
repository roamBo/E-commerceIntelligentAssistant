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
   * 根据用户ID获取支付记录
   * @param {string} userId - 用户ID
   * @returns {Promise} 支付记录列表
   */
  getPaymentsByUserId: async (userId) => {
    try {
      const response = await apiClient.get(`/payments/user/${userId}`);
      return response.data;
    } catch (error) {
      console.error(`获取用户 ${userId} 的支付记录失败:`, error);
      throw {
        message: '获取用户支付记录失败，请稍后再试',
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
  },

  /**
   * 轮询检查用户支付状态变化
   * @param {string} userId - 用户ID
   * @param {function} onStatusChange - 状态变化时的回调函数，参数为变化的支付记录
   * @param[object Object]number} interval - 轮询间隔，单位毫秒，默认500ms
   * @returns {Object} - 包含stop方法的控制对象，用于停止轮询
   */
  pollPaymentStatusChanges: (userId, onStatusChange, interval =500) => {
    if (!userId) {
      console.error('轮询支付状态需要用户ID');
      return { stop: () => {}};
    }
    
    console.log(`开始轮询用户 ${userId} 的支付状态变化，间隔 ${interval}ms`);
    
    // 存储上一次的支付记录状态
    let previousPayments = {};
    let timerId = null;
    let isFirstPoll = true;
    let pollCount = 0;
    
    // 执行轮询
    const poll = async () => {
      pollCount++;
      console.log(`执行第 ${pollCount} 次轮询检查，用户ID: ${userId}`);
      
      try {
        // 直接使用API调用获取支付记录
        console.log(`请求URL: http://10.172.66.224:8084/payment/api/payments/user/${userId}`);
        const response = await fetch(`http://10.172.66.224:8084/payment/api/payments/user/${userId}`);
        if (!response.ok) {
          throw new Error(`API返回错误状态码: ${response.status}`);
        }
        
        const payments = await response.json();
        console.log(`获取到 ${payments.length} 条支付记录:`, payments);
        
        if (isFirstPoll) {
          // 首次轮询，记录所有支付状态
          console.log('首次轮询，记录初始状态');
          payments.forEach(payment => {
            previousPayments[payment.id] = payment.status;
            console.log(`记录支付 ${payment.id} 初始状态: ${payment.status}`);
          });
          isFirstPoll = false;
        } else {
          // 检查状态变化
          let hasStatusChange = false;
          
          payments.forEach(payment => {
            const prevStatus = previousPayments[payment.id];
            const currentStatus = payment.status;
            
            console.log(`检查支付记录 ${payment.id}: 之前状态=${prevStatus}, 当前状态=${currentStatus}`);
            
            // 如果是新支付记录或状态发生变化
            if (prevStatus === undefined || prevStatus !== currentStatus) {
              hasStatusChange = true;
              console.log(`支付记录 ${payment.id} 状态变化: ${prevStatus || '新记录'} -> ${currentStatus}`);
              
              // 特别检查从PENDING到SUCCESS的变化
              if ((prevStatus === 'PENDING' || prevStatus === 'pending') && 
                  (currentStatus === 'SUCCESS' || currentStatus === 'success')) {
                console.log(`检测到支付记录 ${payment.id} 从未支付变为已支付状态`);
                // 调用回调函数
                onStatusChange(payment, 'PENDING_TO_SUCCESS');
              } else if (prevStatus === undefined) {
                // 新支付记录
                console.log(`检测到新支付记录: ${payment.id}, 状态: ${currentStatus}`);
                onStatusChange(payment, 'NEW_PAYMENT');
              } else if (prevStatus !== currentStatus) {
                // 其他状态变化
                console.log(`检测到支付状态变化: ${prevStatus} -> ${currentStatus}`);
                onStatusChange(payment, 'STATUS_CHANGED');
              }
            }
            
            // 更新状态记录
            previousPayments[payment.id] = currentStatus;
          });
          
          if (!hasStatusChange) {
            console.log('本次轮询未检测到状态变化');
          }
        }
      } catch (error) {
        console.error('轮询支付状态时出错:', error);
      }
      
      // 继续轮询
      timerId = setTimeout(poll, interval);
    };
    
    // 立即开始第一次轮询
    poll();
    
    // 返回控制对象
    return {
      stop: () => {
        if (timerId) {
          clearTimeout(timerId);
          console.log(`停止轮询用户 ${userId} 的支付状态`);
        }
      }
    };
  }
};

export default paymentService; 