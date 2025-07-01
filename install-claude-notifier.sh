#!/bin/bash

# Claude Code 通知脚本一键安装器
# 自动检查环境、安装依赖、配置通知方式

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo
    echo "=================================================="
    echo -e "${GREEN}$1${NC}"
    echo "=================================================="
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查Python版本
check_python() {
    print_status "检查Python环境..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python已安装: $PYTHON_VERSION"
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_VERSION=$(python --version | cut -d' ' -f2)
        if [[ $PYTHON_VERSION == 3.* ]]; then
            print_success "Python已安装: $PYTHON_VERSION"
            PYTHON_CMD="python"
        else
            print_error "需要Python 3.x，当前版本: $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "未找到Python，请先安装Python 3.x"
        return 1
    fi
}

# 检查pip
check_pip() {
    print_status "检查pip..."
    
    if $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        print_success "pip已可用"
    else
        print_error "pip不可用，尝试安装..."
        # 在macOS上尝试安装pip
        if [[ "$OSTYPE" == "darwin"* ]]; then
            print_status "在macOS上安装pip..."
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            $PYTHON_CMD get-pip.py --user
            rm get-pip.py
        else
            print_error "请手动安装pip"
            return 1
        fi
    fi
}

# 安装Python依赖
install_dependencies() {
    print_status "安装Python依赖包..."
    
    # 尝试安装到用户目录
    if $PYTHON_CMD -m pip install --user requests python-dotenv; then
        print_success "依赖包安装成功"
    else
        print_error "依赖包安装失败"
        return 1
    fi
}

# 检查Claude Code是否安装（可选）
check_claude_code() {
    print_status "检查Claude Code..."
    
    if command_exists claude; then
        CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "未知版本")
        print_success "Claude Code已安装: $CLAUDE_VERSION"
        CLAUDE_INSTALLED=true
    else
        print_warning "未检测到Claude Code命令行工具"
        print_status "您可以稍后安装Claude Code并配置Hooks"
        print_status "下载地址: https://claude.ai/download"
        CLAUDE_INSTALLED=false
    fi
}

# 创建安装目录
setup_directories() {
    print_status "设置安装目录..."
    
    INSTALL_DIR="$HOME/.claude-notifier"
    SCRIPT_PATH="$INSTALL_DIR/claude-notifier.py"
    ENV_PATH="$INSTALL_DIR/.env"
    
    mkdir -p "$INSTALL_DIR"
    print_success "安装目录创建: $INSTALL_DIR"
}

# 下载或复制脚本文件
install_script() {
    print_status "安装通知脚本..."
    
    # 检查当前目录是否有脚本文件
    if [[ -f "claude-notifier.py" ]]; then
        print_status "从当前目录复制脚本文件..."
        cp claude-notifier.py "$SCRIPT_PATH"
        chmod +x "$SCRIPT_PATH"
    else
        print_status "从GitHub下载脚本文件..."
        if command_exists curl; then
            curl -L "https://raw.githubusercontent.com/emptylower/claude-code-/main/claude-notifier.py" -o "$SCRIPT_PATH"
            chmod +x "$SCRIPT_PATH"
        elif command_exists wget; then
            wget -O "$SCRIPT_PATH" "https://raw.githubusercontent.com/emptylower/claude-code-/main/claude-notifier.py"
            chmod +x "$SCRIPT_PATH"
        else
            print_error "需要curl或wget来下载脚本"
            return 1
        fi
    fi
    
    print_success "脚本安装完成: $SCRIPT_PATH"
}

# 配置通知方式
configure_notifications() {
    print_header "配置通知方式"
    
    # 创建.env文件
    cat > "$ENV_PATH" << EOF
# Claude Code 通知脚本环境配置
# 由安装脚本自动生成

EOF

    # macOS系统通知（默认启用）
    print_success "✅ macOS系统通知已启用（无需配置）"
    
    # 询问Server酱普通版
    echo
    print_status "配置Server酱普通版（基础微信通知）"
    echo "访问 https://sc3.ft07.com/ 获取SendKey"
    read -p "是否启用Server酱普通版? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入Server酱SendKey: " SERVER_CHAN_KEY
        if [[ -n "$SERVER_CHAN_KEY" ]]; then
            echo "SERVER_CHAN_KEY=$SERVER_CHAN_KEY" >> "$ENV_PATH"
            print_success "✅ Server酱普通版配置完成"
        fi
    fi
    
    # 询问Server酱Turbo版
    echo
    print_status "配置Server酱Turbo版（推荐，支持微信公众号推送）"
    echo "访问 https://sct.ftqq.com/ 获取SendKey"
    read -p "是否启用Server酱Turbo版? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入Server酱Turbo SendKey: " SERVER_CHAN_TURBO_KEY
        if [[ -n "$SERVER_CHAN_TURBO_KEY" ]]; then
            echo "SERVER_CHAN_TURBO_KEY=$SERVER_CHAN_TURBO_KEY" >> "$ENV_PATH"
            print_success "✅ Server酱Turbo版配置完成"
        fi
    fi
    
    # 询问iOS Bark推送
    echo
    print_status "配置iOS Bark推送（手机通知）"
    echo "1. 在iPhone上安装Bark应用"
    echo "2. 打开应用获取推送URL"
    read -p "是否启用iOS Bark推送? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入Bark推送URL (如: https://api.day.app/YOUR_KEY/): " IOS_PUSH_URL
        if [[ -n "$IOS_PUSH_URL" ]]; then
            echo "IOS_PUSH_URL=$IOS_PUSH_URL" >> "$ENV_PATH"
            # 提取密钥
            IOS_PUSH_KEY=$(echo "$IOS_PUSH_URL" | sed -n 's|.*day\.app/\([^/]*\).*|\1|p')
            if [[ -n "$IOS_PUSH_KEY" ]]; then
                echo "IOS_PUSH_KEY=$IOS_PUSH_KEY" >> "$ENV_PATH"
            fi
            print_success "✅ iOS Bark推送配置完成"
        fi
    fi
    
    echo >> "$ENV_PATH"
    print_success "配置文件保存: $ENV_PATH"
}

# 测试通知功能
test_notifications() {
    print_header "测试通知功能"
    
    read -p "是否测试通知功能? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "发送测试通知..."
        
        # 创建测试JSON输入
        TEST_JSON='{"transcript_path": "/dev/null"}'
        
        if echo "$TEST_JSON" | $PYTHON_CMD "$SCRIPT_PATH"; then
            print_success "测试通知发送完成！请检查各通知渠道"
        else
            print_warning "测试通知可能失败，请检查配置"
        fi
    fi
}

# 显示hooks配置教程
show_hooks_tutorial() {
    print_header "Claude Code Hooks 配置教程"
    
    if [[ "$CLAUDE_INSTALLED" == "true" ]]; then
        cat << EOF
方法一：使用命令行配置 (推荐)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 配置完成时的通知Hook
claude config hooks.Stop '[{"matcher": "", "hooks": [{"type": "command", "command": "$PYTHON_CMD $SCRIPT_PATH"}]}]'

方法二：使用交互式配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 在Claude Code中运行: /hooks
2. 选择 "Stop" 事件
3. 添加新的matcher（留空表示匹配所有）
4. 添加新的hook，命令为: $PYTHON_CMD $SCRIPT_PATH
5. 保存到 "User settings"

方法三：手动编辑配置文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
编辑文件: ~/.claude/settings.json

添加以下配置到 "hooks" 部分：

{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "$PYTHON_CMD $SCRIPT_PATH"
          }
        ]
      }
    ]
  }
}

📋 其他可用的Hook事件：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Stop: Claude完成响应时触发（推荐用于通知）
• Notification: Claude发送通知时触发
• PreToolUse: 工具调用前触发（可用于权限检查）
• PostToolUse: 工具调用后触发（可用于后处理）

🔧 高级配置示例：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 只在特定工具使用后通知
"PostToolUse": [
  {
    "matcher": "Bash|Write|Edit",
    "hooks": [
      {
        "type": "command",
        "command": "$PYTHON_CMD $SCRIPT_PATH"
      }
    ]
  }
]

# 自定义通知事件
"Notification": [
  {
    "matcher": "",
    "hooks": [
      {
        "type": "command", 
        "command": "$PYTHON_CMD $SCRIPT_PATH"
      }
    ]
  }
]

EOF
    else
        cat << EOF
⚠️  请先安装Claude Code命令行工具
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
下载地址: https://claude.ai/download

安装Claude Code后，使用以下方法配置Hooks：

方法一：使用命令行配置 (推荐)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 配置完成时的通知Hook
claude config hooks.Stop '[{"matcher": "", "hooks": [{"type": "command", "command": "$PYTHON_CMD $SCRIPT_PATH"}]}]'

方法二：使用交互式配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 在Claude Code中运行: /hooks
2. 选择 "Stop" 事件
3. 添加新的matcher（留空表示匹配所有）
4. 添加新的hook，命令为: $PYTHON_CMD $SCRIPT_PATH
5. 保存到 "User settings"

方法三：手动编辑配置文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
编辑文件: ~/.claude/settings.json

添加以下配置到 "hooks" 部分：

{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "$PYTHON_CMD $SCRIPT_PATH"
          }
        ]
      }
    ]
  }
}
EOF
    fi
    
    cat << EOF

🚀 快速测试Hook：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
配置完成后，在Claude Code中执行任意命令，完成后应该会收到通知。

📁 相关文件路径：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 脚本文件: $SCRIPT_PATH
• 配置文件: $ENV_PATH
• Claude配置: ~/.claude/settings.json

🔍 故障排除：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 查看Claude设置: claude config list
• 测试脚本: echo '{"transcript_path": "/dev/null"}' | $PYTHON_CMD $SCRIPT_PATH
• 查看日志: 在Claude Code中按Ctrl-R查看transcript模式
EOF

    echo
    print_success "🎉 安装完成！"
    echo
    print_status "接下来请按照上述教程配置Claude Code Hooks"
    print_status "配置完成后，Claude Code执行完任务时会自动发送通知"
}

# 主安装流程
main() {
    print_header "Claude Code 通知脚本安装器"
    echo "自动检查环境、安装依赖、配置通知方式"
    echo
    
    # 环境检查
    print_header "环境检查"
    check_python || exit 1
    check_pip || exit 1
    check_claude_code
    
    # 安装依赖
    print_header "安装依赖"
    install_dependencies || exit 1
    
    # 设置安装目录
    setup_directories
    
    # 安装脚本
    install_script || exit 1
    
    # 配置通知
    configure_notifications
    
    # 测试功能
    test_notifications
    
    # 显示配置教程
    show_hooks_tutorial
}

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
    print_error "请不要以root用户运行此脚本"
    exit 1
fi

# 运行主程序
main "$@"