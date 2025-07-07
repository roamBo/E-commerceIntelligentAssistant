/**
 * 订单数据模型
 * 定义订单的数据结构和相关操作
 */

/**
 * 创建新订单数据对象
 * @param {Object} data - 订单数据
 * @returns {Object} 订单对象
 */
export const createOrderModel = (data = {}) => {
  // 后端状态到前端状态的映射
  const statusMap = {
    PENDING_PAYMENT: 'pending',
    PROCESSING: 'processing',
    SHIPPED: 'shipped',
    COMPLETED: 'completed',
    // 可根据后端实际枚举继续补充
  };
  // 适配时间格式
  let date = data.orderTime || data.date || new Date().toLocaleString();
  if (typeof date === 'string' && date.includes('T')) {
    // ISO格式转本地字符串
    date = date.replace('T', ' ').split('.')[0];
  }
  return {
    id: data.orderId || data.id || `ORD-${Math.floor(Math.random() * 10000)}`,
    userId: data.userId || 0,
    date,
    status: statusMap[data.status] || data.status || 'pending',
    products: (data.items || data.products || []).map(item => createProductModel(item)),
    logistics: createLogisticsModel(data.logistics),
    shippingAddress: data.shippingAddress || '',
    totalAmount: data.totalAmount || calculateTotalAmount(data.items || data.products || [])
  };
};

/**
 * 创建商品数据模型
 * @param {Object} data - 商品数据
 * @returns {Object} 商品对象
 */
export const createProductModel = (data = {}) => {
  return {
    id: data.productId || data.id || '',
    name: data.productName || data.name || '',
    price: data.unitPrice || data.price || 0,
    quantity: data.quantity || 1,
    image: data.image || `https://picsum.photos/id/${Math.floor(Math.random() * 100)}/200/200`,
    attrs: data.attrs || '默认规格'
  };
};

/**
 * 创建物流数据模型
 * @param {Object} data - 物流数据
 * @returns {Object} 物流对象
 */
export const createLogisticsModel = (data = {}) => {
  return {
    status: data?.status || '待发货',
    company: data?.company || '顺丰速运',
    trackingNumber: data?.trackingNumber || `SF${Math.floor(Math.random() * 1000000000)}`
  };
};

/**
 * 计算订单总金额
 * @param {Array} products - 商品列表
 * @returns {number} 总金额
 */
export const calculateTotalAmount = (products = []) => {
  return products.reduce((sum, product) => {
    const price = product.unitPrice || product.price || 0;
    const quantity = product.quantity || 0;
    return sum + (price * quantity);
  }, 0);
};

/**
 * 创建用于提交到后端的订单数据
 * @param {Object} orderData - 前端订单数据
 * @returns {Object} 后端格式的订单数据
 */
export const createOrderRequestData = (orderData) => {
  return {
    userId: orderData.userId,
    totalAmount: orderData.totalAmount || calculateTotalAmount(orderData.products),
    shippingAddress: orderData.shippingAddress || '',
    items: (orderData.products || []).map(product => ({
      productId: product.id,
      productName: product.name,
      quantity: product.quantity,
      unitPrice: product.price
    }))
  };
};

export default {
  createOrderModel,
  createProductModel,
  createLogisticsModel,
  calculateTotalAmount,
  createOrderRequestData
};