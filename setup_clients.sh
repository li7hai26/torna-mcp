#!/bin/bash
# Torna MCP Server 一键客户端配置脚本
# 支持 Claude Desktop, Cursor, IFlow CLI 等MCP客户端

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印彩色信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${CYAN}=== $1 ===${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 获取绝对路径
get_absolute_path() {
    if [[ -f "$1" ]]; then
        echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
    else
        echo "$1"
    fi
}

# 检查Python版本
check_python() {
    print_info "检查Python环境..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
        print_success "找到 python3: $(which python3)"
    elif command_exists python; then
        PYTHON_CMD="python"
        print_success "找到 python: $(which python)"
    else
        print_error "未找到Python，请先安装Python 3.8+"
        exit 1
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_info "Python版本: $PYTHON_VERSION"
}

# 检查Torna MCP Server
check_torna_server() {
    print_info "检查Torna MCP Server..."
    
    if [[ ! -f "$TORNA_MCP_PATH/main.py" ]]; then
        print_error "Torna MCP Server未找到: $TORNA_MCP_PATH/main.py"
        print_info "请设置正确的路径："
        echo "export TORNA_MCP_PATH=\"/full/path/to/torna-mcp\""
        exit 1
    fi
    
    print_success "找到Torna MCP Server: $TORNA_MCP_PATH/main.py"
}

# 获取用户配置
get_user_config() {
    print_header "配置信息收集"
    
    echo -n "请输入你的Torna服务器地址 (默认: http://localhost:7700/api): "
    read -r TORNA_URL
    TORNA_URL=${TORNA_URL:-"http://localhost:7700/api"}
    
    echo -n "请输入你的Torna访问令牌 (支持多个，用逗号分隔): "
    read -rs TORNA_TOKENS
    echo ""
    
    if [[ -z "$TORNA_TOKENS" ]]; then
        print_error "访问令牌不能为空"
        exit 1
    fi
    
    print_success "配置信息收集完成"
}

# 配置Claude Desktop
configure_claude_desktop() {
    print_header "配置 Claude Desktop"
    
    # 查找配置文件路径
    case "$(uname -s)" in
        Darwin*)
            CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
            CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
            ;;
        Linux*)
            CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
            CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            CLAUDE_CONFIG_DIR="$APPDATA/Claude"
            CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
            ;;
    esac
    
    print_info "Claude配置文件路径: $CLAUDE_CONFIG_FILE"
    
    # 创建配置目录
    mkdir -p "$CLAUDE_CONFIG_DIR"
    
    # 创建或合并配置文件
    if [[ -f "$CLAUDE_CONFIG_FILE" ]]; then
        print_warning "配置文件已存在，将进行备份"
        cp "$CLAUDE_CONFIG_FILE" "$CLAUDE_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        
        # 简单的JSON合并（假设现有配置结构简单）
        print_info "请手动编辑Claude配置文件添加Torna配置"
        print_info "将以下内容添加到claude_desktop_config.json的mcpServers部分："
    else
        # 创建新的配置文件
        cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "torna": {
      "command": "$PYTHON_CMD",
      "args": ["$TORNA_MCP_PATH/main.py"],
      "env": {
        "TORNA_URL": "$TORNA_URL",
        "TORNA_TOKENS": "$TORNA_TOKENS"
      }
    }
  }
}
EOF
        print_success "Claude Desktop配置创建完成"
    fi
    
    # 显示配置内容
    echo -e "\n${YELLOW}配置内容：${NC}"
    cat << EOF
{
  "mcpServers": {
    "torna": {
      "command": "$PYTHON_CMD",
      "args": ["$TORNA_MCP_PATH/main.py"],
      "env": {
        "TORNA_URL": "$TORNA_URL",
        "TORNA_TOKENS": "$TORNA_TOKENS"
      }
    }
  }
}
EOF
}

# 配置Cursor IDE
configure_cursor() {
    print_header "配置 Cursor IDE"
    
    case "$(uname -s)" in
        Darwin*)
            CURSOR_CONFIG_DIR="$HOME/.cursor"
            ;;
        Linux*)
            CURSOR_CONFIG_DIR="$HOME/.config/Cursor"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            CURSOR_CONFIG_DIR="$APPDATA/Cursor"
            ;;
    esac
    
    CURSOR_CONFIG_FILE="$CURSOR_CONFIG_DIR/settings.json"
    
    print_info "Cursor配置文件路径: $CURSOR_CONFIG_FILE"
    
    mkdir -p "$CURSOR_CONFIG_DIR"
    
    if [[ -f "$CURSOR_CONFIG_FILE" ]]; then
        print_warning "配置文件已存在，请手动添加mcpServers配置"
    else
        cat > "$CURSOR_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "torna": {
      "command": "$PYTHON_CMD",
      "args": ["$TORNA_MCP_PATH/main.py"],
      "env": {
        "TORNA_URL": "$TORNA_URL",
        "TORNA_TOKENS": "$TORNA_TOKENS"
      }
    }
  }
}
EOF
        print_success "Cursor IDE配置创建完成"
    fi
}

# 配置IFlow CLI
configure_iflow_cli() {
    print_header "配置 IFlow CLI"
    
    IFLOW_CONFIG_DIR="$HOME/.iflow"
    IFLOW_CONFIG_FILE="$IFLOW_CONFIG_DIR/config.json"
    
    print_info "IFlow CLI配置文件路径: $IFLOW_CONFIG_FILE"
    
    mkdir -p "$IFLOW_CONFIG_DIR"
    
    if [[ -f "$IFLOW_CONFIG_FILE" ]]; then
        print_warning "配置文件已存在，请手动添加mcpServers配置"
    else
        cat > "$IFLOW_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "torna": {
      "command": "$PYTHON_CMD",
      "args": ["$TORNA_MCP_PATH/main.py"],
      "env": {
        "TORNA_URL": "$TORNA_URL",
        "TORNA_TOKENS": "$TORNA_TOKENS"
      }
    }
  }
}
EOF
        print_success "IFlow CLI配置创建完成"
    fi
}

# 配置VS Code
configure_vscode() {
    print_header "配置 VS Code"
    
    VSCODE_CONFIG_DIR="$HOME/.vscode-server/data/User"
    VSCODE_CONFIG_FILE="$VSCODE_CONFIG_DIR/settings.json"
    
    print_info "VS Code配置文件路径: $VSCODE_CONFIG_FILE"
    
    mkdir -p "$VSCODE_CONFIG_DIR"
    
    if [[ -f "$VSCODE_CONFIG_FILE" ]]; then
        print_warning "配置文件已存在，请手动添加mcpServers配置"
    else
        cat > "$VSCODE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "torna": {
      "command": "$PYTHON_CMD",
      "args": ["$TORNA_MCP_PATH/main.py"],
      "env": {
        "TORNA_URL": "$TORNA_URL",
        "TORNA_TOKENS": "$TORNA_TOKENS"
      }
    }
  }
}
EOF
        print_success "VS Code配置创建完成"
    fi
}

# 创建通用配置示例
create_config_examples() {
    print_header "创建通用配置示例"
    
    mkdir -p "$HOME/torna-mcp-configs"
    
    # Claude Desktop配置
    cat > "$HOME/torna-mcp-configs/claude_desktop_config.json" << EOF
{
  "mcpServers": {
    "torna": {
      "command": "$PYTHON_CMD",
      "args": ["$TORNA_MCP_PATH/main.py"],
      "env": {
        "TORNA_URL": "$TORNA_URL",
        "TORNA_TOKENS": "$TORNA_TOKENS"
      }
    }
  }
}
EOF
    
    # Cursor配置
    cat > "$HOME/torna-mcp-configs/cursor_settings.json" << EOF
{
  "mcpServers": {
    "torna": {
      "command": "$PYTHON_CMD",
      "args": ["$TORNA_MCP_PATH/main.py"],
      "env": {
        "TORNA_URL": "$TORNA_URL",
        "TORNA_TOKENS": "$TORNA_TOKENS"
      }
    }
  }
}
EOF
    
    # IFlow CLI配置
    cat > "$HOME/torna-mcp-configs/iflow_config.json" << EOF
{
  "mcpServers": {
    "torna": {
      "command": "$PYTHON_CMD",
      "args": ["$TORNA_MCP_PATH/main.py"],
      "env": {
        "TORNA_URL": "$TORNA_URL",
        "TORNA_TOKENS": "$TORNA_TOKENS"
      }
    }
  }
}
EOF
    
    print_success "通用配置文件已保存到: $HOME/torna-mcp-configs/"
    print_info "复制这些文件到对应客户端的配置目录即可"
}

# 显示配置总结
show_config_summary() {
    print_header "配置完成总结"
    
    echo -e "${GREEN}Torna MCP Server 配置已完成！${NC}\n"
    
    echo -e "${YELLOW}配置信息：${NC}"
    echo "• Python命令: $PYTHON_CMD"
    echo "• Torna MCP路径: $TORNA_MCP_PATH/main.py"
    echo "• Torna服务器: $TORNA_URL"
    echo "• 访问令牌: ${TORNA_TOKENS:0:20}..."
    
    echo -e "\n${YELLOW}配置的文件位置：${NC}"
    
    # Claude Desktop
    case "$(uname -s)" in
        Darwin*)
            CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
            ;;
        Linux*)
            CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            CLAUDE_CONFIG_DIR="$APPDATA/Claude"
            ;;
    esac
    echo "• Claude Desktop: $CLAUDE_CONFIG_DIR/claude_desktop_config.json"
    
    echo "• Cursor IDE: ~/.cursor/settings.json"
    echo "• IFlow CLI: ~/.iflow/config.json"
    echo "• VS Code: ~/.vscode-server/data/User/settings.json"
    echo "• 通用示例: $HOME/torna-mcp-configs/"
    
    echo -e "\n${YELLOW}下一步操作：${NC}"
    echo "1. 重启对应的MCP客户端"
    echo "2. 在客户端中测试连接："
    echo "   工具: torna_list_documents"
    echo "   参数: {\"access_token\": \"your_token\", \"limit\": 1}"
    
    echo -e "\n${YELLOW}故障排除：${NC}"
    echo "• 如果连接失败，请检查："
    echo "  - Python环境是否正确"
    echo "  - Torna服务器是否可访问"
    echo "  - 访问令牌是否有效"
    echo "  - 配置文件路径是否正确"
    
    echo -e "\n${CYAN}🌟 配置成功后，你就可以在任何MCP客户端中使用Torna的所有功能了！${NC}"
}

# 主函数
main() {
    print_header "Torna MCP Server 客户端配置脚本"
    print_info "此脚本将帮你配置各种MCP客户端连接Torna MCP Server"
    
    # 检查参数
    if [[ $# -eq 0 ]]; then
        print_info "使用方法: $0 [选项]"
        print_info "选项:"
        print_info "  --path PATH    指定Torna MCP Server路径"
        print_info "  --url URL      指定Torna服务器URL"
        print_info "  --tokens TOKENS 指定访问令牌"
        print_info "  --all          配置所有支持的客户端"
        print_info "  --help         显示帮助信息"
        exit 0
    fi
    
    # 解析参数
    CONFIG_ALL=false
    while [[ $# -gt 0 ]]; do
        case $1 in
            --path)
                TORNA_MCP_PATH="$2"
                shift 2
                ;;
            --url)
                TORNA_URL="$2"
                shift 2
                ;;
            --tokens)
                TORNA_TOKENS="$2"
                shift 2
                ;;
            --all)
                CONFIG_ALL=true
                shift
                ;;
            --help)
                print_info "使用方法: $0 [选项]"
                print_info "选项:"
                print_info "  --path PATH    指定Torna MCP Server路径"
                print_info "  --url URL      指定Torna服务器URL"
                print_info "  --tokens TOKENS 指定访问令牌"
                print_info "  --all          配置所有支持的客户端"
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    # 设置默认值
    TORNA_MCP_PATH=${TORNA_MCP_PATH:-"$(pwd)"}
    
    # 执行配置
    check_python
    check_torna_server
    get_user_config
    
    if [[ "$CONFIG_ALL" == "true" ]]; then
        configure_claude_desktop
        configure_cursor
        configure_iflow_cli
        configure_vscode
    else
        echo -e "\n${YELLOW}选择要配置的客户端：${NC}"
        echo "1) Claude Desktop"
        echo "2) Cursor IDE" 
        echo "3) IFlow CLI"
        echo "4) VS Code"
        echo "5) 创建通用配置示例"
        echo "6) 配置以上所有客户端"
        
        echo -n "请选择 (1-6): "
        read -r choice
        
        case $choice in
            1) configure_claude_desktop ;;
            2) configure_cursor ;;
            3) configure_iflow_cli ;;
            4) configure_vscode ;;
            5) create_config_examples ;;
            6)
                configure_claude_desktop
                configure_cursor
                configure_iflow_cli
                configure_vscode
                ;;
            *)
                print_error "无效选择"
                exit 1
                ;;
        esac
    fi
    
    create_config_examples
    show_config_summary
}

# 运行主函数
main "$@"