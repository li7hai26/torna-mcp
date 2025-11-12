# MCP 客户端配置指南

## 🚀 用户层面（从PyPI安装）

### 安装方式

首先通过PyPI安装Torna MCP Server：

```bash
# 使用pip安装（推荐）
pip install toma-mcp

# 或使用uv安装（推荐）
uv pip install toma-mcp

# 验证安装
torna-mcp --help
```

### 配置环境变量

```bash
# 设置Torna服务器地址
export TORNA_URL="https://your-torna-instance.com"

# 设置模块令牌（多个用逗号分隔）
export TORNA_TOKENS="token1,token2,token3"
```

**推荐：使用环境变量文件**
```bash
cp .env.example .env
# 编辑.env文件，设置您的TORNA_URL和TORNA_TOKENS
source .env
```

### 启动MCP服务器

```bash
# 简单启动
torna-mcp

# 服务器启动后，在MCP客户端中配置
```

## 🔌 客户端配置

### 1. Claude Desktop

**自动检测**
Claude Desktop会自动检测系统中已安装的MCP服务器，包括`torna-mcp`。

**手动配置**
编辑Claude Desktop配置文件：
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

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

重启Claude Desktop后，在对话中使用：
```
请帮我使用Torna MCP管理接口文档，列出可用的工具。
```

### 2. Cursor

1. 打开Cursor编辑器
2. 进入Settings（设置）
3. 搜索"MCP"或"Model Context Protocol"
4. 在MCP Servers配置中：
   - **名称**: `torna-mcp`
   - **命令**: `torna-mcp`
   - **参数**: 留空

重启Cursor后可以使用：
```
使用Torna MCP工具帮我：
1. 查看所有可用模块
2. 创建新的文档分类
3. 推送API文档
```

### 3. VS Code

1. 安装MCP相关扩展（如MCP、Model Context Protocol等）
2. 打开命令面板 (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. 搜索"MCP"相关命令
4. 配置服务器：
   - **名称**: `torna-mcp`
   - **命令**: `torna-mcp`

### 4. IFlow CLI

```bash
# IFlow CLI会自动检测已安装的MCP服务器
# 直接在对话中使用：

# 或手动连接
iflow connect toma-mcp
```

### 5. 其他MCP客户端

任何支持MCP协议的客户端都可以通过以下方式连接：

```bash
# 启动命令
torna-mcp

# 客户端配置
Name: torna-mcp
Command: toma-mcp
Args: []
```

## 👨‍💻 开发者层面（从源码运行）

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/li7hai26/torna-mcp.git
cd torna-mcp

# 开发模式安装
pip install -e .
# 或使用uv
uv pip install -e .
```

### 本地运行

```bash
# 进入项目目录
cd torna-mcp

# 设置环境变量
export TORNA_URL="https://your-torna-instance.com"
export TORNA_TOKENS="token1,token2,token3"

# 直接运行Python模块
python main.py

# 或通过uv运行
uv run python main.py
```

### 作为Python模块使用

```python
import os
from main import mcp, main

# 配置环境
os.environ['TORNA_URL'] = "https://your-torna.com"
os.environ['TORNA_TOKENS'] = "your_token"

if __name__ == "__main__":
    main()
```

## 📋 可用工具列表

连接成功后，您可以使用以下16个工具：

### 📄 文档API (6个工具)
- `torna_push_document` - 推送文档到Torna
- `torna_create_category` - 创建文档分类
- `torna_update_category_name` - 更新分类名称
- `torna_list_documents` - 列出应用文档
- `torna_get_document_detail` - 获取文档详情
- `torna_get_document_details_batch` - 批量获取文档详情

### 📚 字典API (5个工具)
- `torna_create_dictionary` - 创建字典
- `torna_update_dictionary` - 更新字典
- `torna_list_dictionaries` - 列出字典
- `torna_get_dictionary_detail` - 获取字典详情
- `torna_delete_dictionary` - 删除字典

### 🔧 模块API (5个工具)
- `torna_create_module` - 创建模块
- `torna_update_module` - 更新模块
- `torna_list_modules` - 列出模块
- `torna_get_module_detail` - 获取模块详情
- `torna_delete_module` - 删除模块

## 🎯 使用示例

### 在Claude Desktop中
```
我来帮你管理Torna中的接口文档。

首先，请使用`torpa_list_modules`查看有哪些模块
然后，我们可以：
- 为新功能创建API文档
- 更新现有文档内容
- 管理枚举字典
- 整理文档分类结构
```

### 在Cursor中
```
请使用Torna MCP工具帮我：
1. 查看可用的模块列表
2. 创建用户管理相关的文档分类
3. 推送用户登录API的文档
4. 列出所有枚举字典以供复用
```

### 通用提示模板
```
使用Torna MCP管理接口文档：
- 列出当前所有模块和它们的文档数量
- 创建一个新的用户相关模块
- 为该模块添加用户注册、登录、密码重置三个API文档
- 创建一个"用户权限"枚举字典
- 查看整体文档结构并给出整理建议
```

## 🛠️ 故障排除

### 1. 服务器无法启动

```bash
# 检查环境变量
echo $TORNA_URL
echo $TORNA_TOKENS

# 测试安装
torna-mcp --help

# 重新安装（如果有问题）
pip uninstall toma-mcp && pip install toma-mcp
```

常见错误：
- `TORNA_URL environment variable is required` - 设置TORNA_URL
- `TORNA_TOKENS environment variable is required` - 设置TORNA_TOKENS

### 2. 客户端无法连接

1. **确认服务器运行**：
   ```bash
   # 在终端中测试
   torna-mcp
   ```

2. **检查客户端配置**：
   - 命令路径是否正确：`torna-mcp`
   - 参数是否为空
   - 权限是否正确

3. **重启客户端**：
   - 关闭并重启MCP客户端
   - 重新连接服务器

### 3. 工具调用失败

1. **检查Torna连接**：
   ```bash
   # 测试Torna服务器可达性
   curl -I $TORNA_URL
   ```

2. **验证令牌权限**：
   - 确认TORNA_TOKENS中的令牌有效
   - 检查令牌对应模块的权限

3. **查看错误日志**：
   - 多数MCP客户端会显示详细错误信息
   - 根据错误信息进行问题定位

## 🔄 批量操作示例

### 环境变量文件配置
```bash
# 创建 ~/.torna-mcp/config
echo "TORNA_URL=https://your-torna.com" > ~/.torna-mcp/config
echo "TORNA_TOKENS=token1,token2,token3" >> ~/.torna-mcp/config

# 加载配置
source ~/.torna-mcp/config
torna-mcp
```

### 批量推送脚本
```bash
#!/bin/bash
# 批量文档推送脚本

export TORNA_URL="https://your-torna.com"
export TORNA_TOKENS="your_token"

# 启动MCP服务器
torna-mcp &
MCP_PID=$!

# 等待服务器启动
sleep 3

# 执行批量操作
# 使用MCP工具进行批量操作

# 停止服务器
kill $MCP_PID
```

## 📝 开发者和高级配置

### 自定义配置目录
```bash
# 创建配置文件目录
mkdir -p ~/.torna-mcp

# 创建环境变量文件
cat > ~/.torna-mcp/.env << EOF
TORNA_URL=https://your-torna.com
TORNA_TOKENS=token1,token2,token3
EOF

# 加载配置
source ~/.torna-mcp/.env
torna-mcp
```

### Docker使用（开发者）
```dockerfile
FROM python:3.11-slim

RUN pip install toma-mcp

COPY .env.example .env

# 构建镜像
docker build -t toma-mcp .

# 运行容器
docker run --env-file .env torna-mcp
```

### 调试模式
```bash
# 开启详细日志
TORNA_DEBUG=1 torna-mcp

# 查看工具列表
torna-mcp --list-tools
```

## 🎉 成功！

配置完成后，您就可以在各种MCP客户端中享受智能的Torna接口文档管理体验了！

---

**💡 提示**：
- **用户层面**：使用 `pip install toma-mcp` 即可直接使用
- **开发者层面**：从源码安装，可以自定义和修改
- **生产环境**：建议为Torna MCP设置独立的虚拟环境