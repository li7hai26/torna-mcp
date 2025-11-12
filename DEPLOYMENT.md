# Torna MCP Server - 部署发布指南

本指南详细说明了如何部署和发布 Torna MCP Server，让其他用户能够轻松使用它来操作 Torna 的 OpenAPI。

## 🚀 快速部署选项

### 选项 1: 直接下载使用 (推荐)

```bash
# 1. 克隆或下载项目
git clone <repository-url>  # 或下载 zip 文件并解压

# 2. 进入项目目录
cd torna-mcp

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置

# 5. 启动服务器
python main.py
```

### 选项 2: Docker 部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

构建和运行:

```bash
# 构建镜像
docker build -t torna-mcp .

# 运行容器
docker run -d \
  --name torna-mcp \
  -e TORNA_URL="http://localhost:7700/api" \
  -e TORNA_TOKENS="your_token_here" \
  -p 3000:3000 \
  torna-mcp
```

### 选项 3: 打包为 Python 包发布

创建 `setup.py`:

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="torna-mcp",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="MCP server for Torna API documentation management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/torna-mcp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "torna-mcp=main:main",
        ],
    },
)
```

发布到 PyPI:

```bash
# 安装打包工具
pip install build twine

# 构建包
python -m build

# 发布到 PyPI
python -m twine upload dist/*
```

安装和使用:

```bash
pip install torna-mcp
export TORNA_URL="http://localhost:7700/api"
export TORNA_TOKENS="your_token_here"
torna-mcp
```

## 📋 MCP 客户端配置

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
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
}
```

### VS Code MCP 配置

编辑 `~/.vscode-server/data/User/globalStorage/some-extension/mcp.json`:

```json
{
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
}
```

### 自定义 MCP 客户端

```javascript
// JavaScript/TypeScript 客户端示例
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');

const client = new Client({
  name: "torna-client",
  version: "1.0.0"
});

await client.connect({
  command: "python3",
  args: ["/path/to/torna-mcp/main.py"],
  env: {
    TORNA_URL: "http://localhost:7700/api",
    TORNA_TOKENS: "your_token_here"
  }
});

// 使用工具
const result = await client.callTool({
  name: "torna_create_category",
  arguments: {
    name: "用户管理",
    description: "用户相关API",
    access_token: "your_token_here"
  }
});
```

## 🔧 环境配置

### 环境变量配置

创建 `.env` 文件:

```bash
# Torna 服务器配置
TORNA_URL=http://localhost:7700/api
TORNA_TOKENS=token1,token2,token3

# 可选配置
LOG_LEVEL=INFO
CHARACTER_LIMIT=25000
```

### 配置文件验证

创建配置验证脚本 `validate_config.py`:

```python
#!/usr/bin/env python3
import os
import sys

def validate_config():
    """验证 Torna MCP 配置"""
    errors = []
    
    # 检查必要的环境变量
    if not os.getenv("TORNA_URL"):
        errors.append("❌ TORNA_URL 环境变量未设置")
    elif not os.getenv("TORNA_URL").endswith("/api"):
        errors.append("❌ TORNA_URL 应该以 /api 结尾")
    
    if not os.getenv("TORNA_TOKENS"):
        errors.append("❌ TORNA_TOKENS 环境变量未设置")
    elif "," in os.getenv("TORNA_TOKENS"):
        tokens = os.getenv("TORNA_TOKENS").split(",")
        if len(tokens) == 0:
            errors.append("❌ TORNA_TOKENS 格式错误")
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        errors.append(f"❌ Python 版本过低: {sys.version}")
    
    # 检查依赖包
    try:
        import httpx
        import pydantic
        from mcp.server.fastmcp import FastMCP
    except ImportError as e:
        errors.append(f"❌ 缺少依赖包: {e}")
    
    if errors:
        print("配置验证失败:")
        for error in errors:
            print(error)
        return False
    else:
        print("✅ 配置验证通过")
        return True

if __name__ == "__main__":
    validate_config()
```

## 🌐 网络和代理配置

### HTTP 代理支持

如果需要通过代理访问 Torna 服务器:

```python
# 在 main.py 中添加代理配置
proxy_config = {
    "http://proxy.company.com:8080": {
        "username": "proxy_user",
        "password": "proxy_pass"
    }
}

async with httpx.AsyncClient(proxies=proxy_config) as client:
    # API 调用
    pass
```

### SSL 证书配置

如果使用自签名证书或需要自定义 CA:

```python
import ssl
import httpx

# 自定义 SSL 上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async with httpx.AsyncClient(ssl=ssl_context) as client:
    # API 调用
    pass
```

## 📊 监控和日志

### 日志配置

创建 `logging_config.py`:

```python
import logging
import os

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("torna_mcp.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("torna_mcp")
```

### 健康检查端点

```python
# 添加到 main.py
from mcp.server.fastmcp import FastMCP

@mcp.tool()
async def health_check() -> str:
    """健康检查"""
    return "OK"

@mcp.tool()
async def torna_ping() -> str:
    """测试与 Torna 服务器的连接"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{os.getenv('TORNA_URL')}/ping", timeout=5.0)
            return f"✅ Torna 服务器连接正常 (状态码: {response.status_code})"
    except Exception as e:
        return f"❌ 无法连接到 Torna 服务器: {str(e)}"
```

## 🔐 安全配置

### 访问令牌管理

创建 `token_manager.py`:

```python
import os
import json
from typing import List, Optional

class TokenManager:
    """管理多个 Torna 访问令牌"""
    
    def __init__(self, tokens: str):
        self.tokens = self._parse_tokens(tokens)
        self.current_index = 0
    
    def _parse_tokens(self, tokens_str: str) -> List[str]:
        """解析令牌字符串"""
        return [token.strip() for token in tokens_str.split(",") if token.strip()]
    
    def get_current_token(self) -> Optional[str]:
        """获取当前令牌"""
        if self.tokens and self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        return None
    
    def rotate_token(self) -> Optional[str]:
        """轮换到下一个令牌"""
        if self.tokens:
            self.current_index = (self.current_index + 1) % len(self.tokens)
            return self.get_current_token()
        return None
    
    def validate_token(self, token: str) -> bool:
        """验证令牌格式"""
        return len(token) >= 20 and token.replace("-", "").replace("_", "").isalnum()
```

## 🧪 测试部署

### 自动化测试脚本

创建 `deploy_test.py`:

```python
#!/usr/bin/env python3
import asyncio
import subprocess
import sys
import time

async def test_deployment():
    """测试部署是否成功"""
    print("🧪 测试 Torna MCP Server 部署...")
    
    try:
        # 1. 检查 Python 语法
        result = subprocess.run([sys.executable, "-m", "py_compile", "main.py"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Python 语法检查失败")
            print(result.stderr)
            return False
        print("✅ Python 语法检查通过")
        
        # 2. 验证配置文件
        result = subprocess.run([sys.executable, "validate_config.py"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ 配置验证失败")
            print(result.stderr)
            return False
        print("✅ 配置验证通过")
        
        # 3. 启动服务器并测试工具
        process = subprocess.Popen([sys.executable, "main.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        time.sleep(2)  # 等待服务器启动
        
        # 测试服务器是否响应
        if process.poll() is None:
            print("✅ 服务器启动成功")
            
            # 运行功能测试
            result = subprocess.run([sys.executable, "complete_e2e_test.py"], 
                                  capture_output=True, text=True, timeout=30)
            if "成功率: 100.0%" in result.stdout:
                print("✅ 功能测试通过")
            else:
                print("⚠️ 功能测试部分失败")
                print(result.stdout)
        else:
            print("❌ 服务器启动失败")
            print(process.stderr.read())
            return False
        
        # 清理
        process.terminate()
        process.wait()
        
        print("🎉 部署测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_deployment())
    sys.exit(0 if success else 1)
```

### 部署验证清单

创建 `DEPLOYMENT_CHECKLIST.md`:

```markdown
# Torna MCP Server 部署清单

## 预部署检查
- [ ] Python 3.8+ 已安装
- [ ] pip 可用
- [ ] 项目文件完整下载
- [ ] Torna 服务器可访问
- [ ] 访问令牌有效

## 部署步骤
- [ ] 安装依赖: `pip install -r requirements.txt`
- [ ] 配置环境变量 (.env 文件)
- [ ] 验证配置: `python validate_config.py`
- [ ] 语法检查: `python -m py_compile main.py`
- [ ] 功能测试: `python complete_e2e_test.py`
- [ ] 启动服务器: `python main.py`

## MCP 客户端配置
- [ ] Claude Desktop 配置已更新
- [ ] VS Code MCP 配置已更新
- [ ] 自定义客户端配置已更新

## 生产环境检查
- [ ] SSL 证书配置正确
- [ ] 代理设置（如需要）
- [ ] 日志配置适当
- [ ] 监控和健康检查已设置
- [ ] 访问令牌安全管理

## 故障排除
- [ ] 环境变量配置错误
- [ ] 网络连接问题
- [ ] 权限访问错误
- [ ] 依赖包缺失

部署完成后，通过 MCP 客户端使用以下命令验证:

```
工具: torna_list_documents
参数:
{
  "access_token": "your_token_here",
  "limit": 1
}
```
```

## 📦 发布和分发

### GitHub Release

```bash
# 创建发布版本
git tag -a v1.0.0 -m "Release Torna MCP Server v1.0.0"
git push origin v1.0.0

# 在 GitHub 上创建 Release，附上:
# - 详细的发布说明
# - 下载链接
# - 安装指南
# - 使用示例
```

### Docker Hub 发布

```bash
# 构建并推送镜像
docker build -t yourusername/torna-mcp:latest .
docker build -t yourusername/torna-mcp:v1.0.0 .
docker push yourusername/torna-mcp:latest
docker push yourusername/torna-mcp:v1.0.0
```

### 使用说明生成

```bash
# 生成 API 文档
python -c "
from main import *
import inspect

for name in dir():
    obj = locals()[name]
    if hasattr(obj, '__annotations__') and obj.__annotations__:
        print(f'{name}: {obj.__annotations__}')
" > api_reference.md
```

遵循本指南，你就可以成功部署和发布 Torna MCP Server，让其他用户轻松使用它来管理 Torna 的 API 文档！

## 🆘 获取帮助

如果遇到部署问题:

1. 检查 `DEPLOYMENT_CHECKLIST.md` 中的故障排除部分
2. 查看日志文件 `torna_mcp.log`
3. 运行 `python validate_config.py` 诊断配置问题
4. 在 GitHub Issues 中报告问题

祝你部署顺利！🚀