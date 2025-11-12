# Torna MCP Server

一个用于与 Torna 接口文档管理平台交互的 MCP（模型上下文协议）服务器。该服务器提供了工具，允许 LLM 通过标准化的接口来管理 Torna 中的文档、字典和模块。

## 功能特性

### 文档 API (Doc API)
- **推送文档** (`torna_push_document`) - 向 Torna 推送 API 文档
- **创建分类** (`torna_create_category`) - 创建文档分类/文件夹
- **更新分类名称** (`torna_update_category_name`) - 更新现有分类名称
- **列出文档** (`torna_list_documents`) - 获取应用文档列表
- **获取文档详情** (`torna_get_document_detail`) - 获取单个文档详细信息
- **批量获取文档详情** (`torna_get_document_details_batch`) - 批量获取多个文档详细信息

### 字典 API (Dictionary API)
- **创建字典** (`torna_create_dictionary`) - 创建新的枚举字典
- **更新字典** (`torna_update_dictionary`) - 更新现有字典信息
- **列出字典** (`torna_list_dictionaries`) - 获取字典列表
- **获取字典详情** (`torna_get_dictionary_detail`) - 获取字典详细信息
- **删除字典** (`torna_delete_dictionary`) - 删除字典（破坏性操作）

### 模块 API (Module API)
- **创建模块** (`torna_create_module`) - 创建新的模块
- **更新模块** (`torna_update_module`) - 更新现有模块信息
- **列出模块** (`torna_list_modules`) - 获取模块列表
- **获取模块详情** (`torna_get_module_detail`) - 获取模块详细信息
- **删除模块** (`torna_delete_module`) - 删除模块（破坏性操作）

## 环境要求

### Python 环境
- Python 3.8 或更高版本
- 必要的依赖包（见 requirements.txt）

### Torna 私有化部署
- 可访问的 Torna 服务器地址
- 模块访问令牌（access_token）

## 安装和使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

需要设置以下环境变量：

```bash
export TORNA_URL="http://localhost:7700/api"
export TORNA_TOKENS="your_module_token_1,your_module_token_2,your_module_token_3"
```

其中：
- `TORNA_URL`: Torna 私有化部署的 API 地址
- `TORNA_TOKENS`: 逗号分隔的模块令牌列表

### 3. 运行 MCP 服务器

```bash
python main.py
```

服务器将启动并通过 stdio 等待 MCP 客户端连接。

### 4. 在 MCP 客户端中使用

将 `python main.py` 作为 MCP 服务器添加到你的 MCP 客户端配置中。

## 工具使用示例

### 推送文档示例

```python
# 推送一个简单的 API 文档
params = {
    "name": "获取用户信息",
    "description": "根据用户 ID 获取用户详细信息",
    "url": "/api/users/{userId}",
    "http_method": "GET",
    "content_type": "application/json",
    "request_params": [
        {
            "name": "userId",
            "type": "string",
            "description": "用户 ID",
            "required": True,
            "example": "12345"
        }
    ],
    "response_params": [
        {
            "name": "id",
            "type": "string",
            "description": "用户 ID"
        },
        {
            "name": "name",
            "type": "string",
            "description": "用户姓名"
        }
    ],
    "access_token": "your_module_token",
    "response_format": "markdown"
}
```

### 创建分类示例

```python
# 创建一个用户管理分类
params = {
    "name": "用户管理",
    "description": "用户相关的 API 接口",
    "access_token": "your_module_token",
    "response_format": "markdown"
}
```

### 创建字典示例

```python
# 创建一个状态枚举字典
params = {
    "name": "订单状态",
    "description": "订单状态枚举值",
    "access_token": "your_module_token",
    "response_format": "markdown"
}
```

## 响应格式

所有工具都支持两种响应格式：

- **Markdown 格式** (默认): 人类可读，适合展示给用户
- **JSON 格式**: 机器可读，适合程序处理

## 错误处理

服务器提供了一致的错误处理机制：

- **输入验证错误**: 通过 Pydantic 模型自动处理
- **API 访问错误**: 返回格式化的错误消息
- **网络错误**: 处理超时和连接问题
- **权限错误**: 检查访问令牌的有效性

## 安全注意事项

1. **环境变量安全**: 确保不要在代码中硬编码访问令牌
2. **网络通信**: 建议使用 HTTPS 连接到 Torna 服务器
3. **权限控制**: 确保访问令牌具有适当的权限
4. **数据备份**: 重要操作前建议备份数据

## 开发和调试

### 本地测试

```bash
# 检查 Python 语法
python -m py_compile main.py

# 运行服务器进行测试
python main.py
```

### 调试技巧

1. 使用 `response_format: "json"` 获取结构化响应
2. 检查 Torna 服务器日志获取详细错误信息
3. 验证环境变量配置是否正确

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个 MCP 服务器。

## 许可证

本项目基于 MIT 许可证开源。