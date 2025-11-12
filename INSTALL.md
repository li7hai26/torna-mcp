# 安装指南 - Torna MCP Server

## 🚀 快速安装（推荐）

### 通过PyPI安装

```bash
# 使用pip
pip install toma-mcp

# 或使用uv（推荐）
uv pip install toma-mcp
```

### 验证安装

```bash
torna-mcp --help
```

## 🔧 环境要求

- **Python**: 3.8+
- **Torna**: 私有化部署版本
- **MCP客户端**: Cursor、Claude Desktop、VS Code等

## ⚙️ 配置

### 设置环境变量

```bash
# 基本配置
export TORNA_URL="https://your-torna-instance.com"
export TORNA_TOKENS="token1,token2,token3"

# 或使用环境变量文件（推荐）
cp .env.example .env
# 编辑 .env 文件，设置您的配置
source .env
```

### 环境变量说明

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `TORNA_URL` | 是 | Torna服务器地址 | `https://your-torna.com/api` |
| `TORNA_TOKENS` | 是 | 访问令牌（逗号分隔） | `token1,token2,token3` |

## 🖥️ 启动MCP服务器

```bash
torna-mcp
```

服务器启动后，您将看到启动信息。在MCP客户端中配置使用 `torna-mcp` 作为服务器命令。

## 🔗 MCP客户端配置

### Cursor
1. 打开Cursor设置
2. 找到MCP Servers配置
3. 添加服务器配置（参考README.md或MCP_CLIENTS.md）

### Claude Desktop
1. 编辑Claude配置文件
2. 添加MCP服务器配置
3. 重启应用

### VS Code
1. 安装MCP相关扩展
2. 配置服务器连接
3. 使用MCP工具

详细的客户端配置请参见 [MCP_CLIENTS.md](./MCP_CLIENTS.md)

## 📦 从源码安装

如果您需要开发或修改代码：

```bash
# 克隆仓库
git clone https://github.com/li7hai26/torna-mcp.git
cd torna-mcp

# 开发模式安装
pip install -e .
# 或使用uv
uv pip install -e .

# 运行测试
python complete_e2e_test.py
```

## 🛠️ 系统特定说明

### macOS
```bash
# 使用Homebrew安装Python
brew install python3

# 使用uv安装（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# 使用uv（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```bash
# 安装Python（从官网下载）
# 或使用Chocolatey
choco install python
```

## 🔧 故障排除

### 安装问题

**pip找不到包**
```bash
# 确保使用正确的包名
pip install toma-mcp

# 检查Python版本
python --version

# 更新pip
python -m pip install --upgrade pip
```

**uv安装失败**
```bash
# 更新uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 使用完整路径
uv pip install toma-mcp
```

### 运行问题

**环境变量未设置**
```bash
# 检查环境变量
echo $TORNA_URL
echo $TORNA_TOKENS

# 重新加载配置文件
source .env
```

**服务器启动失败**
```bash
# 检查依赖
pip list | grep torna-mcp

# 重新安装
pip uninstall toma-mcp && pip install toma-mcp
```

### 连接问题

**MCP客户端连接失败**
- 确保服务器正在运行
- 检查环境变量配置
- 查看客户端日志

## 📞 技术支持

如果遇到问题：

1. **GitHub Issues**: https://github.com/li7hai26/torna-mcp/issues
2. **PyPI评论**: https://pypi.org/project/torna-mcp/
3. **邮件联系**: li7hai26@gmail.com

## 🔗 相关链接

- [PyPI页面](https://pypi.org/project/torna-mcp/)
- [GitHub仓库](https://github.com/li7hai26/torna-mcp)
- [Torna项目](https://gitee.com/dromara/Torna)