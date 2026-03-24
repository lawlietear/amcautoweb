# -*- coding: utf-8 -*-
"""
通知模块
支持企业微信、日志记录等
"""

import json
import requests
import datetime
from pathlib import Path


class Notification:
    """通知管理类"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.webhook_url = self.config.get('webhook_url', '')
        self.audit_log_file = self.config.get('audit_log_file', 'audit.log')
    
    def send_wechat(self, success, project_no, debtor, file_info=None, error_msg=None):
        """
        发送企业微信通知
        """
        if not self.webhook_url:
            return False
        
        if success:
            message = f"""✅ **批复文件生成成功**

📋 项目编号：{project_no}
🏢 债务人：{debtor}
📁 文件：{file_info['name']}
💾 路径：{file_info['path']}
⏰ 时间：{datetime.datetime.now().strftime('%H:%M:%S')}

⚠️ 请核对金额、期限等关键要素后使用。"""
        else:
            message = f"""❌ **批复生成失败**

📋 项目：{project_no}（{debtor}）
❗ 错误：{error_msg}
🕐 时间：{datetime.datetime.now().strftime('%H:%M:%S')}"""
        
        try:
            headers = {"Content-Type": "application/json"}
            payload = {"msgtype": "text", "text": {"content": message}}
            resp = requests.post(
                self.webhook_url, 
                headers=headers, 
                data=json.dumps(payload, ensure_ascii=False), 
                timeout=10
            )
            return resp.json().get("errcode") == 0
        except Exception as e:
            print(f"⚠️ 群通知发送失败：{e}")
            return False
    
    def write_audit_log(self, ip, dept, action, filename, summary):
        """
        写入审计日志
        """
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} | {ip} | {dept} | {action} | {filename} | {summary}\n"
        
        try:
            with open(self.audit_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            return True
        except Exception as e:
            print(f"审计日志写入失败: {e}")
            return False
    
    def log_generation(self, dept, filename, context, client_ip='127.0.0.1'):
        """
        记录生成操作
        """
        summary = f"债务人:{context.get('debtor_name','')} 金额:{context.get('total_claim_amount','')}"
        return self.write_audit_log(client_ip, dept, '生成', filename, summary)
