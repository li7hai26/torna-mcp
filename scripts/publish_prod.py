#!/usr/bin/env python3
"""
Torna SDK 发布脚本 - 正式 PyPI 版本
用于发布正式版本到 PyPI 仓库
"""

import os
import sys
import subprocess
import shutil
import getpass
from pathlib import Path


class ProductionPublisher:
    """正式 PyPI 发布器"""
    
    def __init__(self):
        self.sdk_dir = Path(__file__).parent.parent / "torna-sdk"
        self.dist_dir = self.sdk_dir / "dist"
        self.package_name = "torna-sdk"
        
    def check_dependencies(self):
        """检查构建依赖"""
        print("🔍 检查构建依赖...")
        
        required_packages = ["build", "twine"]
        missing_packages = []
        
        for package in required_packages:
            try:
                subprocess.run([sys.executable, "-m", package, "--help"], 
                             capture_output=True, check=True)
                print(f"  ✅ {package} 已安装")
            except subprocess.CalledProcessError:
                missing_packages.append(package)
                print(f"  ❌ {package} 未安装")
        
        if missing_packages:
            print(f"\n⚠️  缺少依赖: {', '.join(missing_packages)}")
            print("请运行: pip install " + " ".join(missing_packages))
            return False
        
        return True
    
    def check_environment(self):
        """检查发布环境"""
        print("🔍 检查发布环境...")
        
        # 检查包版本
        pyproject_file = self.sdk_dir / "pyproject.toml"
        if pyproject_file.exists():
            with open(pyproject_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'version = "0.1.0"' in content:
                    print("  ⚠️  版本号仍然是 0.1.0，建议更新到正式版本号")
                    print("  💡 请更新 pyproject.toml 中的 version 为更高版本")
                    return False
                else:
                    print("  ✅ 版本号已更新")
        else:
            print("  ❌ 找不到 pyproject.toml 文件")
            return False
        
        # 检查 README 文件
        readme_file = self.sdk_dir / "README.md"
        if readme_file.exists():
            print("  ✅ README.md 存在")
        else:
            print("  ⚠️  README.md 不存在")
        
        return True
    
    def clean_dist(self):
        """清理旧的构建文件"""
        print("🧹 清理构建目录...")
        
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            print("  ✅ 已清理 dist 目录")
        else:
            print("  ℹ️  dist 目录不存在，无需清理")
    
    def build_package(self):
        """构建包"""
        print("🔨 构建包...")
        
        os.chdir(self.sdk_dir)
        
        try:
            # 构建源码包和wheel包
            result = subprocess.run([
                sys.executable, "-m", "build"
            ], check=True, capture_output=True, text=True)
            
            print("  ✅ 包构建成功")
            
            # 显示生成的文件
            if self.dist_dir.exists():
                files = list(self.dist_dir.glob("*"))
                print(f"  📦 生成的文件 ({len(files)} 个):")
                for file in files:
                    size = file.stat().st_size
                    print(f"    - {file.name} ({size:,} bytes)")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ 构建失败: {e}")
            if e.stderr:
                print(f"错误输出: {e.stderr}")
            return False
    
    def get_pypi_token(self):
        """获取 PyPI token"""
        token = os.getenv("PYPI_TOKEN")
        if not token:
            token = os.getenv("PYPI_PASSWORD")  # 兼容老版本
        
        if not token:
            print("  ⚠️  未找到 PYPI_TOKEN 环境变量")
            print("  📝 请设置: export PYPI_TOKEN='pypi-xxxxxx_token_here_xxxxxx'")
            token = getpass.getpass("或者输入 PyPI Token: ")
        
        return token.strip()
    
    def upload_to_pypi(self):
        """上传到正式 PyPI"""
        print("🚀 上传到 PyPI...")
        
        token = self.get_pypi_token()
        if not token:
            print("  ❌ 未提供有效的 token")
            return False
        
        try:
            # 上传到正式 PyPI
            result = subprocess.run([
                sys.executable, "-m", "twine", "upload",
                "--repository", "pypi",
                "--username", "__token__",
                "--password", token,
                str(self.dist_dir / "*")
            ], check=True, capture_output=True, text=True)
            
            print("  ✅ 上传成功")
            
            # 提取 URL 信息
            output = result.stdout
            if "View at:" in output:
                url_line = [line for line in output.split('\n') if "View at:" in line]
                if url_line:
                    url = url_line[0].split("View at:")[-1].strip()
                    print(f"  🔗 包页面: {url}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ 上传失败: {e}")
            if e.stderr:
                print(f"错误输出: {e.stderr}")
            
            # 检查是否是重复版本错误
            if "already exists" in str(e.stderr) or "already exists" in str(e.stdout):
                print("  💡 可能是版本号已存在，请检查版本号")
            
            return False
    
    def verify_publication(self):
        """验证发布"""
        print("🔍 验证发布...")
        
        try:
            import urllib.request
            import json
            
            # 检查包是否存在
            url = f"https://pypi.org/pypi/{self.package_name}/json"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                
                version = data["info"]["version"]
                print(f"  ✅ 包存在，版本: {version}")
                
                # 检查文件
                files = data["urls"]
                print(f"  📁 可用文件: {len(files)} 个")
                for file_info in files:
                    print(f"    - {file_info['filename']} ({file_info['size']:,} bytes)")
                
                return True
                
        except Exception as e:
            print(f"  ❌ 验证失败: {e}")
            return False
    
    def show_production_guide(self):
        """显示生产环境使用指南"""
        print("\n📋 生产环境使用指南:")
        print("=" * 50)
        
        print("1️⃣  从 PyPI 安装:")
        print("   pip install torna-sdk")
        
        print("\n2️⃣  测试安装:")
        print("   python3 -c \"from torna_sdk import TornaClient; print('✅ 成功!')\"")
        
        print("\n3️⃣  项目集成:")
        print("   # requirements.txt")
        print("   torna-sdk>=1.0.0")
        
        print("\n4️⃣  使用示例:")
        print("""
   from torna_sdk import TornaClient, DocListRequest
   
   with TornaClient("https://api.example.com", "production-token") as client:
       docs = client.get_documents()
       print(f"找到 {len(docs)} 个文档")
        """)
    
    def run(self):
        """运行完整的发布流程"""
        print("🚀 Torna SDK 发布到 PyPI (生产环境)")
        print("=" * 50)
        
        # 显示当前配置
        print(f"📦 包名: {self.package_name}")
        print(f"📁 SDK目录: {self.sdk_dir}")
        print(f"🔧 Python: {sys.executable}")
        print()
        
        # 检查环境和依赖
        if not self.check_environment():
            return False
        
        if not self.check_dependencies():
            return False
        
        # 清理构建目录
        self.clean_dist()
        
        # 构建包
        if not self.build_package():
            return False
        
        # 显示构建结果并确认
        print("\n📦 构建完成，准备发布到生产环境")
        print("⚠️  这将发布到正式的 PyPI 仓库，影响所有用户")
        print("\n❓ 确认发布到 PyPI 生产环境? (yes/no): ", end="")
        response = input().strip().lower()
        if response != 'yes':
            print("发布已取消")
            return False
        
        # 上传到 PyPI
        if not self.upload_to_pypi():
            return False
        
        # 验证发布
        if not self.verify_publication():
            print("⚠️  验证失败，但可能需要几分钟才能同步")
        
        # 显示使用指南
        self.show_production_guide()
        
        print("\n🎉 正式版本发布完成！")
        return True


def main():
    """主函数"""
    publisher = ProductionPublisher()
    success = publisher.run()
    
    if success:
        print("\n✅ 正式版本发布成功！")
        print("📋 下一步:")
        print("   1. 更新文档和 README")
        print("   2. 创建 GitHub Release")
        print("   3. 通知用户更新")
        print("   4. 更新 torna-mcp 包的依赖")
        sys.exit(0)
    else:
        print("\n❌ 发布失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()