# cli.py
import sys
import os
import asyncio
import json

# 解决导入路径问题
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from core.agent import OrderAgent
from app_config import settings


def main():
    """命令行交互入口"""
    print("=" * 50)
    print(" 欢迎使用电商订单助手 - 命令行交互模式 ")
    print("=" * 50)
    print("输入 'exit' 退出对话")
    print("支持创建、修改、取消、退款订单，查询订单状态和物流信息")
    print("-" * 50)

    # 初始化Agent
    agent = OrderAgent()

    # 使用配置中的文件路径
    chat_history_file = settings.CHAT_HISTORY_FILE

    # 确保目录存在
    directory = os.path.dirname(chat_history_file)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    # 初始化订单ID为None
    order_id = None

    while True:
        # 获取用户输入
        user_input = input("\n你: ").strip()

        # 退出条件
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("助手: 再见！")
            agent.save_chat_history_to_file(chat_history_file)
            print(f"对话历史已保存到: {chat_history_file}")
            break

        # 检查是否为订单ID（格式为ORD+5位数字）
        if user_input.startswith("ORD") and len(user_input) == 9:
            order_id = user_input
            print(f"助手: 已记录订单ID: {order_id}")
            continue

        # 构建带订单ID的完整输入（仅当order_id已设置时）
        full_input = f"订单ID: {order_id}. {user_input}" if order_id else user_input

        # 获取Agent回复
        response = agent.run(full_input)
        print(f"助手: {response}")

        # 保存对话历史到文件
        agent.save_chat_history_to_file(chat_history_file)


if __name__ == "__main__":
    main()