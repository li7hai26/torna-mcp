# MCP 客户端配置指南

## 🚀 安装方式

首先安装 Torna MCP Server：

```bash
# 从 PyPI 安装（推荐）
pip install toma-mcp
# 或使用 uv
uv pip install toma-mcp

# 验证安装
torna-mcp --help
```

## ⚙️ 配置环境变量

```bash
# 设置 Torna 服务器地址
export TORNA_URL="https://your-torna-instance.com"

# 设置模块令牌（多个用逗号分隔）
export TORNA_TOKENS="token1,token2,token3"
```

## 🔌 客户端配置

### 1. Claude Desktop

**方式一：自动检测**
Claude Desktop 会自动检测系统中可用的 MCP 服务器。

**方式二：手动配置**

编辑 Claude Desktop 配置文件：`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "torna-mcp": {
      "command": "torna-mcp",
      "args": []
    }
  }
}
```

重启 Claude Desktop 后，在对话中使用：
```
请帮我连接 Torna MCP 服务器，列出所有可用的工具。
```

### 2. Cursor

1. 打开 Cursor 编辑器
2. 进入 Settings（设置）
3. 搜索 "MCP" 或 "Model Context Protocol"
4. 在 MCP Servers 配置中：
   - **名称**: `torna-mcp`
   - **命令**: `torna-mcp`
   - **参数**: 留空

重启 Cursor 后可以使用：
```
使用 Torna MCP 工具管理我的接口文档。
```

### 3. VS Code

1. 安装 MCP 相关扩展（如 MCP、Model Context Protocol 等）
2. 打开命令面板 (`Ctrl+Shift+P`)
3. 搜索 "MCP" 相关命令
4. 配置服务器：
   - **名称**: `torna-mcp`
   - **命令**: `torna-mcp`

### 4. IFlow CLI

```bash
# IFlow CLI 会自动检测已安装的 MCP 服务器
# 直接使用：

# 连接 Torna MCP 服务器
iflow connect toma-mcp

# 或在对话中：
```

### 5. 其他 MCP 客户端

任何支持 MCP 协议的客户端都可以通过以下方式连接：

```bash
# 启动命令
torna-mcp

# 客户端配置
Name: torna-mcp
Command: toma-mcp
Args: []
```

## 📋 可用工具列表

连接成功后，您可以使用以下工具：

### 📄 文档 API (6个工具)
- `torna_push_document` - 推送文档到 Torna
- `torna_create_category` - 创建文档分类
- `torna_update_category_name` - 更新分类名称
- `torna_list_documents` - 列出应用文档
- `torna_get_document_detail` - 获取文档详情
- `torna_get_document_details_batch` - 批量获取文档详情

### 📚 字典 API (5个工具)
- `torna_create_dictionary` - 创建字典
- `torna_update_dictionary` - 更新字典
- `torna_list_dictionaries` - 列出字典
- `torna_get_dictionary_detail` - 获取字典详情
- `torna_delete_dictionary` - 删除字典

### 🔧 模块 API (5个工具)
- `torna_create_module` - 创建模块
- `torna_update_module` - 更新模块
- `torna_list_modules` - 列出模块
- `torna_get_module_detail` - 获取模块详情
- `torna_delete_module` - 删除模块

## 🎯 使用示例

### 在 Claude Desktop 中
```
我来帮你管理 Torna 中的接口文档。

首先，列出当前所有的文档：
请使用 `torna_list_documents` 查看有哪些文档

然后，我可以：
- 创建新的 API 文档
- 更新现有文档内容
- 管理文档分类
- 查看模块详情
```

### 在 Cursor 中
```
请使用 Torna MCP 工具帮我：
1. 检查可用的模块列表
2. 为新功能创建文档分类
3. 推送 API 文档到指定模块
```

### 通用提示
```
使用 Torna MCP 管理接口文档：
- 列出当前所有模块
- 创建新模块的文档分类
- 推送一个用户管理相关的API文档
- 列出所有枚举字典
```

## 🛠️ 故障排除

### 1. 服务器无法启动

```bash
# 检查环境变量
echo $TORNA_URL
echo $TORNA_TOKENS

# 测试启动
torna-mcp
```

常见错误：
- `TORNA_URL environment variable is required` - 设置 TORNA_URL
- `TORNA_TOKENS environment variable is required` - 设置 TORNA_TOKENS

### 2. 客户端无法连接

1. **确认服务器运行**：
   ```bash
   # 在终端中测试
   torna-mcp
   ```

2. **检查客户端配置**：
   - 命令路径是否正确
   - 参数是否为空
   - 权限是否正确

3. **重启客户端**：
   - 关闭并重启 MCP 客户端
   - 重新连接服务器

### 3. 工具调用失败

1. **检查 Torna 连接**：
   ```bash
   # 测试 Torna 服务器可达性
   curl -I $TORNA_URL
   ```

2. **验证令牌权限**：
   - 确认 TORNA_TOKENS 中的令牌有效
   - 检查令牌对应模块的权限

3. **查看错误日志**：
   - 多数 MCP 客户端会显示详细错误信息
   - 根据错误信息进行问题定位

## 📝 开发者和高级用法

### 自定义配置

```bash
# 创建配置文件 ~/.torna-mcp/config
TORNA_URL=https://your-torna.com
TORNA_TOKENS=token1,token2,token3

# 加载配置
source ~/.torna-mcp/config
torna-mcp
```

### 批量操作脚本

```bash
#!/bin/bash
# 批量推送文档脚本

export TORNA_URL="https://your-torna.com"
export TORNA_TOKENS="your_token"

# 启动 MCP 服务器
torna-mcp &
MCP_PID=$!

# 等待服务器启动
sleep 3

# 执行批量操作
# 这里可以调用 MCP 工具进行批量操作

# 停止服务器
kill $MCP_PID
```

### 作为 Python 模块使用

```python
import os
from main import mcp, main

# 配置环境
os.environ['TORNA_URL'] = "https://your-torna.com"
os.environ['TORNA_TOKENS'] = "your_token"

# 启动服务器
if __name__ == "__main__":
    main()
```

## 🎉 成功！

配置完成后，您就可以在各种 MCP 客户端中享受智能的 Torna 接口文档管理体验了！

---

**💡 提示**: 建议在生产环境中为 Torna MCP 设置独立的运行环境，避免与其他 Python 包冲突。