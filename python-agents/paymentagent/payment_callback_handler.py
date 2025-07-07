from flask import Flask, request, jsonify
import logging
from payment_agent import PaymentAgent
from config import PaymentConfig

app = Flask(__name__)
payment_agent = PaymentAgent()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/payment/callback/alipay', methods=['POST'])
def alipay_callback():
    """
    支付宝支付回调
    """
    try:
        # 获取回调数据
        callback_data = request.json
        logger.info(f"收到支付宝回调: {callback_data}")
        
        # 处理回调
        result = payment_agent.handle_payment_callback(callback_data)
        
        if result["success"]:
            return jsonify({"code": 200, "message": "success"})
        else:
            return jsonify({"code": 400, "message": result["error"]}), 400
            
    except Exception as e:
        logger.error(f"支付宝回调处理失败: {str(e)}")
        return jsonify({"code": 500, "message": "internal error"}), 500

@app.route('/payment/callback/wechat', methods=['POST'])
def wechat_callback():
    """
    微信支付回调
    """
    try:
        # 获取回调数据
        callback_data = request.json
        logger.info(f"收到微信支付回调: {callback_data}")
        
        # 处理回调
        result = payment_agent.handle_payment_callback(callback_data)
        
        if result["success"]:
            return jsonify({"code": 200, "message": "success"})
        else:
            return jsonify({"code": 400, "message": result["error"]}), 400
            
    except Exception as e:
        logger.error(f"微信支付回调处理失败: {str(e)}")
        return jsonify({"code": 500, "message": "internal error"}), 500

@app.route('/payment/notify', methods=['POST'])
def payment_notify():
    """
    通用支付通知接口
    """
    try:
        # 获取通知数据
        notify_data = request.json
        logger.info(f"收到支付通知: {notify_data}")
        
        # 处理通知
        result = payment_agent.handle_payment_callback(notify_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"支付通知处理失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/payment/status/<payment_id>', methods=['GET'])
def get_payment_status(payment_id):
    """
    获取支付状态
    """
    try:
        result = payment_agent.payment_api.get_payment_by_id(payment_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取支付状态失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查
    """
    return jsonify({"status": "healthy", "service": "payment_agent"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)