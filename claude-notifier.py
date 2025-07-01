#!/usr/bin/env python3
"""
Claude Code 完成通知脚本
支持多种通知方式：系统通知、推送到手机、邮件等
"""

import json
import sys
import subprocess
import os
import re
import requests
from datetime import datetime
from typing import Tuple, Dict, Any
# 尝试加载环境变量，如果没有dotenv包则跳过
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 如果没有dotenv，直接从系统环境变量读取
    print("Warning: python-dotenv not installed. Using system environment variables only.", file=sys.stderr)


class NotificationConfig:
    """通知配置类"""
    
    # macOS 系统通知设置
    ENABLE_SYSTEM_NOTIFICATION = True
    
    # iOS 推送配置 (使用 Bark 或类似服务)
    ENABLE_IOS_PUSH = os.getenv('IOS_PUSH_URL', '').strip() != ''
    IOS_PUSH_URL = os.getenv('IOS_PUSH_URL', 'YOUR_BARK_URL')
    IOS_PUSH_KEY = os.getenv('IOS_PUSH_KEY', 'YOUR_PUSH_KEY')
    
    # Server酱配置 (普通版本)
    ENABLE_SERVER_CHAN = os.getenv('SERVER_CHAN_KEY', '').strip() != ''
    SERVER_CHAN_KEY = os.getenv('SERVER_CHAN_KEY', 'YOUR_SERVER_CHAN_KEY')
    
    # Server酱Turbo配置 (支持微信公众号推送)
    ENABLE_SERVER_CHAN_TURBO = os.getenv('SERVER_CHAN_TURBO_KEY', '').strip() != ''
    SERVER_CHAN_TURBO_KEY = os.getenv('SERVER_CHAN_TURBO_KEY', 'YOUR_SERVER_CHAN_TURBO_KEY')


class ClaudeNotifier:
    """Claude Code 通知器"""
    
    def __init__(self):
        self.config = NotificationConfig()
    
    def analyze_completion_status(self, transcript_path: str) -> Tuple[str, str, str]:
        """
        分析对话记录判断完成状态 - 重点关注最后的输出内容
        返回: (状态类型, 标题, 详细信息)
        """
        try:
            expanded_path = os.path.expanduser(transcript_path)
            if not os.path.exists(expanded_path):
                return "unknown", "Claude 完成响应", "无法访问对话记录"
            
            with open(expanded_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 只分析最后500字符的内容，重点关注最终输出
            recent_content = content[-500:]
            recent_lower = recent_content.lower()
            
            # 优先检测明显的错误标识（API ERROR等红色警告）
            critical_error_patterns = [
                (r'api error|api_error', "api_error", "API调用错误"),
                (r'authentication.*failed|auth.*error', "auth_error", "认证失败"),
                (r'rate.*limit.*exceeded|too many requests', "rate_limit", "请求频率超限"),
                (r'network.*error|connection.*error', "network_error", "网络连接错误"),
                (r'timeout.*error|request.*timeout', "timeout_error", "请求超时"),
            ]
            
            for pattern, error_type, description in critical_error_patterns:
                if re.search(pattern, recent_lower):
                    return error_type, f"🚨 {description}", self._extract_recent_lines(content, 5)
            
            # 检测需要用户交互的停止情况
            interaction_patterns = [
                (r'permission.*required|grant.*permission|allow.*access', "permission_required", "需要授予权限"),
                (r'please.*confirm|confirm.*\(y/n\)|do you want to', "confirmation_required", "需要用户确认"),
                (r'enter.*password|provide.*credentials', "credentials_required", "需要输入凭据"),
                (r'waiting.*for.*input|please.*provide', "input_required", "等待用户输入"),
                (r'press.*any.*key|press.*enter', "key_required", "等待按键确认"),
            ]
            
            for pattern, interaction_type, description in interaction_patterns:
                if re.search(pattern, recent_lower):
                    return interaction_type, f"⏸️ {description}", self._extract_recent_lines(content, 3)
            
            # 检测严重错误（但不是API错误）
            error_patterns = [
                (r'fatal.*error|critical.*error', "fatal_error", "严重错误"),
                (r'command.*not.*found|no such file', "command_error", "命令或文件未找到"),
                (r'permission.*denied|access.*denied', "permission_denied", "权限被拒绝"),
                (r'out of memory|memory.*error', "memory_error", "内存不足"),
            ]
            
            for pattern, error_type, description in error_patterns:
                if re.search(pattern, recent_lower):
                    return error_type, f"❌ {description}", self._extract_recent_lines(content, 5)
            
            # 检测成功完成的明确标识
            success_patterns = [
                (r'successfully.*completed|task.*completed.*successfully', "success", "任务成功完成"),
                (r'tests?.*passed|all.*tests.*pass', "test_success", "测试通过"),
                (r'build.*successful|compilation.*successful', "build_success", "构建成功"),
                (r'deployed.*successfully|deployment.*complete', "deploy_success", "部署成功"),
                (r'committed.*successfully|pushed.*successfully', "git_success", "代码提交成功"),
            ]
            
            for pattern, success_type, description in success_patterns:
                if re.search(pattern, recent_lower):
                    return success_type, f"✅ {description}", self._extract_recent_lines(content, 3)
            
            # 默认完成状态
            return "completed", "🤖 Claude 完成响应", "检查终端查看详细结果"
            
        except Exception as e:
            return "error", "❌ 分析失败", f"无法分析对话记录: {str(e)}"
    
    def _extract_recent_lines(self, content: str, num_lines: int = 3) -> str:
        """提取文件最后几行内容"""
        lines = content.split('\n')
        recent_lines = lines[-num_lines:] if len(lines) >= num_lines else lines
        
        # 过滤空行并格式化
        meaningful_lines = []
        for line in recent_lines:
            stripped = line.strip()
            if stripped and len(stripped) > 5:  # 过滤太短的行
                meaningful_lines.append(stripped)
        
        if meaningful_lines:
            return '\n'.join(meaningful_lines)
        return "检查终端查看详细信息"
    
    def _extract_error_details(self, content: str) -> str:
        """提取错误详情"""
        lines = content.split('\n')
        error_lines = []
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                # 提取错误行及其前后几行
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                error_context = lines[start:end]
                error_lines.extend(error_context)
                break
        
        if error_lines:
            return '\n'.join(error_lines[-5:])  # 最多返回5行
        return "检查终端查看详细错误信息"
    
    def _extract_success_details(self, content: str) -> str:
        """提取成功详情"""
        lines = content.split('\n')
        recent_lines = lines[-10:]  # 最后10行
        
        # 查找有意义的输出
        meaningful_lines = []
        for line in recent_lines:
            if line.strip() and not line.startswith('//') and len(line.strip()) > 10:
                meaningful_lines.append(line.strip())
        
        if meaningful_lines:
            return '\n'.join(meaningful_lines[-3:])  # 最多返回3行
        return "任务已成功完成"
    
    def send_system_notification(self, title: str, message: str, status_type: str = "completed"):
        """发送系统通知"""
        try:
            if sys.platform == "darwin":  # macOS
                # 根据状态类型选择不同的图标
                sound = "default"
                if "error" in status_type:
                    sound = "Basso"
                elif "success" in status_type:
                    sound = "Glass"
                
                script = f'''
                osascript -e 'display notification "{message}" with title "{title}" sound name "{sound}"'
                '''
                subprocess.run(script, shell=True, capture_output=True)
                
            elif sys.platform == "linux":  # Linux
                # 根据状态类型选择不同的图标
                icon = "dialog-information"
                if "error" in status_type:
                    icon = "dialog-error"
                elif "success" in status_type:
                    icon = "dialog-information"
                
                subprocess.run([
                    "notify-send", 
                    "--icon", icon,
                    "--app-name", "Claude Code",
                    title, 
                    message
                ], capture_output=True)
                
            elif sys.platform == "win32":  # Windows
                # Windows 通知（需要安装 plyer 或使用 win10toast）
                try:
                    import win10toast
                    toaster = win10toast.ToastNotifier()
                    toaster.show_toast(title, message, duration=10)
                except ImportError:
                    print(f"Windows notification: {title} - {message}")
                    
        except Exception as e:
            print(f"系统通知发送失败: {e}", file=sys.stderr)
    
    def send_server_chan_notification(self, title: str, message: str, status_type: str = "completed"):
        """通过 Server酱 发送通知"""
        try:
            # Server酱 API URL
            url = f"https://sctapi.ftqq.com/{self.config.SERVER_CHAN_KEY}.send"
            
            # 根据状态类型选择emoji
            emoji = "🤖"
            if "error" in status_type:
                emoji = "❌"
            elif "success" in status_type:
                emoji = "✅"
            
            # 格式化消息
            formatted_title = f"{emoji} {title}"
            formatted_message = f"{message}\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            data = {
                "title": formatted_title,
                "desp": formatted_message
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code != 200:
                print(f"Server酱 通知发送失败: {response.text}", file=sys.stderr)
            else:
                result = response.json()
                if result.get('code') != 0:
                    print(f"Server酱 通知发送失败: {result.get('message', 'Unknown error')}", file=sys.stderr)
                
        except Exception as e:
            print(f"Server酱 通知发送失败: {e}", file=sys.stderr)
    
    def send_server_chan_turbo_notification(self, title: str, message: str, status_type: str = "completed"):
        """通过 Server酱Turbo 发送微信公众号通知"""
        try:
            # Server酱Turbo API URL
            url = f"https://sctapi.ftqq.com/{self.config.SERVER_CHAN_TURBO_KEY}.send"
            
            # 根据状态类型选择emoji
            emoji = "🤖"
            if "error" in status_type:
                emoji = "❌"
            elif "success" in status_type:
                emoji = "✅"
            
            # 格式化消息 - Turbo版本支持Markdown
            formatted_title = f"{emoji} {title}"
            formatted_message = f"**{message}**\n\n---\n\n⏰ 时间: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n📡 来源: Claude Code Notifier"
            
            # 使用GET请求（推荐方式）
            params = {
                "title": formatted_title,
                "desp": formatted_message
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"Server酱Turbo 通知发送失败: {response.text}", file=sys.stderr)
            else:
                result = response.json()
                if result.get('code') != 0:
                    print(f"Server酱Turbo 通知发送失败: {result.get('message', 'Unknown error')}", file=sys.stderr)
                else:
                    # 成功时可以显示推送ID
                    push_id = result.get('data', {}).get('pushid', '')
                    if push_id:
                        print(f"Server酱Turbo 通知发送成功, 推送ID: {push_id}")
                
        except Exception as e:
            print(f"Server酱Turbo 通知发送失败: {e}", file=sys.stderr)
    
    def send_ios_push_notification(self, title: str, message: str, status_type: str = "completed"):
        """通过 Bark 或类似服务发送 iOS 推送"""
        try:
            # 根据状态类型选择emoji和声音
            emoji = "🤖"
            sound = "default"
            if "error" in status_type:
                emoji = "❌"
                sound = "alarm"
            elif "success" in status_type:
                emoji = "✅"
                sound = "bell"
            
            # 格式化标题和消息
            formatted_title = f"{emoji} {title}"
            formatted_message = f"{message}\n\n{datetime.now().strftime('%H:%M:%S')}"
            
            # 构造 Bark URL (例如: https://api.day.app/YOUR_KEY/title/body)
            import urllib.parse
            encoded_title = urllib.parse.quote(formatted_title)
            encoded_message = urllib.parse.quote(formatted_message)
            
            # 如果是完整的 Bark URL
            if self.config.IOS_PUSH_URL.startswith('http'):
                if self.config.IOS_PUSH_URL.endswith('/'):
                    url = f"{self.config.IOS_PUSH_URL}{encoded_title}/{encoded_message}"
                else:
                    url = f"{self.config.IOS_PUSH_URL}/{encoded_title}/{encoded_message}"
            else:
                # 如果只是 key，构造完整 URL
                url = f"https://api.day.app/{self.config.IOS_PUSH_KEY}/{encoded_title}/{encoded_message}"
            
            # 添加参数
            params = {
                "sound": sound,
                "group": "ClaudeCode"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"iOS 推送发送失败: {response.text}", file=sys.stderr)
            else:
                result = response.json()
                if result.get('code') != 200:
                    print(f"iOS 推送发送失败: {result.get('message', 'Unknown error')}", file=sys.stderr)
                
        except Exception as e:
            print(f"iOS 推送发送失败: {e}", file=sys.stderr)
    
    
    def send_all_notifications(self, title: str, message: str, status_type: str = "completed"):
        """发送所有启用的通知"""
        if self.config.ENABLE_SYSTEM_NOTIFICATION:
            self.send_system_notification(title, message, status_type)
        
        if self.config.ENABLE_IOS_PUSH:
            self.send_ios_push_notification(title, message, status_type)
        
        if self.config.ENABLE_SERVER_CHAN:
            self.send_server_chan_notification(title, message, status_type)
        
        if self.config.ENABLE_SERVER_CHAN_TURBO:
            self.send_server_chan_turbo_notification(title, message, status_type)


def main():
    """主函数"""
    try:
        # 读取输入数据
        input_data = json.load(sys.stdin)
        
        # 创建通知器
        notifier = ClaudeNotifier()
        
        # 分析完成状态
        transcript_path = input_data.get("transcript_path", "")
        status_type, title, message = notifier.analyze_completion_status(transcript_path)
        
        # 发送通知
        notifier.send_all_notifications(title, message, status_type)
        
        # 输出到控制台（用于调试）
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {title}: {message}")
        
    except json.JSONDecodeError:
        print("错误: 无效的 JSON 输入", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # 即使出错也发送通知
        try:
            notifier = ClaudeNotifier()
            notifier.send_system_notification(
                "Claude Code 通知脚本错误", 
                f"通知脚本执行失败: {str(e)}", 
                "error"
            )
        except:
            pass
        print(f"通知脚本错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()