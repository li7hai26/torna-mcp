# 安装指南 - Torna MCP Server

## 通过uv安装（推荐）

### 1. 克隆项目
```bash
git clone https://github.com/li7hai26/torna-mcp.git
cd torna-mcp
```

### 2. 使用uv安装依赖
```bash
uv venv
source .venv/bin/activate  # 或在 Windows 上: .venv\Scripts\activate
uv pip install -e .
```

### 3. 配置环境变量
创建 `.env` 文件或设置环境变量：

```bash
export TORNA_URL="https://your-torna-instance.com"
export TORNA_TOKENS="token1,token2,token3"
```

### 4. 运行服务器
```bash
torna-mcp
```

## 通过pip安装

如果包已发布到PyPI：
```bash
pip install torna-mcp
```

## 系统要求
- Python 3.8 或更高版本
- uv（推荐）或 pip
- 网络访问权限连接到您的Torna实例

## 验证安装
```bash
torna-mcp --help
```

安装成功后，您将在终端看到MCP服务器启动消息，表示可以接受来自MCP客户端（如Claude Desktop、Cursor等）的连接。