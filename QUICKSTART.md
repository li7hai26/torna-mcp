# Torna MCP Server - 快速开始指南

## 项目概述

这是一个完整的 MCP（模型上下文协议）服务器，用于与 Torna 接口文档管理平台交互。该服务器提供了17个工具函数，涵盖文档、字典和模块的完整管理功能。

## 已实现的功能

### 📚 文档 API (6个工具)
- `torna_push_document` - 推送文档到 Torna
- `torna_create_category` - 创建文档分类
- `torna_update_category_name` - 更新分类名称
- `torna_list_documents` - 列出文档
- `torna_get_document_detail` - 获取文档详情
- `torna_get_document_details_batch` - 批量获取文档详情

### 📖 字典 API (5个工具)
- `torna_create_dictionary` - 创建字典
- `torna_update_dictionary` - 更新字典
- `torna_list_dictionaries` - 列出字典
- `torna_get_dictionary_detail` - 获取字典详情
- `torna_delete_dictionary` - 删除字典

### 🏗️ 模块 API (5个工具)
- `torna_create_module` - 创建模块
- `torna_update_module` - 更新模块
- `torna_list_modules` - 列出模块
- `torna_get_module_detail` - 获取模块详情
- `torna_delete_module` - 删除模块

## 快速部署

### 1. 下载项目
```bash
# 项目已在 /Users/li7hai26/workspace/idp-mcp/torna-mcp/ 目录中
cd /Users/li7hai26/workspace/idp-mcp/torna-mcp
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 设置你的 Torna 服务器地址和访问令牌
export TORNA_URL="http://localhost:7700/api"
export TORNA_TOKENS="your_module_token_1,your_module_token_2"

# 或者复制 .env.example 为 .env 并修改配置
cp .env.example .env
# 编辑 .env 文件填入实际配置
```

### 4. 验证安装
```bash
python3 -m py_compile main.py  # 语法检查
python3 test_server.py         # 运行测试脚本
```

### 5. 启动 MCP 服务器
```bash
python main.py
```

## 在 MCP 客户端中使用

在你的 MCP 客户端配置中添加：

```json
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["/Users/li7hai26/workspace/idp-mcp/torna-mcp/main.py"]
    }
  }
}
```

## 使用示例

### 创建文档分类
```
工具: torna_create_category
参数:
{
  "name": "用户管理",
  "description": "用户相关的API接口",
  "access_token": "your_token"
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
  ],
  "access_token": "your_token"
}
```

### 列出所有文档
```
工具: torna_list_documents
参数:
{
  "access_token": "your_token",
  "limit": 20,
  "offset": 0
}
```

## 响应格式

所有工具支持两种响应格式：

- **Markdown** (默认): 人类可读格式，适合展示
- **JSON**: 结构化数据，适合程序处理

## 重要特性

✅ **完整的类型验证** - 使用 Pydantic 确保输入数据的准确性
✅ **错误处理** - 一致的错误消息格式
✅ **分页支持** - 所有列表操作都支持分页
✅ **字符限制** - 自动处理大响应数据的截断
✅ **异步处理** - 使用 asyncio 提高性能
✅ **响应格式** - 支持 Markdown 和 JSON 两种格式
✅ **文档化** - 每个工具都有详细的说明和示例

## 故障排除

### 环境变量错误
确保设置了必要的环境变量：
- `TORNA_URL`: Torna 服务器地址
- `TORNA_TOKENS`: 访问令牌列表

### 权限错误
检查访问令牌是否有效且具有相应权限。

### 网络连接
确保能够访问 Torna 服务器地址。

## 文件结构

```
torna-mcp/
├── main.py              # 主要的 MCP 服务器实现
├── requirements.txt     # Python 依赖列表
├── README.md           # 详细使用文档
├── QUICKSTART.md       # 快速开始指南
├── .env.example        # 环境变量配置示例
├── test_server.py      # 测试脚本
└── evaluation.xml      # 评估测试用例
```

## 注意事项

1. **安全**: 不要在代码中硬编码访问令牌
2. **备份**: 重要操作前建议备份数据
3. **测试**: 使用 test_server.py 进行功能验证
4. **文档**: 详细文档请参考 README.md

开始使用 Torna MCP Server，提升你的 API 文档管理效率！