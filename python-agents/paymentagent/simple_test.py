from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

def debug_environment():
    """调试环境变量和路径"""
    print("=== 环境调试信息 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python 可执行文件: {os.sys.executable}")
    print(f"__file__ 路径: {__file__}")
    
    # 检查 .env 文件是否存在
    env_files = ['.env', './.env', '../.env']
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"✅ 找到 .env 文件: {os.path.abspath(env_file)}")
            # 读取并显示文件内容
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"文件内容:\n{content}")
        else:
            print(f"❌ 未找到 .env 文件: {os.path.abspath(env_file)}")
    
    # 在加载 .env 之前检查环境变量
    print("\n=== 加载 .env 文件之前的环境变量 ===")
    print(f"MODEL_NAME (加载前): {os.getenv('MODEL_NAME')}")
    
    # 尝试加载环境变量
    print("\n=== 加载环境变量 ===")
    load_result = load_dotenv(override=True)
    print(f"load_dotenv() 结果: {load_result}")
    
    # 加载后检查环境变量
    print("\n=== 加载 .env 文件之后的环境变量 ===")
    api_key = os.getenv("SILICONFLOW_API_KEY")
    base_url = os.getenv("SILICONFLOW_BASE_URL") 
    model_name = os.getenv("MODEL_NAME")
    
    print(f"SILICONFLOW_API_KEY: {api_key[:10] + '...' if api_key else 'None'}")
    print(f"SILICONFLOW_BASE_URL: {base_url}")
    print(f"MODEL_NAME: {model_name}")
    
    # 检查所有包含 MODEL 的环境变量
    print("\n=== 所有包含 MODEL 的环境变量 ===")
    for key, value in os.environ.items():
        if 'MODEL' in key.upper():
            print(f"{key}: {value}")
    
    return api_key, base_url, model_name

def test_with_override():
    """强制覆盖环境变量进行测试"""
    print("\n=== 强制覆盖环境变量测试 ===")
    
    # 强制设置正确的模型名称
    os.environ["MODEL_NAME"] = "deepseek-ai/DeepSeek-R1"
    
    try:
        llm = ChatOpenAI(
            api_key=os.getenv("SILICONFLOW_API_KEY"),
            base_url=os.getenv("SILICONFLOW_BASE_URL"),
            model=os.getenv("MODEL_NAME"),  # 使用强制设置的值
            temperature=0.1,
            max_tokens=100
        )
        
        print("正在测试强制覆盖后的调用...")
        print(f"使用的模型: {os.getenv('MODEL_NAME')}")
        
        messages = [
            SystemMessage(content="你是一个专业的支付助手。"),
            HumanMessage(content="请回复：测试成功")
        ]
        
        response = llm.invoke(messages)
        print(f"✅ 调用成功: {response.content}")
        
    except Exception as e:
        print(f"❌ 调用失败: {str(e)}")

def test_simple_chat():
    """测试简单的聊天功能"""
    try:
        # 先调试环境
        api_key, base_url, model_name = debug_environment()
        
        if not api_key:
            print("❌ API Key 未找到，请检查 .env 文件")
            return
        
        llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model_name,
            temperature=0.1,
            max_tokens=100
        )
        
        print("\n=== 测试 API 调用 ===")
        print("正在测试 ChatOpenAI 调用...")
        print(f"使用的模型: {model_name}")
        
        messages = [
            SystemMessage(content="你是一个专业的支付助手。"),
            HumanMessage(content="请回复：测试成功")
        ]
        
        response = llm.invoke(messages)
        print(f"✅ 调用成功: {response.content}")
        
    except Exception as e:
        print(f"❌ 调用失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_chat()
    test_with_override()