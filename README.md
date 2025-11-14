# Torna MCP Server

[![PyPI](https://img.shields.io/pypi/v/torna-mcp)](https://pypi.org/project/torna-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/torna-mcp)](https://pypi.org/project/torna-mcp/)
[![License](https://img.shields.io/pypi/l/torna-mcp)](https://github.com/li7hai26/torna-mcp/blob/main/LICENSE)
[![GitHub](https://img.shields.io/github/stars/li7hai26/torna-mcp)](https://github.com/li7hai26/torna-mcp)

一个用于与 Torna 接口文档管理平台交互的 MCP（模型上下文协议）服务器。该服务器基于真实的 Torna OpenAPI 规范，提供了5个完整工具，允许 LLM 通过标准化的接口来管理 Torna 中的 API 文档。

**基于真实 Torna API 规范**: http://localhost:7700/api

## 🚀 快速开始

### 安装

#### 方法1：通过 uv 安装（推荐）

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装包
uv add toma-mcp

# 或使用 pip
pip install toma-mcp
```

#### 方法2：从源码安装

```bash
# 使用 uv
uv pip install -e .

# 或使用 pip
pip install -e .
```

### 配置环境变量

```bash
# 设置Torna服务器地址
export TORNA_URL="http://localhost:7700/api"

# 设置模块访问令牌
export TORNA_TOKEN="your-module-token-here"
```

**获取Token方法:**
1. 登录 Torna 管理后台
2. 选择项目
3. 选择模块
4. 点击 OpenAPI 标签
5. 复制 token

**环境变量文件:** 如果您使用环境变量文件：

```bash
cp .env.example .env
# 编辑 .env 文件，设置您的 TORNA_URL 和 TORNA_TOKEN
```

### 启动MCP服务器

```bash
torna-mcp
```

启动后，服务器将在标准输出显示连接信息，您可以将其配置到MCP客户端中使用。

## 📚 功能特性

### 核心 API 接口 (5个工具)

基于真实的 Torna OpenAPI 规范实现：

- **推送文档** (`torna_push_document`) - 向 Torna 推送 API 文档
  - 支持创建分类/文件夹
  - 支持请求/响应参数定义
  - 支持错误码配置
  - 支持调试环境设置

- **获取单个文档详情** (`torna_get_document_detail`) - 获取单个文档详细信息
  - 获取文档完整信息
  - 包括请求/响应参数
  - 包括错误码信息

- **获取模块信息** (`torna_get_module`) - 获取应用模块基本信息
  - 模块名称和描述
  - 模块状态信息

- **列出所有文档** (`torna_list_documents`) - 获取完整文档列表
  - 获取所有文档和文件夹
  - 支持分类结构
  - 解决“获取所有文档详情”问题

- **批量获取文档详情** (`torna_get_document_detail_batch`) - 批量获取多个文档详情
  - 一次性获取多个文档详细信息
  - 高效处理大量文档
  - 完整参数列表

**API 规范**: 基于 [Torna 官方 OpenAPI](https://torna.cn/dev/openapi.html) 实现

## 🛠️ MCP客户端配置

### Cursor
1. 打开Cursor设置
2. 找到MCP Servers配置
3. 添加新服务器：
```json
{
  "mcpServers": {
    "torna-mcp": {
      "command": "torna-mcp",
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKEN": "your-module-token-here"
      }
    }
  }
}
```

### Claude Desktop
1. 编辑Claude配置文件
2. 添加MCP服务器配置：
```json
{
  "mcpServers": {
    "torna-mcp": {
      "command": "torna-mcp"
    }
  }
}
```
3. 重启Claude Desktop

### VS Code
1. 安装MCP相关扩展
2. 配置服务器连接
3. 使用MCP工具

## 📝 使用示例

### 推送 API 文档
```
工具: toma_push_document
参数:
{
  "name": "用户登录",
  "description": "用户登录接口",
  "url": "/api/auth/login",
  "http_method": "POST",
  "content_type": "application/json",
  "request_params": [
    {
      "name": "username",
      "type": "string",
      "description": "用户名",
      "required": true,
      "example": "john_doe"
    },
    {
      "name": "password", 
      "type": "string",
      "description": "密码",
      "required": true,
      "example": "123456"
    }
  ],
  "response_params": [
    {
      "name": "token",
      "type": "string",
      "description": "访问令牌"
    },
    {
      "name": "userId",
      "type": "string", 
      "description": "用户ID"
    }
  ],
  "author": "张三"
}
```

### 获取文档详情
```
工具: torna_get_document_detail
参数:
{
  "doc_id": "doc_123"
}
```

### 批量获取文档详情
```
工具: torna_get_document_detail_batch
参数:
{
  "doc_ids": ["doc_123", "doc_456", "doc_789"]
}
```

### 获取模块信息
```
工具: torna_get_module
参数:
{}
```

### 列出所有文档
```
工具: torna_list_documents
参数:
{}
```

### 创建分类（文件夹）
```
工具: toma_push_document
参数:
{
  "name": "用户管理",
  "description": "用户相关的API接口",
  "url": "",
  "http_method": "GET",
  "is_folder": true
}
```

### 带调试环境的文档
```
工具: toma_push_document
参数:
{
  "name": "商品查询",
  "description": "查询商品信息",
  "url": "/api/products/{id}",
  "http_method": "GET",
  "content_type": "application/json",
  "path_params": [
    {
      "name": "id",
      "type": "int",
      "description": "商品ID",
      "required": true,
      "example": "123"
    }
  ],
  "debug_env_name": "测试环境",
  "debug_env_url": "http://localhost:8080"
}
```

## 🔧 系统要求

### 环境要求
- **Python**: 3.11 或更高版本
- **Torna**: 私有化部署版本
- **MCP客户端**: Cursor、Claude Desktop、VS Code等

### 开发工具
- **uv**: 现代 Python 包管理器
- **pytest**: 测试框架
- **black**: 代码格式化
- **isort**: 导入排序
- **mypy**: 类型检查

## 🧪 开发

### 安装开发依赖

```bash
uv sync --dev
```

### 运行测试

```bash
uv run pytest
```

### 代码格式化

```bash
uv run black src/ tests/
uv run isort src/ tests/
```

### 类型检查

```bash
uv run mypy src/
```

## 📄 许可证

本项目采用 MIT 许可证，详情请参见 [LICENSE](./LICENSE) 文件。

## 👨‍💻 开发者

- **作者**: 阿拉丁神灯
- **邮箱**: li7hai26@gmail.com
- **GitHub**: [@li7hai26](https://github.com/li7hai26)

## 📋 变更日志

详细变更日志请查看 [CHANGELOG.md](./CHANGELOG.md)

### v0.1.0 (2025-11-12) - Beta版本
- ✨ 初始版本发布
- ✅ 基于真实 Torna OpenAPI 规范实现 (5个工具)
- ✅ 解决"获取所有文档详情"的核心问题
- 📦 使用 uv 进行现代化包管理
- 🧪 添加完整测试套件
- 🔧 遵循 MCP 开发通用规范
- 🌏 支持国内镜像加速

---

**🔗 相关链接**
- [PyPI包](https://pypi.org/project/torna-mcp/)
- [GitHub仓库](https://github.com/li7hai26/torna-mcp)
- [Torna项目](https://gitee.com/dromara/Torna)