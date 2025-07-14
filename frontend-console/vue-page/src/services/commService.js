import axios from 'axios';

/**
 * 通信服务 - 作为前端与所有agent交互的唯一入口
 * 所有与用户的交互均由comm_agent负责，由comm_agent进一步调用其他agent
 */

// 创建API客户端实例
const apiClient = axios.create({
  baseURL: 'http://10.172.66.224:8084/agents', // 通信agent的API地址
  timeout: 600000,
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

// 通信服务
const commService = {
  /**
   * 与通信Agent进行对话交互
   * 通信Agent负责处理所有用户交互，并根据需要调用其他功能Agent
   * 
   * @param {string} userInput - 用户输入消息
   * @param {string} sessionId - 会话ID，用于维护对话历史
   * @param {string} agentType - 请求的服务类型，如'shopping'、'payment'等
   * @returns {Promise} - 响应数据
   */
  async chatWithAgent(userInput, sessionId, agentType = 'shopping') {
    try {
      const response = await apiClient.post('/chat', {
        user_input: userInput,
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      console.error('通信服务请求失败:', error);
      // 错误信息处理
      let errorMessage = '通信服务连接失败';
      
      if (error.response) {
        // 服务器返回了错误状态码
        const status = error.response.status;
        if (status === 401 || status === 403) {
          errorMessage = '认证失败，请重新登录';
        } else if (status === 404) {
          errorMessage = '通信服务接口不存在';
        } else if (status >= 500) {
          errorMessage = '通信服务内部错误';
        }
        
        // 如果服务器返回了详细错误信息
        if (error.response.data && error.response.data.detail) {
          errorMessage += `: ${error.response.data.detail}`;
        }
      } else if (error.request) {
        // 请求已发出，但没有收到响应
        errorMessage = '无法连接到通信服务，请检查网络连接';
      }
      
      throw {
        message: errorMessage,
        originalError: error
      };
    }
  },
  
  /**
   * 查询订单信息
   * 实际由comm_agent转发到order_agent处理
   * 
   * @param {string} sessionId - 会话ID
   * @returns {Promise} - 订单数据
   */
  async getOrders(sessionId) {
    try {
      const response = await apiClient.post('/chat', {
        user_input: '查询我的订单',
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      console.error('订单查询失败:', error);
      throw {
        message: '订单查询服务暂时不可用',
        originalError: error
      };
    }
  },
  
  /**
   * 查询支付信息
   * 实际由comm_agent转发到payment_agent处理
   * 
   * @param {string} sessionId - 会话ID
   * @returns {Promise} - 支付数据
   */
  async getPaymentInfo(sessionId) {
    try {
      const response = await apiClient.post('/chat', {
        user_input: '查询我的支付信息',
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      console.error('支付信息查询失败:', error);
      throw {
        message: '支付查询服务暂时不可用',
        originalError: error
      };
    }
  },
  
  /**
   * 生成唯一的会话ID
   * @returns {string} UUID格式的会话ID
   */
  generateSessionId() {
    // 创建类似UUID的标识符
    return 'user_' + Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }
};

export default commService; 