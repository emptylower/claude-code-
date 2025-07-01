# Claude Code 通知脚本

Claude Code 完成后自动发送通知的脚本，支持多种通知方式。

## 支持的通知方式

- **macOS 系统通知**: 本地桌面通知
- **iOS 推送通知**: 通过 Bark 应用推送到 iPhone
- **Server酱通知**: 推送到微信（普通版本）
- **Server酱Turbo通知**: 推送到微信公众号（Turbo版本，支持Markdown格式）

## 安装依赖

```bash
pip install requests python-dotenv
```

## 配置方法

1. 复制配置文件模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的配置：

### Server酱配置

#### 普通版Server酱
- 访问 [https://sc3.ft07.com/](https://sc3.ft07.com/)
- 微信扫码登录获取 SendKey
- 在 `.env` 中设置：`SERVER_CHAN_KEY=你的密钥`

#### Turbo版Server酱（推荐）
- 访问 [https://sct.ftqq.com/](https://sct.ftqq.com/)
- 微信扫码登录获取 SendKey
- 在 `.env` 中设置：`SERVER_CHAN_TURBO_KEY=你的Turbo密钥`
- 支持微信公众号推送，支持Markdown格式
- 与普通版本互不影响，可同时使用

### iOS Bark推送配置
- 在 iPhone 上安装 Bark 应用
- 获取推送 URL（如：`https://api.day.app/YOUR_KEY/`）
- 在 `.env` 中设置：`IOS_PUSH_URL=你的Bark_URL`

## 使用方法

脚本会自动从 `.env` 文件读取配置，只有配置了相应密钥的通知方式才会启用。

## 使用技巧

### 1. 快速测试

创建测试脚本验证通知是否正常：

```bash
# 创建测试JSON输入
echo '{"transcript_path": "/dev/null"}' | python3 ~/scripts/claude-notifier.py
```

### 2. 在Claude Code中集成

将脚本设置为Claude Code的完成hook：

```bash
# 添加到Claude Code配置
claude config set completion_hook "python3 ~/scripts/claude-notifier.py"
```

### 3. 自定义通知内容

脚本会智能分析Claude的执行结果：
- ✅ **成功模式**: 检测到 "completed successfully"、"tests passed" 等
- ❌ **错误模式**: 检测到 "error"、"failed"、"exception" 等  
- ⏳ **等待模式**: 检测到 "waiting for input"、"please provide" 等
- 🤖 **默认模式**: 其他情况显示为 "Claude 完成响应"

### 4. 通知方式选择建议

- **macOS系统通知**: 适合本地开发，即时提醒
- **iOS Bark推送**: 适合移动办公，随时接收
- **Server酱普通版**: 基础微信通知
- **Server酱Turbo版**: 推荐使用，支持微信公众号推送，格式更美观

### 5. 批量配置技巧

可以通过环境变量批量配置，无需修改代码：

```bash
# 临时启用所有通知
export SERVER_CHAN_KEY="your_key"
export SERVER_CHAN_TURBO_KEY="your_turbo_key" 
export IOS_PUSH_URL="your_bark_url"
python3 ~/scripts/claude-notifier.py
```

### 6. 故障排除

- **权限问题**: 确保脚本有执行权限 `chmod +x claude-notifier.py`
- **网络问题**: 检查防火墙设置和网络连接
- **密钥无效**: 重新生成SendKey或Bark密钥
- **依赖缺失**: 运行 `pip install requests python-dotenv`

### 7. 高级用法

#### 自定义过滤器
脚本支持通过修改正则表达式来自定义状态检测：

```python
# 在error_patterns中添加自定义错误模式
(r'your_custom_error_pattern', "custom_error", "自定义错误描述")
```

#### 日志记录
脚本会输出执行日志到stderr，可以重定向保存：

```bash
echo '{}' | python3 claude-notifier.py 2>> ~/logs/claude-notifications.log
```

### 8. 性能优化

- 脚本支持并发发送多种通知
- 每个通知方式有10秒超时保护
- 失败的通知不会影响其他通知方式

## 安全说明

- `.env` 文件已加入 `.gitignore`，不会被提交到仓库
- 使用环境变量管理敏感配置，确保安全性
- 支持容错模式，没有dotenv包时自动降级到系统环境变量