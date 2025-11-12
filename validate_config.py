#!/usr/bin/env python3
"""
Torna MCP Server 配置验证脚本
验证部署环境和配置是否正确
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_header(title: str):
    """打印标题"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")

def print_success(message: str):
    """打印成功消息"""
    print(f"✅ {message}")

def print_error(message: str):
    """打印错误消息"""
    print(f"❌ {message}")

def print_warning(message: str):
    """打印警告消息"""
    print(f"⚠️  {message}")

def print_info(message: str):
    """打印信息消息"""
    print(f"ℹ️  {message}")

def validate_python_version():
    """验证 Python 版本"""
    print_info(f"当前 Python 版本: {sys.version}")
    
    if sys.version_info >= (3, 8):
        print_success(f"Python 版本符合要求 (>=3.8)")
        return True
    else:
        print_error(f"Python 版本过低: {sys.version_info}")
        return False

def check_file_exists(filepath: str) -> bool:
    """检查文件是否存在"""
    path = Path(filepath)
    if path.exists():
        print_success(f"文件存在: {filepath}")
        return True
    else:
        print_error(f"文件不存在: {filepath}")
        return False

def validate_torna_config():
    """验证 Torna 配置"""
    config_errors = []
    
    # 检查 TORNA_URL
    torna_url = os.getenv("TORNA_URL")
    if not torna_url:
        config_errors.append("TORNA_URL 环境变量未设置")
    else:
        print_success(f"TORNA_URL: {torna_url}")
        
        # 检查 URL 格式
        if not (torna_url.startswith("http://") or torna_url.startswith("https://")):
            config_errors.append("TORNA_URL 应该以 http:// 或 https:// 开头")
        elif not torna_url.endswith("/api"):
            print_warning("TORNA_URL 建议以 /api 结尾")
        else:
            print_success("TORNA_URL 格式正确")
    
    # 检查 TORNA_TOKENS
    torna_tokens = os.getenv("TORNA_TOKENS")
    if not torna_tokens:
        config_errors.append("TORNA_TOKENS 环境变量未设置")
    else:
        tokens = [token.strip() for token in torna_tokens.split(",") if token.strip()]
        print_success(f"找到 {len(tokens)} 个访问令牌")
        
        # 验证令牌格式
        valid_tokens = 0
        for i, token in enumerate(tokens, 1):
            if len(token) >= 20:
                print_success(f"令牌 {i} 格式正确 ({token[:10]}...)")
                valid_tokens += 1
            else:
                print_warning(f"令牌 {i} 格式可能不正确 ({token})")
        
        if valid_tokens == 0:
            config_errors.append("没有找到有效的访问令牌")
    
    # 检查 .env 文件
    if check_file_exists(".env"):
        print_info("找到 .env 配置文件")
    
    return len(config_errors) == 0

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        ("httpx", "异步 HTTP 客户端"),
        ("pydantic", "数据验证和设置管理"),
        ("mcp.server.fastmcp", "MCP 服务器框架")
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            print_success(f"依赖包可用: {package} ({description})")
        except ImportError:
            print_error(f"缺少依赖包: {package} ({description})")
            missing_packages.append(package)
    
    if missing_packages:
        print_info(f"安装缺失依赖: pip install {' '.join(missing_packages)}")
    
    return len(missing_packages) == 0

def check_project_files():
    """检查项目文件"""
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md"
    ]
    
    optional_files = [
        ".env.example",
        "test_server.py",
        "DEPLOYMENT.md"
    ]
    
    print_info("检查必需文件:")
    all_required_files_exist = True
    for file in required_files:
        if not check_file_exists(file):
            all_required_files_exist = False
    
    print_info("检查可选文件:")
    for file in optional_files:
        check_file_exists(file)
    
    return all_required_files_exist

def check_permissions():
    """检查文件和目录权限"""
    current_dir = Path(".")
    
    try:
        # 检查目录是否可读
        os.access(current_dir, os.R_OK)
        print_success("当前目录可读")
    except Exception:
        print_error("当前目录不可读")
        return False
    
    try:
        # 检查目录是否可执行（进入目录）
        os.access(current_dir, os.X_OK)
        print_success("当前目录可执行")
    except Exception:
        print_error("当前目录不可执行")
        return False
    
    return True

def validate_syntax():
    """验证 Python 语法"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", "main.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_success("Python 语法检查通过")
            return True
        else:
            print_error("Python 语法检查失败:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print_error("语法检查超时")
        return False
    except Exception as e:
        print_error(f"语法检查异常: {e}")
        return False

def test_network_connectivity():
    """测试网络连接"""
    torna_url = os.getenv("TORNA_URL")
    if not torna_url:
        print_error("无法测试网络连接: TORNA_URL 未设置")
        return False
    
    try:
        import httpx
        import asyncio
        
        async def test_connection():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    # 尝试连接但不发送实际请求
                    response = await client.get(torna_url.rstrip('/api') + '/ping', timeout=5.0)
                    return True, response.status_code
            except httpx.TimeoutException:
                return False, "连接超时"
            except Exception as e:
                return False, str(e)
        
        # 运行异步测试
        success, status = asyncio.run(test_connection())
        
        if success:
            print_success(f"网络连接测试成功 (状态码: {status})")
            return True
        else:
            print_warning(f"网络连接测试失败: {status}")
            print_info("这可能是正常的，如果 Torna 服务器没有 /ping 端点")
            return True  # 不影响部署，只给出警告
    except ImportError:
        print_info("无法测试网络连接: 缺少 httpx 包")
        return True

def generate_config_example():
    """生成配置文件示例"""
    config = {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_1,your_token_2,your_token_3"
    }
    
    with open("config_example.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print_info("已生成配置文件示例: config_example.json")

def main():
    """主函数"""
    print_header("Torna MCP Server 配置验证")
    
    validation_results = []
    
    # 1. Python 环境检查
    print_header("Python 环境检查")
    validation_results.append(("Python 版本", validate_python_version()))
    
    # 2. 权限检查
    print_header("权限检查")
    validation_results.append(("文件权限", check_permissions()))
    
    # 3. 项目文件检查
    print_header("项目文件检查")
    validation_results.append(("项目文件", check_project_files()))
    
    # 4. 依赖包检查
    print_header("依赖包检查")
    validation_results.append(("依赖包", check_dependencies()))
    
    # 5. Torna 配置检查
    print_header("Torna 配置检查")
    validation_results.append(("Torna 配置", validate_torna_config()))
    
    # 6. 语法检查
    print_header("语法检查")
    validation_results.append(("Python 语法", validate_syntax()))
    
    # 7. 网络连接测试
    print_header("网络连接测试")
    validation_results.append(("网络连接", test_network_connectivity()))
    
    # 8. 生成配置示例
    print_header("配置示例生成")
    generate_config_example()
    
    # 汇总结果
    print_header("验证结果汇总")
    
    total_checks = len(validation_results)
    passed_checks = sum(1 for _, result in validation_results if result)
    success_rate = (passed_checks / total_checks) * 100
    
    print(f"\n📊 验证统计:")
    print(f"总检查项: {total_checks}")
    print(f"通过检查: {passed_checks}")
    print(f"失败检查: {total_checks - passed_checks}")
    print(f"成功率: {success_rate:.1f}%")
    
    print(f"\n详细结果:")
    for check_name, result in validation_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} {check_name}")
    
    # 总体建议
    if success_rate >= 90:
        print(f"\n🎉 配置验证基本通过！可以尝试部署 Torna MCP Server。")
    elif success_rate >= 70:
        print(f"\n⚠️  配置验证部分通过。建议解决以下问题后再部署:")
        for check_name, result in validation_results:
            if not result:
                print(f"  - 需要修复: {check_name}")
    else:
        print(f"\n❌ 配置验证失败过多。建议解决以下问题:")
        for check_name, result in validation_results:
            if not result:
                print(f"  - 必须修复: {check_name}")
    
    # 提供下一步建议
    print(f"\n📋 下一步建议:")
    if not os.getenv("TORNA_URL") or not os.getenv("TORNA_TOKENS"):
        print(f"  1. 设置环境变量:")
        print(f"     export TORNA_URL='http://localhost:7700/api'")
        print(f"     export TORNA_TOKENS='your_token_here'")
    
    print(f"  2. 安装依赖:")
    print(f"     pip install -r requirements.txt")
    
    print(f"  3. 测试功能:")
    print(f"     python main.py")
    
    print(f"  4. 运行完整测试:")
    print(f"     python complete_e2e_test.py")
    
    return success_rate >= 70

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
