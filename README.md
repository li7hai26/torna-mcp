# Torna MCP Server

[![PyPI](https://img.shields.io/pypi/v/torna-mcp)](https://pypi.org/project/torna-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/torna-mcp)](https://pypi.org/project/torna-mcp/)
[![License](https://img.shields.io/pypi/l/torna-mcp)](https://github.com/li7hai26/torna-mcp/blob/main/LICENSE)
[![GitHub](https://img.shields.io/github/stars/li7hai26/torna-mcp)](https://github.com/li7hai26/torna-mcp)

一个用于与 Torna 接口文档管理平台交互的 MCP（模型上下文协议）服务器。该服务器基于真实的 Torna OpenAPI 规范，提供了2个核心工具，允许 LLM 通过标准化的接口来管理 Torna 中的 API 文档。

**基于真实 Torna API 规范**: http://localhost:7700/api

## 🎉 发布状态

**项目已成功发布到PyPI！**  
- **包名**: `torna-mcp`  
- **版本**: `1.0.0`  
- **PyPI页面**: https://pypi.org/project/torna-mcp/  
- **许可证**: MIT  
- **Python支持**: >=3.8

## 🚀 快速开始

### 安装

#### 方法1：通过PyPI安装（推荐）

```bash
# 使用 pip
pip install toma-mcp

# 或使用 uv（推荐）
uv pip install toma-mcp
```

#### 方法2：从源码安装

```bash
git clone https://github.com/li7hai26/torna-mcp.git
cd torna-mcp
pip install -e .
# 或使用 uv
uv pip install -e .
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

### 核心 API 接口 (2个工具)

基于真实的 Torna OpenAPI 规范实现：

- **推送文档** (`torna_push_document`) - 向 Torna 推送 API 文档
  - 支持创建分类/文件夹
  - 支持请求/响应参数定义
  - 支持错误码配置
  - 支持调试环境设置

- **获取文档** (`torna_get_document`) - 获取单个文档详细信息
  - 获取文档完整信息
  - 包括请求/响应参数
  - 包括错误码信息

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

### IFlow CLI
```bash
# 添加到MCP配置
iflow mcp add toma-mcp
```

详细的客户端配置说明请参见 [MCP_CLIENTS.md](./MCP_CLIENTS.md)

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
工具: toma_get_document
参数:
{
  "doc_id": "doc_123"
}
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
- **Python**: 3.8 或更高版本
- **Torna**: 私有化部署版本
- **MCP客户端**: Cursor、Claude Desktop、VS Code等

### 安装Python环境
- **pip** (标准Python安装)
- **uv** (推荐 - 更快更现代的包管理器)
  ```bash
  # 安装uv
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## 📖 详细文档

- **[快速开始](./QUICKSTART.md)** - 详细的快速入门指南
- **[安装指南](./INSTALL.md)** - 多种安装方法
- **[MCP客户端配置](./MCP_CLIENTS.md)** - 各种MCP客户端的配置方法
- **[部署指南](./DEPLOYMENT.md)** - 生产环境部署说明

## 🐛 问题反馈

如果您在使用过程中遇到问题，请：

1. 查看 [GitHub Issues](https://github.com/li7hai26/torna-mcp/issues)
2. 在PyPI页面提交反馈
3. 发送邮件至: li7hai26@gmail.com

## 📄 许可证

本项目采用 MIT 许可证，详情请参见 [LICENSE](./LICENSE) 文件。

## 👨‍💻 开发者

- **作者**: 阿拉丁神灯
- **邮箱**: li7hai26@gmail.com
- **GitHub**: [@li7hai26](https://github.com/li7hai26)

---

**🔗 相关链接**
- [PyPI包](https://pypi.org/project/torna-mcp/)
- [GitHub仓库](https://github.com/li7hai26/torna-mcp)
- [Torna项目](https://gitee.com/dromara/Torna)