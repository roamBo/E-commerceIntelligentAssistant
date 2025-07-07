# main.py - 使用示例
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

def main():
    """主函数示例"""
    # 设置日志
    setup_logging()

    # 创建支付代理
    payment_agent = PaymentAgent()

    # 示例对话
    test_requests = [
        "我想支付100元，使用支付宝",
        "查询交易TXN_12345的状态",
        "我要申请退款，交易ID是TXN_12345，原因是商品有质量问题",
        "帮我验证这个支付信息是否正确：金额150元，币种CNY，支付方式微信"
    ]

    print("=== 支付代理测试 ===")
    for i, request in enumerate(test_requests, 1):
        print(f"\n测试 {i}: {request}")
        print("-" * 50)
        response = payment_agent.process_request(request)
        print(f"回复: {response}")

    # 交互式对话
    print("\n=== 交互式对话模式 ===")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'help' 获取帮助信息")

    while True:
        user_input = input("\n用户: ").strip()

        if user_input.lower() in ['quit', 'exit']:
            print("再见！")
            break

        if user_input.lower() == 'help':
            print(payment_agent.get_payment_help())
            continue

        if not user_input:
            continue

        response = payment_agent.process_request(user_input)
        print(f"代理: {response}")

if __name__ == "__main__":
    main()