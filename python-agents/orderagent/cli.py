# cli.py（保留 Rich 但简化标签）
import os
import sys
from rich.console import Console
from rich.prompt import Prompt

# 解决导入路径问题
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from core.agent import OrderAgent

console = Console()


def main():
    # 初始化代理
    agent = OrderAgent()

    console.print("[bold green]===== 订单处理助手已启动 =====")
    console.print("输入 [bold]exit[/bold], [bold]quit[/bold] 或 [bold]bye[/bold] 退出")
    console.print("输入 [bold]clear[/bold] 清空聊天记录")

    try:
        # 主循环
        while True:
            # 修改此处：使用单个样式标签
            user_input = Prompt.ask("\n[blue]你[/blue]")
            if user_input.lower() in ["exit", "quit", "bye"]:
                break
            elif user_input.lower() == "clear":
                agent.clear_chat_history()
            else:
                response = agent.run(user_input)
                console.print(f"\n[green]助手[/green]: {response}\n")

    finally:
        # 保存聊天记录到 Redis
        agent._save_chat_history()
        console.print("[yellow]聊天记录已保存到 Redis[/yellow]")


if __name__ == "__main__":
    main()