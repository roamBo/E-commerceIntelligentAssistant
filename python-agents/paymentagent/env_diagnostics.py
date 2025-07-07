import os
import platform
import subprocess
import sys
from dotenv import load_dotenv

def check_system_env_variables():
    """检查系统环境变量设置"""
    print("=== 系统环境变量诊断 ===")
    print(f"操作系统: {platform.system()}")
    print(f"Python 版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查所有包含 MODEL 的环境变量
    print("\n=== 所有包含 MODEL 的系统环境变量 ===")
    model_vars = {}
    for key, value in os.environ.items():
        if 'MODEL' in key.upper():
            model_vars[key] = value
            print(f"{key}: {value}")
    
    if not model_vars:
        print("未找到包含 MODEL 的系统环境变量")
    
    # 检查 Windows 环境变量设置位置
    if platform.system() == "Windows":
        print("\n=== Windows 环境变量检查 ===")
        try:
            # 检查用户环境变量
            result = subprocess.run(
                ['powershell', '-Command', '[Environment]::GetEnvironmentVariable("MODEL_NAME", "User")'],
                capture_output=True,
                text=True
            )
            user_model = result.stdout.strip()
            if user_model:
                print(f"用户环境变量 MODEL_NAME: {user_model}")
            else:
                print("用户环境变量中未找到 MODEL_NAME")
            
            # 检查系统环境变量
            result = subprocess.run(
                ['powershell', '-Command', '[Environment]::GetEnvironmentVariable("MODEL_NAME", "Machine")'],
                capture_output=True,
                text=True
            )
            system_model = result.stdout.strip()
            if system_model:
                print(f"系统环境变量 MODEL_NAME: {system_model}")
            else:
                print("系统环境变量中未找到 MODEL_NAME")
                
        except Exception as e:
            print(f"检查 Windows 环境变量失败: {e}")
    
    # 检查可能的配置文件
    print("\n=== 检查可能的配置文件 ===")
    config_files = [
        os.path.expanduser("~/.bashrc"),
        os.path.expanduser("~/.zshrc"),
        os.path.expanduser("~/.profile"),
        os.path.expanduser("~/.bash_profile"),
        os.path.expanduser("~/.env"),
        ".env",
        ".env.local"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ 找到配置文件: {config_file}")
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'MODEL_NAME' in content:
                        print(f"   📝 该文件包含 MODEL_NAME 设置")
                        # 显示相关行
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'MODEL_NAME' in line:
                                print(f"   第 {i+1} 行: {line.strip()}")
            except Exception as e:
                print(f"   ❌ 无法读取文件: {e}")
        else:
            print(f"❌ 配置文件不存在: {config_file}")

def check_python_env():
    """检查 Python 环境"""
    print("\n=== Python 环境检查 ===")
    
    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 正在使用虚拟环境")
        print(f"虚拟环境路径: {sys.prefix}")
        
        # 检查虚拟环境中的激活脚本
        if platform.system() == "Windows":
            activate_script = os.path.join(sys.prefix, "Scripts", "activate.bat")
            if os.path.exists(activate_script):
                print(f"激活脚本: {activate_script}")
                try:
                    with open(activate_script, 'r') as f:
                        content = f.read()
                        if 'MODEL_NAME' in content:
                            print("   📝 激活脚本包含 MODEL_NAME 设置")
                except Exception as e:
                    print(f"   ❌ 无法读取激活脚本: {e}")
    else:
        print("❌ 未使用虚拟环境")
    
    # 检查 site-packages
    import site
    print(f"site-packages 目录: {site.getsitepackages()}")

def check_ide_settings():
    """检查 IDE 设置"""
    print("\n=== IDE 环境检查 ===")
    
    # 检查 PyCharm/IntelliJ 设置
    pycharm_configs = [
        os.path.expanduser("~/.PyCharm*/config/options/other.xml"),
        os.path.expanduser("~/.IntelliJIdea*/config/options/other.xml"),
        ".idea/workspace.xml",
        ".idea/runConfigurations/*.xml"
    ]
    
    for config_pattern in pycharm_configs:
        import glob
        matching_files = glob.glob(config_pattern)
        for config_file in matching_files:
            if os.path.exists(config_file):
                print(f"✅ 找到 IDE 配置: {config_file}")
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'MODEL_NAME' in content:
                            print(f"   📝 该配置文件包含 MODEL_NAME 设置")
                except Exception as e:
                    print(f"   ❌ 无法读取配置文件: {e}")

def test_dotenv_loading():
    """测试 .env 文件加载"""
    print("\n=== .env 文件加载测试 ===")
    
    # 加载前的环境变量
    print("加载 .env 文件前:")
    model_before = os.getenv('MODEL_NAME')
    print(f"  MODEL_NAME: {model_before}")
    
    # 加载 .env 文件
    load_result = load_dotenv(override=True)
    print(f"load_dotenv(override=True) 结果: {load_result}")
    
    # 加载后的环境变量
    print("加载 .env 文件后:")
    model_after = os.getenv('MODEL_NAME')
    print(f"  MODEL_NAME: {model_after}")
    
    # 检查是否被覆盖
    if model_before and model_after and model_before != model_after:
        print(f"✅ 环境变量被 .env 文件覆盖: {model_before} → {model_after}")
    elif model_before and model_after and model_before == model_after:
        print(f"⚠️  环境变量未被覆盖 (可能系统环境变量优先级更高)")
    elif not model_before and model_after:
        print(f"✅ 环境变量从 .env 文件加载: {model_after}")

def main():
    """主函数"""
    print("🔍 环境变量诊断工具")
    print("=" * 50)
    
    check_system_env_variables()
    check_python_env()
    check_ide_settings()
    test_dotenv_loading()
    
    print("\n=== 建议的解决方案 ===")
    print("1. 如果在 Windows 系统环境变量中设置了 MODEL_NAME，可以通过以下方式清除:")
    print("   - 打开 '系统属性' → '高级' → '环境变量'")
    print("   - 在 '用户变量' 或 '系统变量' 中找到并删除 MODEL_NAME")
    print("2. 检查 IDE (如 PyCharm) 的运行配置中是否设置了环境变量")
    print("3. 检查虚拟环境的激活脚本是否包含环境变量设置")
    print("4. 使用 load_dotenv(override=True) 强制覆盖系统环境变量")

if __name__ == "__main__":
    main()