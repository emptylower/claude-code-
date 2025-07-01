# Claude Code 通知脚本

Claude Code 完成后自动发送通知的脚本，支持多种通知方式。

## 支持的通知方式

- **macOS 系统通知**: 本地桌面通知
- **iOS 推送通知**: 通过 Bark 应用推送到 iPhone
- **Server酱通知**: 推送到微信

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
- 访问 [https://sc3.ft07.com/](https://sc3.ft07.com/)
- 微信扫码登录获取 SendKey
- 在 `.env` 中设置：`SERVER_CHAN_KEY=你的密钥`

### iOS Bark推送配置
- 在 iPhone 上安装 Bark 应用
- 获取推送 URL（如：`https://api.day.app/YOUR_KEY/`）
- 在 `.env` 中设置：`IOS_PUSH_URL=你的Bark_URL`

## 使用方法

脚本会自动从 `.env` 文件读取配置，只有配置了相应密钥的通知方式才会启用。

## 安全说明

- `.env` 文件已加入 `.gitignore`，不会被提交到仓库
- 使用环境变量管理敏感配置，确保安全性