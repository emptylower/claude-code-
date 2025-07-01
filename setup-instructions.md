# Claude Code 推送通知设置指南

## 📋 已完成的设置

✅ 创建了智能通知脚本 `~/scripts/claude-notifier.py`  
✅ 设置了脚本执行权限  
✅ 创建了 hooks 配置示例  

## 🚀 如何启用通知

### 1. 基础系统通知（立即可用）

脚本已经支持系统通知，无需额外配置：
- **macOS**: 使用 `osascript` 发送通知
- **Linux**: 使用 `notify-send` 发送通知  
- **Windows**: 支持 `win10toast`（需安装）

### 2. 配置 Claude Code Hooks

在 Claude Code 中运行：
```bash
/hooks
```

然后：
1. 选择 `Stop` 事件
2. 添加 matcher（留空表示匹配所有）
3. 添加 hook 命令：`python3 ~/scripts/claude-notifier.py`
4. 保存到用户设置

或者手动编辑 `~/.claude/settings.json`，添加：
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/scripts/claude-notifier.py"
          }
        ]
      }
    ]
  }
}
```

### 3. 手机推送设置（可选）

#### Pushover（推荐）
1. 访问 https://pushover.net/ 注册账户
2. 创建应用获取 App Token
3. 编辑脚本，修改配置：
```python
ENABLE_PUSHOVER = True
PUSHOVER_APP_TOKEN = "你的App Token"
PUSHOVER_USER_KEY = "你的User Key"
```

#### Telegram Bot
1. 在 Telegram 中找到 @BotFather
2. 创建 bot 获取 Token
3. 获取你的 Chat ID（发送消息给 @userinfobot）
4. 编辑脚本配置：
```python
ENABLE_TELEGRAM = True
TELEGRAM_BOT_TOKEN = "你的Bot Token"
TELEGRAM_CHAT_ID = "你的Chat ID"
```

### 4. 邮件通知设置（可选）

适用于 Gmail：
1. 开启两步验证
2. 生成应用专用密码
3. 编辑脚本配置：
```python
ENABLE_EMAIL = True
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
EMAIL_TO = "your-email@gmail.com"
```

## 🧪 测试通知

1. 启动 Claude Code
2. 执行一个简单命令：`ls`
3. 等待 Claude 完成响应
4. 应该收到通知："🤖 Claude 完成响应"

## 🎯 通知类型

脚本会自动识别以下状态：

| 状态 | 图标 | 说明 |
|------|------|------|
| ❌ 错误 | 错误音效 | 遇到错误、权限问题等 |
| ✅ 成功 | 成功音效 | 任务完成、测试通过、部署成功 |
| ⏳ 等待 | 默认音效 | 等待用户输入 |
| 🤖 完成 | 默认音效 | 正常完成响应 |

## 📁 文件位置

- 主脚本: `~/scripts/claude-notifier.py`
- 配置示例: `~/scripts/claude-hooks-config.json`
- 说明文档: `~/scripts/setup-instructions.md`

## 🔧 自定义配置

可以编辑脚本顶部的 `NotificationConfig` 类来调整：
- 启用/禁用不同的通知方式
- 修改推送服务的配置
- 调整通知的触发条件

## 🐛 故障排除

1. **权限问题**: 确保脚本有执行权限 `chmod +x ~/scripts/claude-notifier.py`
2. **Python 模块**: 如需手机推送，安装 requests: `pip install requests`
3. **系统通知**: macOS 确保允许终端发送通知
4. **Hook 不生效**: 重启 Claude Code 让配置生效

## 📝 使用小贴士

- 脚本会分析对话内容智能判断状态
- 支持多种通知方式同时启用
- 通知内容包含简要的执行结果
- 可以根据不同项目设置不同的通知规则