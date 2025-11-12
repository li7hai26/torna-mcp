# Torna MCP Server

[![PyPI](https://img.shields.io/pypi/v/torna-mcp)](https://pypi.org/project/torna-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/torna-mcp)](https://pypi.org/project/torna-mcp/)
[![License](https://img.shields.io/pypi/l/torna-mcp)](https://github.com/li7hai26/torna-mcp/blob/main/LICENSE)
[![GitHub](https://img.shields.io/github/stars/li7hai26/torna-mcp)](https://github.com/li7hai26/torna-mcp)

一个用于与 Torna 接口文档管理平台交互的 MCP（模型上下文协议）服务器。该服务器提供了16个工具，允许 LLM 通过标准化的接口来管理 Torna 中的文档、字典和模块。

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
export TORNA_URL="https://your-torna-instance.com"

# 设置访问令牌（多个令牌用逗号分隔，系统会自动选择第一个）
export TORNA_TOKENS="token1,token2,token3"
```

**注意：** 如果您使用的是Gitee，可以使用环境变量文件：

```bash
cp .env.example .env
# 编辑 .env 文件，设置您的TORNA_URL和TORNA_TOKENS
```

### 🔐 智能Token选择机制

本系统支持智能Token选择，您无需在每个工具中手动指定token：

1. **自动选择**：如果没有提供 `access_token` 参数，系统会自动使用 `TORNA_TOKENS` 环境变量中的第一个token
2. **手动覆盖**：您仍可以在特定工具中提供 `access_token` 参数来覆盖默认选择
3. **多token支持**：如果您有多个模块的token，可以设置多个，系统会使用第一个作为默认

**示例：**
```python
# 使用默认token（从环境变量自动选择）
{
  "name": "用户登录",
  "description": "用户登录接口"
  # 无需提供 access_token
}

# 手动指定特定token
{
  "name": "商品管理",
  "description": "商品管理接口",
  "access_token": "specific_token_for_product_module"
}
```

### 启动MCP服务器

```bash
torna-mcp
```

启动后，服务器将在标准输出显示连接信息，您可以将其配置到MCP客户端中使用。

## 📚 功能特性

### 文档 API (6个工具)
- **推送文档** (`torna_push_document`) - 向 Torna 推送 API 文档
- **创建分类** (`torna_create_category`) - 创建文档分类/文件夹  
- **更新分类名称** (`torna_update_category_name`) - 更新现有分类名称
- **列出文档** (`torna_list_documents`) - 获取应用文档列表
- **获取文档详情** (`torna_get_document_detail`) - 获取单个文档详细信息
- **批量获取文档详情** (`torna_get_document_details_batch`) - 批量获取多个文档详细信息

### 字典 API (5个工具)
- **创建字典** (`torna_create_dictionary`) - 创建新的枚举字典
- **更新字典** (`torna_update_dictionary`) - 更新现有字典信息
- **列出字典** (`torna_list_dictionaries`) - 获取字典列表
- **获取字典详情** (`torna_get_dictionary_detail`) - 获取字典详细信息
- **删除字典** (`torna_delete_dictionary`) - 删除字典（破坏性操作）

### 模块 API (5个工具)
- **创建模块** (`torna_create_module`) - 创建新的模块
- **更新模块** (`torna_update_module`) - 更新现有模块信息
- **列出模块** (`torna_list_modules`) - 获取模块列表
- **获取模块详情** (`torna_get_module_detail`) - 获取模块详细信息
- **删除模块** (`torna_delete_module`) - 删除模块（破坏性操作）

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
        "TORNA_URL": "https://your-torna-instance.com",
        "TORNA_TOKENS": "your-tokens-here"
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

### 创建文档分类
```
工具: torna_create_category
参数:
{
  "name": "用户管理",
  "description": "用户相关的API接口"
  // access_token会自动从环境变量选择
}
```

### 推送 API 文档
```
工具: torna_push_document
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
  ]
  // access_token会自动从环境变量选择
}
```

### 列出所有文档
```
工具: torna_list_documents
参数:
{
  "limit": 20,
  "offset": 0
  // access_token会自动从环境变量选择
}
```

### 使用特定Token（覆盖默认选择）
```
工具: toma_push_document
参数:
{
  "name": "商品管理",
  "description": "商品管理接口",
  "url": "/api/products",
  "http_method": "GET",
  "access_token": "specific_product_token"  // 手动指定特定token
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