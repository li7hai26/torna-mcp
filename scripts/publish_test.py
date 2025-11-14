#!/usr/bin/env python3
"""
Torna SDK 发布脚本 - Test PyPI 版本
用于发布测试版本到 Test PyPI 仓库
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class TestPublisher:
    """Test PyPI 发布器"""
    
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
    
    def upload_to_testpypi(self):
        """上传到 Test PyPI"""
        print("🚀 上传到 Test PyPI...")
        
        # API Token 从环境变量获取
        token = os.getenv("TEST_PYPI_TOKEN")
        if not token:
            print("  ⚠️  未找到 TEST_PYPI_TOKEN 环境变量")
            print("  📝 请设置: export TEST_PYPI_TOKEN='your-token'")
            return False
        
        try:
            # 上传到 Test PyPI
            result = subprocess.run([
                sys.executable, "-m", "twine", "upload",
                "--repository", "testpypi",
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
            return False
    
    def verify_publication(self):
        """验证发布"""
        print("🔍 验证发布...")
        
        try:
            import urllib.request
            import json
            
            # 检查包是否存在
            url = f"https://test.pypi.org/pypi/{self.package_name}/json"
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
    
    def show_installation_guide(self):
        """显示安装指南"""
        print("\n📋 安装和使用指南:")
        print("=" * 50)
        
        print("1️⃣  从 Test PyPI 安装:")
        print("   pip install -i https://test.pypi.org/simple/ torna-sdk==0.1.0")
        
        print("\n2️⃣  测试安装:")
        print("   python3 -c \"from torna_sdk import TornaClient; print('✅ 成功!')\"")
        
        print("\n3️⃣  使用示例:")
        print("""
   from torna_sdk import TornaClient, DocListRequest
   
   with TornaClient("http://localhost:7700", "your-token") as client:
       docs = client.get_documents()
       print(f"找到 {len(docs)} 个文档")
        """)
    
    def run(self):
        """运行完整的发布流程"""
        print("🚀 Torna SDK 发布到 Test PyPI")
        print("=" * 50)
        
        # 显示当前配置
        print(f"📦 包名: {self.package_name}")
        print(f"📁 SDK目录: {self.sdk_dir}")
        print(f"🔧 Python: {sys.executable}")
        print()
        
        # 检查依赖
        if not self.check_dependencies():
            return False
        
        # 清理构建目录
        self.clean_dist()
        
        # 构建包
        if not self.build_package():
            return False
        
        # 确认发布
        print("\n❓ 确认发布到 Test PyPI? (y/N): ", end="")
        response = input().strip().lower()
        if response not in ['y', 'yes']:
            print("发布已取消")
            return False
        
        # 上传到 Test PyPI
        if not self.upload_to_testpypi():
            return False
        
        # 验证发布
        if not self.verify_publication():
            print("⚠️  验证失败，但可能需要几分钟才能同步")
        
        # 显示安装指南
        self.show_installation_guide()
        
        print("\n🎉 Test PyPI 发布完成！")
        return True


def main():
    """主函数"""
    publisher = TestPublisher()
    success = publisher.run()
    
    if success:
        print("\n✅ 发布成功！")
        print("📋 下一步:")
        print("   1. 测试安装: pip install -i https://test.pypi.org/simple/ torna-sdk==0.1.0")
        print("   2. 验证功能")
        print("   3. 准备正式发布")
        sys.exit(0)
    else:
        print("\n❌ 发布失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()