# 一键安装 Claude Code 通知脚本

## 快速安装

```bash
# 方法一：如果已经clone了仓库
cd claude-code-notifier
chmod +x install-claude-notifier.sh
./install-claude-notifier.sh

# 方法二：直接从GitHub下载并运行
curl -fsSL https://raw.githubusercontent.com/emptylower/claude-code-/main/install-claude-notifier.sh | bash
```

## 安装脚本功能

### 🔍 自动环境检查
- ✅ Python 3.x 版本检测
- ✅ pip 包管理器检查
- ✅ Claude Code 命令行工具检测
- ✅ 自动安装缺失的依赖

### 📦 依赖安装
- ✅ 自动安装 `requests` 库
- ✅ 自动安装 `python-dotenv` 库
- ✅ 支持用户目录安装（无需sudo）

### ⚙️ 智能配置
- ✅ 交互式配置各种通知方式
- ✅ 自动生成 `.env` 配置文件
- ✅ 验证配置正确性

### 🔔 支持的通知方式
- ✅ **macOS系统通知**（自动启用）
- ✅ **Server酱普通版**（基础微信通知）
- ✅ **Server酱Turbo版**（推荐，微信公众号推送）
- ✅ **iOS Bark推送**（手机通知）

### 🧪 功能测试
- ✅ 安装后自动测试通知功能
- ✅ 验证各通知渠道是否正常工作

### 📖 配置教程
- ✅ 详细的Claude Code Hooks配置说明
- ✅ 多种配置方法（命令行/交互式/手动）
- ✅ 故障排除指南

## 安装后配置

安装完成后，脚本会显示详细的Claude Code Hooks配置教程。最简单的配置方法：

```bash
# 配置Claude Code在完成任务时发送通知
claude config hooks.Stop '[{"matcher": "", "hooks": [{"type": "command", "command": "python3 ~/.claude-notifier/claude-notifier.py"}]}]'
```

## 文件位置

安装后的文件位置：
- 脚本文件：`~/.claude-notifier/claude-notifier.py`
- 配置文件：`~/.claude-notifier/.env`
- Claude配置：`~/.claude/settings.json`

## 测试安装

```bash
# 测试通知脚本
echo '{"transcript_path": "/dev/null"}' | python3 ~/.claude-notifier/claude-notifier.py

# 查看Claude配置
claude config list | grep hooks
```

## 故障排除

如果遇到问题：

1. **权限错误**：确保脚本有执行权限
2. **Python错误**：确保Python 3.x已安装
3. **网络错误**：检查网络连接和防火墙设置
4. **配置错误**：重新运行安装脚本重新配置

## 卸载

```bash
# 删除安装文件
rm -rf ~/.claude-notifier

# 清除Claude Code配置（可选）
claude config unset hooks.Stop
```