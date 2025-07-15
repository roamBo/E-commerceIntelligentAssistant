# api_service.py - 使用示例（模拟支付）
import logging
from payment_agent import PaymentAgent
from config import PaymentConfig

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('paymentagent.log'),
            logging.StreamHandler()
        ]
    )

def test_payment_simulation():
    """测试模拟支付流程"""
    payment_agent = PaymentAgent()
    
    print("=== 测试模拟支付流程 ===")
    
    # 1. 创建支付
    print("\n1. 创建模拟支付")
    result = payment_agent.create_payment(
        order_id="ORD_SIM_001",
        user_id="USER_001",
        amount=99.99,
        payment_method="simulated"
    )
    print(f"创建支付结果: {result}")
    
    if result["success"]:
        payment_id = result["data"].get("id")
        
        if payment_id:
            # 2. 查询支付状态
            print("\n2. 查询支付状态")
            status_result = payment_agent.payment_api.get_payment_by_id(payment_id)
            print(f"查询状态结果: {status_result}")
            
            # 3. 模拟支付成功
            print("\n3. 模拟支付成功")
            success_result = payment_agent.simulate_payment_success(payment_id)
            print(f"模拟成功结果: {success_result}")
            
            # 4. 再次查询状态确认
            print("\n4. 确认支付状态")
            confirm_result = payment_agent.payment_api.get_payment_by_id(payment_id)
            print(f"确认状态结果: {confirm_result}")
            
            # 5. 测试退款
            print("\n5. 测试退款")
            refund_result = payment_agent.process_refund(payment_id, "测试退款")
            print(f"退款结果: {refund_result}")
    
    # 6. 测试获取用户支付记录
    print("\n6. 测试获取用户支付记录")
    user_payments = payment_agent.get_user_payments("USER_001")
    print(f"用户支付记录: {user_payments}")

def test_payment_failure_simulation():
    """测试模拟支付失败流程"""
    payment_agent = PaymentAgent()
    
    print("\n=== 测试模拟支付失败流程 ===")
    
    # 1. 创建支付
    print("\n1. 创建模拟支付")
    result = payment_agent.create_payment(
        order_id="ORD_SIM_002",
        user_id="USER_002",
        amount=199.99,
        payment_method="simulated"
    )
    print(f"创建支付结果: {result}")
    
    if result["success"]:
        payment_id = result["data"].get("id")
        
        if payment_id:
            # 2. 模拟支付失败
            print("\n2. 模拟支付失败")
            failure_result = payment_agent.simulate_payment_failure(payment_id)
            print(f"模拟失败结果: {failure_result}")
            
            # 3. 查询状态确认
            print("\n3. 确认支付状态")
            confirm_result = payment_agent.payment_api.get_payment_by_id(payment_id)
            print(f"确认状态结果: {confirm_result}")

def test_inter_agent_requests():
    """测试跨Agent请求"""
    payment_agent = PaymentAgent()
    
    print("\n=== 测试跨Agent请求接口 ===")
    
    # 1. 测试创建支付请求
    print("\n1. 测试跨Agent创建支付")
    result = payment_agent.handle_inter_agent_request("create_payment", {
        "order_id": "ORD_INTER_001",
        "user_id": "USER_003",
        "amount": 150.00,
        "payment_method": "simulated"
    })
    print(f"跨Agent创建支付结果: {result}")
    
    if result["success"]:
        payment_id = result["data"].get("id")
        
        # 2. 测试模拟支付成功
        print("\n2. 测试跨Agent模拟支付成功")
        success_result = payment_agent.handle_inter_agent_request("simulate_payment_success", {
            "payment_id": payment_id
        })
        print(f"跨Agent模拟成功结果: {success_result}")
        
        # 3. 测试查询支付状态
        print("\n3. 测试跨Agent查询支付状态")
        status_result = payment_agent.handle_inter_agent_request("get_payment_status", {
            "payment_id": payment_id
        })
        print(f"跨Agent查询状态结果: {status_result}")

def test_edge_cases():
    """测试边界情况"""
    payment_agent = PaymentAgent()
    
    print("\n=== 测试边界情况 ===")
    
    # 1. 测试零金额支付
    print("\n1. 测试零金额支付")
    result = payment_agent.create_payment(
        order_id="ORD_ZERO",
        user_id="USER_004",
        amount=0,
        payment_method="simulated"
    )
    print(f"零金额支付结果: {result}")
    
    # 2. 测试超限金额支付
    print("\n2. 测试超限金额支付")
    result = payment_agent.create_payment(
        order_id="ORD_OVERLIMIT",
        user_id="USER_005",
        amount=99999,
        payment_method="simulated"
    )
    print(f"超限金额支付结果: {result}")
    
    # 3. 测试对不存在支付的退款
    print("\n3. 测试对不存在支付的退款")
    result = payment_agent.process_refund("NONEXISTENT_PAYMENT", "测试退款")
    print(f"不存在支付退款结果: {result}")

def main():
    """主函数"""
    setup_logging()
    
    print("Payment Agent - 模拟支付测试")
    print("=" * 50)
    print("🎭 注意：所有支付都是模拟的，不涉及真实资金")
    
    try:
        # 测试模拟支付成功流程
        test_payment_simulation()
        
        # 测试模拟支付失败流程
        test_payment_failure_simulation()
        
        # 测试跨Agent请求
        test_inter_agent_requests()
        
        # 测试边界情况
        test_edge_cases()
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("✅ 模拟支付测试完成")

if __name__ == "__main__":
    main()