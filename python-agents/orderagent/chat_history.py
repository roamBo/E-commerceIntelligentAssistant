import redis
import json
from app_config import settings

# 连接到 RedisStack
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

class OrderAgent:
    def __init__(self):
        # ...
        from langchain_community.chat_message_histories import ChatMessageHistory
        self.message_history = ChatMessageHistory()
        self._load_chat_history()

    def run(self, user_input: str) -> str:
        try:
            # ...
            if "订单ID" in user_input:
                order_id = user_input.split("订单ID")[1].strip()
                order_info = self._get_order_info(order_id)
                if order_info:
                    return f"订单 {order_id} 的信息如下：{order_info}"
                else:
                    return f"未找到订单 {order_id} 的信息。"

            # 保存聊天记录到 Redis
            self._save_chat_history()
            # 这里需要模拟 response 存在 "output" 键的情况，假设这里有一个响应
            response = {"output": "模拟的响应内容"}
            return response["output"]
        except Exception as e:
            # ...
            error_msg = f"处理请求时出错: {str(e)}"
            self.message_history.add_ai_message(error_msg)
            # 保存聊天记录到 Redis
            self._save_chat_history()
            return error_msg

    def _save_chat_history(self):
        """将对话历史保存到 Redis"""
        try:
            history = []
            for message in self.message_history.messages:
                if hasattr(message, 'type') and message.type == "human":
                    history.append({"type": "human", "data": {"content": message.content}})
                elif hasattr(message, 'type') and message.type == "ai":
                    history.append({"type": "ai", "data": {"content": message.content}})

            # 将聊天记录序列化为 JSON 字符串并保存到 Redis
            redis_client.set('chat_history', json.dumps(history))

        except Exception as e:
            print(f"保存对话历史失败: {str(e)}")

    def _load_chat_history(self):
        """从 Redis 加载对话历史"""
        try:
            history_data = redis_client.get('chat_history')
            if history_data:
                history = json.loads(history_data)
                for item in history:
                    if item["type"] == "human":
                        self.message_history.add_user_message(item["data"]["content"])
                    elif item["type"] == "ai":
                        self.message_history.add_ai_message(item["data"]["content"])
        except Exception as e:
            print(f"加载对话历史失败: {str(e)}")

    def _save_order_info(self, order_id, order_info):
        """保存订单信息到 Redis"""
        try:
            redis_client.set(f"order_info:{order_id}", json.dumps(order_info))
        except Exception as e:
            print(f"保存订单信息失败: {str(e)}")

    def _get_order_info(self, order_id):
        """从 Redis 中获取订单信息"""
        try:
            order_info_data = redis_client.get(f"order_info:{order_id}")
            if order_info_data:
                return json.loads(order_info_data)
            return None
        except Exception as e:
            print(f"获取订单信息失败: {str(e)}")
            return None

    def print_chat_history(self):
        """按行输出聊天记录"""
        history_data = redis_client.get('chat_history')
        if history_data:
            history = json.loads(history_data)
            for item in history:
                message_type = item["type"]
                content = item["data"]["content"]
                print(f"{message_type}: {content}")
        else:
            print("未找到聊天记录。")

if __name__ == "__main__":
    agent = OrderAgent()
    agent.print_chat_history()