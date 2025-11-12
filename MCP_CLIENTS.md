# 🔗 Torna MCP Server - MCP 客户端连接指南

本指南详细说明如何在各种MCP客户端中配置和使用Torna MCP Server。

## 📋 支持的MCP客户端

| 客户端 | 支持状态 | 配置文件位置 |
|--------|----------|--------------|
| Claude Desktop | ✅ 完全支持 | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Cursor IDE | ✅ 完全支持 | `~/.cursor/settings.json` |
| IFlow CLI | ✅ 完全支持 | `~/.iflow/config.json` |
| VS Code MCP | ✅ 完全支持 | `~/.vscode-server/data/User/globalStorage/some-extension/mcp.json` |
| 其他MCP客户端 | ✅ 通用支持 | 根据客户端文档配置 |

## 🛠️ 配置方法

### 1. Claude Desktop 配置

**配置文件位置**：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**配置方法**：
```json
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["/full/path/to/torna-mcp/main.py"],
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_1,your_token_2,your_token_3"
      }
    }
  }
}
```

**具体步骤**：
```bash
# 1. 创建或编辑配置文件
mkdir -p ~/Library/Application\ Support/Claude
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << EOF
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["/full/path/to/torna-mcp/main.py"],
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_here"
      }
    }
  }
}
EOF

# 2. 重启 Claude Desktop
```

### 2. Cursor IDE 配置

**配置文件位置**：
- macOS: `~/.cursor/settings.json`
- Windows: `%APPDATA%\Cursor\settings.json`
- Linux: `~/.config/Cursor/settings.json`

**配置方法**：
```json
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["/full/path/to/torna-mcp/main.py"],
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_here"
      }
    }
  }
}
```

**具体步骤**：
```bash
# 1. 编辑Cursor设置文件
mkdir -p ~/.cursor
cat > ~/.cursor/settings.json << EOF
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["/full/path/to/torna-mcp/main.py"],
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_here"
      }
    }
  }
}
EOF

# 2. 重启 Cursor IDE
```

### 3. IFlow CLI 配置

**配置文件位置**：
- `~/.iflow/config.json`

**配置方法**：
```json
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["/full/path/to/torna-mcp/main.py"],
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_here"
      }
    }
  }
}
```

**具体步骤**：
```bash
# 1. 编辑IFlow配置
mkdir -p ~/.iflow
cat > ~/.iflow/config.json << EOF
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["/full/path/to/torna-mcp/main.py"],
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_here"
      }
    }
  }
}
EOF

# 2. 重启 IFlow CLI
```

### 4. VS Code 配置

**配置方法**：
1. 打开VS Code设置 (Cmd/Ctrl + ,)
2. 搜索 "MCP Servers"
3. 在 settings.json 中添加配置

**配置文件位置**：
- `~/.vscode-server/data/User/settings.json`

**配置内容**：
```json
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["/full/path/to/torna-mcp/main.py"],
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_here"
      }
    }
  }
}
```

## 🔧 环境变量配置

### 方法1: 环境变量 (推荐)

**设置环境变量**：
```bash
# 方式1: 在配置文件中设置 (见上方示例)
# 方式2: 设置系统环境变量

# Linux/macOS
export TORNA_URL="http://localhost:7700/api"
export TORNA_TOKENS="your_token_here"

# Windows
set TORNA_URL=http://localhost:7700/api
set TORNA_TOKENS=your_token_here
```

### 方法2: .env 文件

在torna-mcp项目目录中创建 `.env` 文件：
```bash
# .env 文件内容
TORNA_URL=http://localhost:7700/api
TORNA_TOKENS=your_token_here
```

## 📝 完整配置示例

### Linux/macOS 完整配置

```bash
#!/bin/bash
# 自动配置脚本

# 设置Torna MCP Server路径
TORNA_MCP_PATH="/full/path/to/torna-mcp"

# Claude Desktop配置
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << EOF
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["$TORNA_MCP_PATH/main.py"],
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_here"
      }
    }
  }
}
EOF

# Cursor配置
cat > ~/.cursor/settings.json << EOF
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["$TORNA_MCP_PATH/main.py"],
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_here"
      }
    }
  }
}
EOF

# IFlow CLI配置
cat > ~/.iflow/config.json << EOF
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["$TORNA_MCP_PATH/main.py"],
      "env": {
        "TORNA_URL": "http://localhost:7700/api",
        "TORNA_TOKENS": "your_token_here"
      }
    }
  }
}
EOF

echo "✅ 所有MCP客户端配置完成！"
echo "请重启对应的客户端以应用更改。"
```

### Windows 完整配置

```powershell
# PowerShell配置脚本

# 设置Torna MCP Server路径
$TORNA_MCP_PATH = "C:\path\to\torna-mcp"

# 创建配置目录
$ConfigDir = "$env:APPDATA\Claude"
New-Item -ItemType Directory -Force -Path $ConfigDir

# Claude Desktop配置
$ClaudeConfig = @{
    mcpServers = @{
        torna = @{
            command = "python"
            args = @("$TORNA_MCP_PATH\main.py")
            env = @{
                TORNA_URL = "http://localhost:7700/api"
                TORNA_TOKENS = "your_token_here"
            }
        }
    }
}
$ClaudeConfig | ConvertTo-Json -Depth 10 | Set-Content "$ConfigDir\claude_desktop_config.json"

# Cursor配置
$CursorConfig = $ClaudeConfig.Clone()
$CursorConfig | ConvertTo-Json -Depth 10 | Set-Content "$env:APPDATA\Cursor\settings.json"

Write-Host "✅ 所有MCP客户端配置完成！"
Write-Host "请重启对应的客户端以应用更改。"
```

## 🧪 连接测试

### 测试步骤

1. **启动Torna MCP Server**：
```bash
cd /path/to/torna-mcp
python main.py
```

2. **在MCP客户端中测试**：
```
工具: torna_list_documents
参数:
{
  "access_token": "your_token_here",
  "limit": 1
}
```

3. **验证响应**：
- ✅ 成功：返回文档列表信息
- ❌ 失败：检查配置或服务器状态

### 调试方法

1. **检查服务器是否运行**：
```bash
python /path/to/torna-mcp/main.py --help
```

2. **验证配置**：
```bash
python /path/to/torna-mcp/validate_config.py
```

3. **测试网络连接**：
```bash
curl -X POST http://localhost:7700/api -H "Content-Type: application/json" -d '{"name":"doc.list","version":"1.0","data":"{}","access_token":"your_token"}'
```

## 🔍 常见问题解决

### 问题1: "Command not found: python3"

**解决方案**：
```bash
# 检查Python安装
which python3 || which python

# 更新配置中的命令
"command": "python"  # Windows 或
"command": "/usr/bin/python3"  # 完整路径
```

### 问题2: "Permission denied"

**解决方案**：
```bash
# 检查文件权限
chmod +x /path/to/torna-mcp/main.py

# 或在配置中添加完整路径
"command": "/usr/bin/python3"
```

### 问题3: "Environment variable not found"

**解决方案**：
1. 确保环境变量已设置
2. 使用.env文件或配置文件中设置
3. 重新启动客户端

### 问题4: "Module not found: mcp.server.fastmcp"

**解决方案**：
```bash
# 安装依赖
pip install -r requirements.txt

# 或检查Python环境
which python
pip list | grep mcp
```

### 问题5: Torna API 连接失败

**解决方案**：
1. 检查TORNA_URL是否正确
2. 验证网络连接
3. 确认访问令牌有效
4. 检查防火墙设置

## 📱 移动设备配置

### iOS/iPadOS (支持MCP的客户端)

**配置文件位置**：
- 通过客户端设置界面配置
- 或通过共享配置文件

**配置示例**：
```json
{
  "mcpServers": {
    "torna": {
      "command": "python3",
      "args": ["/path/to/torna-mcp/main.py"],
      "env": {
        "TORNA_URL": "https://your-torna-server.com/api",
        "TORNA_TOKENS": "your_mobile_token"
      }
    }
  }
}
```

### Android (支持MCP的客户端)

**配置方法**：
- 通过客户端设置界面配置
- 使用环境变量配置

## 🌐 远程服务器配置

### 配置远程访问

```bash
# 1. 在服务器上启动Torna MCP Server
python main.py --host 0.0.0.0 --port 3000

# 2. 客户端配置
{
  "mcpServers": {
    "torna": {
      "command": "ssh",
      "args": ["user@server", "python /path/to/torna-mcp/main.py"],
      "env": {
        "TORNA_URL": "http://your-torna-server:7700/api",
        "TORNA_TOKENS": "your_token_here"
      }
    }
  }
}
```

## 🔐 安全注意事项

1. **访问令牌安全**：
   - 不要在配置文件中硬编码生产环境令牌
   - 使用环境变量或密钥管理工具
   - 定期轮换访问令牌

2. **网络连接**：
   - 生产环境使用HTTPS
   - 配置防火墙规则
   - 使用VPN或专用网络

3. **文件权限**：
   - 确保配置文件权限安全
   - 限制文件访问权限

## 📞 获取帮助

如需帮助，请：

1. 查看 `RELEASE_STATUS.md` 中的故障排除部分
2. 运行 `python validate_config.py` 诊断问题
3. 检查各客户端的日志输出
4. 访问项目仓库的Issues页面

---

**配置完成后，你就可以在任何MCP客户端中使用Torna MCP Server的所有16个工具函数了！** 🚀