# -*- coding: utf-8 -*-
"""
系统配置修复脚本
"""
import os
import json
import shutil

os.chdir(r'G:\Workfile-TZ01\VScode\autodocweb_v2')

def fix_template_names():
    """修复模板文件名"""
    print("修复模板文件名...")
    templates_dir = 'word_templates'
    files = os.listdir(templates_dir)
    
    mapping = {
        32048: 'template_一次性业务批复.docx',
        39140: 'template_分期业务批复.docx'
    }
    
    for f in files:
        if not f.endswith('.docx'):
            continue
            
        old_path = os.path.join(templates_dir, f)
        size = os.path.getsize(old_path)
        
        if size in mapping:
            new_name = mapping[size]
            new_path = os.path.join(templates_dir, new_name)
            
            if f != new_name:
                if os.path.exists(new_path):
                    os.remove(new_path)
                os.rename(old_path, new_path)
                print(f"  重命名: {f} -> {new_name}")
            else:
                print(f"  已正确: {new_name}")

def fix_business_config():
    """修复业务部配置 - 暂时使用风险合规部的模板作为占位"""
    print("\n修复业务部配置...")
    
    config_path = 'config/config_业务部.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 更新为实际存在的模板路径（使用风险合规部的模板作为示例）
    config['templates'] = {
        "pifu": {
            "name": "通用批复模板",
            "path": "G:/Workfile-TZ01/VScode/autodocweb_v2/word_templates/template_一次性业务批复.docx",
            "description": "通用批复文件模板"
        }
    }
    config['default_template'] = "pifu"
    
    # 更新变量定义以匹配风险合规部的模板
    config['variables'] = [
        {
            "key": "doc_full_no",
            "label": "批复文号",
            "type": "text",
            "required": True,
            "category": "基本信息"
        },
        {
            "key": "debtor_name",
            "label": "债务人名称",
            "type": "text",
            "required": True,
            "category": "基本信息"
        },
        {
            "key": "principal_amount",
            "label": "债权本金",
            "type": "numeric",
            "format": "thousand",
            "required": True,
            "category": "金额信息"
        },
        {
            "key": "total_claim_amount",
            "label": "债权总额",
            "type": "numeric",
            "format": "thousand",
            "required": True,
            "category": "金额信息"
        }
    ]
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    
    print(f"  已更新: {config_path}")
    print(f"  注意: 业务部当前使用风险合规部的模板作为占位")
    print(f"  建议: 后续请添加业务部专用模板并更新配置")

def main():
    print("=" * 50)
    print("AMC 文书生成器 - 系统修复")
    print("=" * 50)
    
    fix_template_names()
    fix_business_config()
    
    print("\n" + "=" * 50)
    print("修复完成")
    print("=" * 50)
    print("建议后续操作:")
    print("1. 为业务部创建专用的 Word 模板")
    print("2. 更新 config/config_业务部.json 指向正确的模板")
    print("3. 运行 verify_setup.py 验证修复结果")

if __name__ == '__main__':
    main()
