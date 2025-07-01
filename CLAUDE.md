# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code notification system that automatically sends notifications when Claude Code completes tasks. It supports multiple notification channels including macOS system notifications, iOS push notifications via Bark, and WeChat notifications via Server酱 (both regular and Turbo versions).

## Core Architecture

### Main Components

- **`claude-notifier.py`**: The core notification script that analyzes Claude Code transcripts and sends notifications through configured channels
- **`install-claude-notifier.sh`**: Automated installation script that handles environment setup, dependency installation, and user configuration
- **`.env`**: Configuration file containing API keys and notification settings (git-ignored for security)
- **`.env.example`**: Template showing required configuration variables

### Notification Flow

1. **Transcript Analysis**: Script receives JSON input with `transcript_path` from Claude Code hooks
2. **Status Detection**: Analyzes transcript content using regex patterns to determine completion status:
   - Success patterns: "completed successfully", "tests passed", etc.
   - Error patterns: "error", "failed", "exception", etc.  
   - Waiting patterns: "waiting for input", "please provide", etc.
3. **Multi-Channel Dispatch**: Sends notifications concurrently to all enabled channels
4. **Error Handling**: Each notification channel has 10-second timeout and independent error handling

### Configuration System

- **Environment-based**: Uses `python-dotenv` for `.env` file loading with fallback to system environment variables
- **Auto-detection**: Notification channels are automatically enabled when corresponding API keys are configured
- **Security**: Sensitive credentials stored in git-ignored `.env` file

## Development Commands

### Testing the Notification System

```bash
# Test notifications with sample input
echo '{"transcript_path": "/dev/null"}' | python3 claude-notifier.py

# Test specific notification channels by setting environment variables
SERVER_CHAN_KEY="your_key" python3 claude-notifier.py < test_input.json
```

### Installation and Setup

```bash
# Automated installation (recommended)
./install-claude-notifier.sh

# Manual dependency installation
pip install requests python-dotenv

# Configuration setup
cp .env.example .env
# Edit .env with actual API keys
```

### Claude Code Integration

```bash
# Configure Stop hook (triggers when Claude completes tasks)
claude config hooks.Stop '[{"matcher": "", "hooks": [{"type": "command", "command": "python3 ~/.claude-notifier/claude-notifier.py"}]}]'

# Configure Notification hook (triggers on Claude notifications) 
claude config hooks.Notification '[{"matcher": "", "hooks": [{"type": "command", "command": "python3 ~/.claude-notifier/claude-notifier.py"}]}]'
```

## Key Implementation Details

### Status Analysis Logic
The script uses regex patterns to intelligently categorize Claude's execution results:
- **Error Detection**: Matches error keywords and extracts context lines
- **Success Detection**: Identifies completion indicators and extracts meaningful output
- **Smart Formatting**: Different notification channels get optimized message formats (Turbo version supports Markdown)

### Notification Channels
- **macOS System**: Uses `osascript` with different sounds based on status
- **iOS Bark**: REST API calls to `api.day.app` with URL encoding
- **Server酱 Regular**: POST to `sctapi.ftqq.com` with basic formatting  
- **Server酱 Turbo**: GET requests with Markdown support and push ID tracking

### Error Recovery
- **Graceful Degradation**: Missing `python-dotenv` doesn't break functionality
- **Independent Channels**: Failure in one notification method doesn't affect others
- **Timeout Protection**: All HTTP requests have 10-second timeouts

## File Structure Notes

- Installation creates files in `~/.claude-notifier/` directory
- Configuration stored separately from source code for security
- Git ignores all sensitive configuration files
- Install script handles multiple installation methods (direct download, local clone)

## Environment Variables

Required for respective notification channels:
- `SERVER_CHAN_KEY`: Server酱 regular version SendKey
- `SERVER_CHAN_TURBO_KEY`: Server酱 Turbo version SendKey  
- `IOS_PUSH_URL`: Bark app push URL (e.g., `https://api.day.app/YOUR_KEY/`)
- `IOS_PUSH_KEY`: Extracted from Bark URL for fallback usage