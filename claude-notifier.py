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
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class NotificationConfig:
    """通知配置类"""
    
    # macOS 系统通知设置
    ENABLE_SYSTEM_NOTIFICATION = True
    
    # iOS 推送配置 (使用 Bark 或类似服务)
    ENABLE_IOS_PUSH = os.getenv('IOS_PUSH_URL', '').strip() != ''
    IOS_PUSH_URL = os.getenv('IOS_PUSH_URL', 'YOUR_BARK_URL')
    IOS_PUSH_KEY = os.getenv('IOS_PUSH_KEY', 'YOUR_PUSH_KEY')
    
    # Server酱配置
    ENABLE_SERVER_CHAN = os.getenv('SERVER_CHAN_KEY', '').strip() != ''
    SERVER_CHAN_KEY = os.getenv('SERVER_CHAN_KEY', 'YOUR_SERVER_CHAN_KEY')


class ClaudeNotifier:
    """Claude Code 通知器"""
    
    def __init__(self):
        self.config = NotificationConfig()
    
    def analyze_completion_status(self, transcript_path: str) -> Tuple[str, str, str]:
        """
        分析对话记录判断完成状态
        返回: (状态类型, 标题, 详细信息)
        """
        try:
            expanded_path = os.path.expanduser(transcript_path)
            if not os.path.exists(expanded_path):
                return "unknown", "Claude 完成响应", "无法访问对话记录"
            
            with open(expanded_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分析最后的内容（最近的2000字符）
            recent_content = content[-2000:].lower()
            
            # 错误模式检测
            error_patterns = [
                (r'error|failed|exception|traceback', "error", "遇到错误"),
                (r'permission denied|access denied', "permission", "权限被拒绝"),
                (r'not found|cannot find|missing', "missing", "文件或资源未找到"),
                (r'timeout|timed out', "timeout", "操作超时"),
                (r'connection.*refused|network.*error', "network", "网络连接问题"),
            ]
            
            for pattern, error_type, description in error_patterns:
                if re.search(pattern, recent_content):
                    return error_type, f"❌ {description}", self._extract_error_details(content)
            
            # 成功完成模式检测
            success_patterns = [
                (r'completed successfully|task completed|finished successfully', "success", "任务成功完成"),
                (r'tests? passed|all tests pass', "test_success", "测试通过"),
                (r'deployed successfully|deployment complete', "deploy_success", "部署成功"),
                (r'build successful|compilation successful', "build_success", "构建成功"),
                (r'committed|pushed to|git push', "git_success", "代码已提交"),
            ]
            
            for pattern, success_type, description in success_patterns:
                if re.search(pattern, recent_content):
                    return success_type, f"✅ {description}", self._extract_success_details(content)
            
            # 等待输入模式检测
            if re.search(r'waiting for.*input|please provide|enter.*:', recent_content):
                return "waiting", "⏳ 等待输入", "Claude 正在等待你的输入"
            
            # 默认完成状态
            return "completed", "🤖 Claude 完成响应", "检查终端查看详细结果"
            
        except Exception as e:
            return "error", "❌ 分析失败", f"无法分析对话记录: {str(e)}"
    
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