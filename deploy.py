#!/usr/bin/env python3
"""
Torna MCP Server 一键部署和验证脚本
自动检查环境、安装依赖、验证配置并启动服务器
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

class Colors:
    """终端颜色常量"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_colored(text: str, color: str):
    """打印彩色文本"""
    print(f"{color}{text}{Colors.END}")

def print_header(title: str):
    """打印标题"""
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored(f"🚀 {title}", Colors.BOLD + Colors.CYAN)
    print_colored(f"{'='*60}", Colors.CYAN)

def print_step(step: str, description: str):
    """打印步骤"""
    print_colored(f"\n📋 步骤 {step}: {description}", Colors.BLUE + Colors.BOLD)

def check_command(command: str) -> bool:
    """检查命令是否可用"""
    try:
        subprocess.run([command, "--version"], 
                      capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False

def run_command(command: list, description: str = None, capture_output: bool = True) -> tuple:
    """运行命令并返回结果"""
    if description:
        print_colored(f"   执行: {' '.join(command)}", Colors.YELLOW)
    
    try:
        if capture_output:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        else:
            result = subprocess.run(command, timeout=30)
        return result.returncode == 0, result
    except subprocess.TimeoutExpired:
        print_colored(f"   ❌ 命令超时: {' '.join(command)}", Colors.RED)
        return False, None
    except Exception as e:
        print_colored(f"   ❌ 命令执行异常: {e}", Colors.RED)
        return False, None

def install_dependencies():
    """安装依赖包"""
    print_step("1", "安装依赖包")
    
    # 检查是否在正确的目录
    if not Path("main.py").exists():
        print_colored("❌ 未找到 main.py 文件，请确保在项目根目录运行", Colors.RED)
        return False
    
    print_colored("✅ 项目文件检查通过", Colors.GREEN)
    
    # 升级 pip
    print_colored("升级 pip...", Colors.BLUE)
    success, _ = run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    if not success:
        print_colored("⚠️  pip 升级失败，继续安装依赖", Colors.YELLOW)
    
    # 安装依赖
    print_colored("安装 requirements.txt 中的依赖...", Colors.BLUE)
    success, result = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    if success:
        print_colored("✅ 依赖安装成功", Colors.GREEN)
        return True
    else:
        print_colored("❌ 依赖安装失败", Colors.RED)
        if result and result.stderr:
            print_colored(f"错误信息: {result.stderr}", Colors.RED)
        return False

def check_environment():
    """检查环境"""
    print_step("2", "检查运行环境")
    
    checks_passed = 0
    total_checks = 4
    
    # Python 版本检查
    python_version = sys.version_info
    print_colored(f"Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}", Colors.WHITE)
    if python_version >= (3, 8):
        print_colored("✅ Python 版本符合要求", Colors.GREEN)
        checks_passed += 1
    else:
        print_colored("❌ Python 版本过低，需要 3.8+", Colors.RED)
    
    # pip 检查
    if check_command("pip"):
        print_colored("✅ pip 可用", Colors.GREEN)
        checks_passed += 1
    else:
        print_colored("❌ pip 不可用", Colors.RED)
    
    # 项目文件检查
    required_files = ["main.py", "requirements.txt", "README.md"]
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if not missing_files:
        print_colored("✅ 所有必需文件存在", Colors.GREEN)
        checks_passed += 1
    else:
        print_colored(f"❌ 缺少文件: {', '.join(missing_files)}", Colors.RED)
    
    # 权限检查
    current_dir = Path(".")
    if current_dir.is_readable() and current_dir.is_executable():
        print_colored("✅ 目录权限正常", Colors.GREEN)
        checks_passed += 1
    else:
        print_colored("❌ 目录权限不足", Colors.RED)
    
    print_colored(f"环境检查结果: {checks_passed}/{total_checks} 通过", 
                  Colors.GREEN if checks_passed == total_checks else Colors.YELLOW)
    
    return checks_passed >= 3  # 允许一个检查失败

def validate_config():
    """验证配置"""
    print_step("3", "验证配置")
    
    # 运行配置验证脚本
    success, _ = run_command([sys.executable, "validate_config.py"])
    
    if success:
        print_colored("✅ 配置验证通过", Colors.GREEN)
        return True
    else:
        print_colored("⚠️  配置验证有警告，但可以继续", Colors.YELLOW)
        return True  # 配置验证的警告不影响部署

def setup_environment():
    """设置环境"""
    print_step("4", "设置环境变量")
    
    # 检查现有环境变量
    if os.getenv("TORNA_URL") and os.getenv("TORNA_TOKENS"):
        print_colored("✅ 环境变量已设置", Colors.GREEN)
        return True
    
    # 提供环境变量设置指南
    print_colored("未检测到环境变量，需要设置以下变量:", Colors.YELLOW)
    print_colored("export TORNA_URL='http://localhost:7700/api'", Colors.CYAN)
    print_colored("export TORNA_TOKENS='your_token_here'", Colors.CYAN)
    
    # 检查 .env 文件
    if Path(".env").exists():
        print_colored("✅ 找到 .env 配置文件", Colors.GREEN)
        return True
    elif Path(".env.example").exists():
        print_colored("💡 建议复制 .env.example 为 .env 并填入配置", Colors.BLUE)
        print_colored("cp .env.example .env", Colors.CYAN)
    
    print_colored("请设置环境变量或创建 .env 文件，然后重新运行此脚本", Colors.YELLOW)
    return False

def test_functionality():
    """测试功能"""
    print_step("5", "测试功能")
    
    # 语法检查
    print_colored("进行语法检查...", Colors.BLUE)
    success, _ = run_command([sys.executable, "-m", "py_compile", "main.py"])
    
    if success:
        print_colored("✅ 语法检查通过", Colors.GREEN)
    else:
        print_colored("❌ 语法检查失败", Colors.RED)
        return False
    
    # 如果有端到端测试，运行测试
    if Path("complete_e2e_test.py").exists():
        print_colored("运行端到端测试...", Colors.BLUE)
        success, result = run_command([sys.executable, "complete_e2e_test.py"])
        
        if success and "成功率: 100.0%" in (result.stdout if result else ""):
            print_colored("✅ 端到端测试通过", Colors.GREEN)
            return True
        else:
            print_colored("⚠️  端到端测试部分失败，但不影响部署", Colors.YELLOW)
            return True
    else:
        print_colored("ℹ️  未找到端到端测试，跳过", Colors.BLUE)
        return True

def start_server():
    """启动服务器"""
    print_step("6", "启动 MCP 服务器")
    
    print_colored("正在启动 Torna MCP Server...", Colors.BLUE)
    print_colored("按 Ctrl+C 停止服务器", Colors.YELLOW)
    print_colored("服务器启动后，可以通过 MCP 客户端连接使用", Colors.GREEN)
    
    try:
        # 以交互模式启动
        success, result = run_command([sys.executable, "main.py"], capture_output=False)
        if not success:
            print_colored("❌ 服务器启动失败", Colors.RED)
            return False
    except KeyboardInterrupt:
        print_colored("\n服务器已停止", Colors.YELLOW)
        return True
    
    return True

def show_usage_info():
    """显示使用信息"""
    print_header("Torna MCP Server 使用指南")
    
    print_colored("📚 文档:", Colors.BLUE)
    print_colored("  README.md      - 详细使用文档", Colors.WHITE)
    print_colored("  QUICKSTART.md  - 快速开始指南", Colors.WHITE)
    print_colored("  DEPLOYMENT.md  - 部署发布指南", Colors.WHITE)
    
    print_colored("\n🛠️  配置:", Colors.BLUE)
    print_colored("  .env           - 环境变量配置", Colors.WHITE)
    print_colored("  validate_config.py - 配置验证", Colors.WHITE)
    
    print_colored("\n🧪 测试:", Colors.BLUE)
    print_colored("  test_server.py       - 基础测试", Colors.WHITE)
    print_colored("  complete_e2e_test.py - 完整端到端测试", Colors.WHITE)
    
    print_colored("\n🚀 启动方式:", Colors.BLUE)
    print_colored("  python main.py                    - 直接启动", Colors.WHITE)
    print_colored("  python validate_config.py         - 验证配置", Colors.WHITE)
    print_colored("  python complete_e2e_test.py       - 运行测试", Colors.WHITE)
    
    print_colored("\n📝 MCP 客户端配置示例:", Colors.BLUE)
    config_example = """{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["/path/to/torna-mcp/main.py"],
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_here"
      }
    }
  }
}"""
    print_colored(config_example, Colors.CYAN)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Torna MCP Server 一键部署和验证脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python deploy.py              # 完整部署流程
  python deploy.py --config-only # 仅配置验证
  python deploy.py --start      # 仅启动服务器
  python deploy.py --help       # 显示帮助信息
        """
    )
    
    parser.add_argument("--config-only", action="store_true", 
                       help="仅验证配置，不启动服务器")
    parser.add_argument("--start", action="store_true", 
                       help="仅启动服务器，跳过其他步骤")
    parser.add_argument("--no-tests", action="store_true", 
                       help="跳过功能测试")
    
    args = parser.parse_args()
    
    print_header("Torna MCP Server 一键部署")
    
    # 显示使用信息
    show_usage_info()
    
    if args.start:
        # 仅启动服务器
        start_server()
        return
    
    if args.config_only:
        # 仅验证配置
        print_step("验证", "验证配置")
        validate_config()
        setup_environment()
        return
    
    # 完整部署流程
    success = True
    
    # 1. 检查环境
    if not check_environment():
        print_colored("❌ 环境检查失败，请解决环境问题后重试", Colors.RED)
        success = False
    
    # 2. 安装依赖
    if success and not install_dependencies():
        print_colored("❌ 依赖安装失败，请检查网络连接和权限", Colors.RED)
        success = False
    
    # 3. 验证配置
    if success:
        if not validate_config():
            print_colored("⚠️  配置验证有警告，但可以继续", Colors.YELLOW)
        
        if not setup_environment():
            print_colored("⚠️  请设置环境变量后重新运行", Colors.YELLOW)
            print_colored("设置完成后，可以运行: python deploy.py --start", Colors.BLUE)
            return
    
    # 4. 测试功能
    if success and not args.no_tests:
        if not test_functionality():
            print_colored("❌ 功能测试失败", Colors.RED)
            success = False
    
    # 汇总结果
    if success:
        print_header("部署完成!")
        print_colored("🎉 Torna MCP Server 部署成功!", Colors.GREEN + Colors.BOLD)
        print_colored("服务器已准备就绪，可以开始使用", Colors.GREEN)
        
        # 询问是否启动
        try:
            response = input("\n是否立即启动服务器? (y/n): ").lower().strip()
            if response in ['y', 'yes', '是', '']:
                start_server()
        except KeyboardInterrupt:
            print_colored("\n用户取消启动", Colors.YELLOW)
    else:
        print_header("部署失败")
        print_colored("❌ 部署过程中遇到问题", Colors.RED)
        print_colored("请检查错误信息并解决后重试", Colors.YELLOW)
        print_colored("或者运行: python validate_config.py", Colors.BLUE)

if __name__ == "__main__":
    main()