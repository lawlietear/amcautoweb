# -*- coding: utf-8 -*-
"""
系统配置验证脚本
"""
import os
import json
import sys

os.chdir(r'G:\Workfile-TZ01\VScode\autodocweb_v2')

def check_templates():
    """验证模板文件"""
    print("=" * 50)
    print("1. 验证模板文件")
    print("=" * 50)
    
    templates_dir = 'word_templates'
    files = os.listdir(templates_dir)
    docx_files = [f for f in files if f.endswith('.docx')]
    
    expected_files = [
        'template_一次性业务批复.docx',
        'template_分期业务批复.docx'
    ]
    
    all_ok = True
    for expected in expected_files:
        if expected in docx_files:
            size = os.path.getsize(os.path.join(templates_dir, expected))
            print(f"  [OK] {expected} ({size} bytes)")
        else:
            print(f"  [MISSING] {expected}")
            all_ok = False
    
    return all_ok

def check_configs():
    """验证配置文件"""
    print("\n" + "=" * 50)
    print("2. 验证配置文件")
    print("=" * 50)
    
    config_files = [
        'config/config_风险合规部.json',
        'config/config_业务部.json'
    ]
    
    all_ok = True
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"  [OK] {config_file}")
            print(f"       部门: {config['dept_name']}")
            print(f"       模板: {list(config['templates'].keys())}")
            
            # 验证模板路径
            for k, v in config['templates'].items():
                exists = os.path.exists(v['path'])
                status = "OK" if exists else "MISSING"
                print(f"       - {k}: {status}")
                if not exists:
                    all_ok = False
        except Exception as e:
            print(f"  [ERROR] {config_file}: {e}")
            all_ok = False
    
    return all_ok

def check_directories():
    """验证目录结构"""
    print("\n" + "=" * 50)
    print("3. 验证目录结构")
    print("=" * 50)
    
    dirs = [
        'generated',
        'generated/风险合规部',
        'generated/业务部'
    ]
    
    all_ok = True
    for d in dirs:
        if os.path.isdir(d):
            # 测试写入权限
            test_file = os.path.join(d, '.write_test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"  [OK] {d} (可读写)")
            except Exception as e:
                print(f"  [ERROR] {d} 写入失败: {e}")
                all_ok = False
        else:
            print(f"  [MISSING] {d}")
            all_ok = False
    
    return all_ok

def main():
    print("AMC 文书生成器 - 系统配置验证")
    
    results = []
    results.append(("模板文件", check_templates()))
    results.append(("配置文件", check_configs()))
    results.append(("目录结构", check_directories()))
    
    print("\n" + "=" * 50)
    print("验证结果汇总")
    print("=" * 50)
    
    all_passed = True
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {name}: {status}")
        if not ok:
            all_passed = False
    
    if all_passed:
        print("\n[OK] 所有检查通过，系统可以正常运行！")
        return 0
    else:
        print("\n[WARNING] 部分检查未通过，请根据提示修复。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
