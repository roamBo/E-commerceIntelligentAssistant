import axios from 'axios';

// 创建API客户端实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8085', // 商品推荐Agent的API地址
  timeout: 15000,
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

// 商品推荐服务
const guideService = {
  /**
   * 与商品推荐Agent进行对话交互
   * @param {string} userInput - 用户输入消息
   * @param {string} sessionId - 会话ID，用于维护对话历史
   * @returns {Promise} - 响应数据
   */
  async chatWithAgent(userInput, sessionId) {
    try {
      const response = await apiClient.post('/chat', {
        user_input: userInput,
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      console.error('商品推荐对话请求失败:', error);
      // 错误信息处理
      let errorMessage = '商品推荐服务连接失败';
      
      if (error.response) {
        // 服务器返回了错误状态码
        const status = error.response.status;
        if (status === 401 || status === 403) {
          errorMessage = '认证失败，请重新登录';
        } else if (status === 404) {
          errorMessage = '商品推荐服务接口不存在';
        } else if (status >= 500) {
          errorMessage = '商品推荐服务内部错误';
        }
        
        // 如果服务器返回了详细错误信息
        if (error.response.data && error.response.data.detail) {
          errorMessage += `: ${error.response.data.detail}`;
        }
      } else if (error.request) {
        // 请求已发出，但没有收到响应
        errorMessage = '无法连接到商品推荐服务，请检查网络连接';
      }
      
      throw {
        message: errorMessage,
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

export default guideService; 