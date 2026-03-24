#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
山东金融资产智能文书系统
整合原 app.py 和 generate_pifu.py 的功能

版本: 2.0.0
发布日期: 2026-03-12
作者: Kimi Code CLI
"""

__version__ = "2.0.0"

import os
import sys
import json
import glob
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, send_file, send_from_directory, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename

# 导入核心模块
from core import DocumentGenerator, FormatUtils, ExcelHandler, Notification

# ==================== 配置 ====================

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 上传限制
app.secret_key = 'amc-secret-key-2024'  # Session 密钥

# 审计日志密码（可修改）
AUDIT_PASSWORD = 'amc2026'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
GENERATED_DIR = os.path.join(BASE_DIR, 'generated')
AUDIT_LOG_FILE = os.path.join(BASE_DIR, 'audit.log')

# 确保目录存在
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(os.path.join(GENERATED_DIR, '风险合规部'), exist_ok=True)
os.makedirs(os.path.join(GENERATED_DIR, '业务部'), exist_ok=True)

# 部门配置映射
DEPT_CONFIG = {
    'risk_compliance': {
        'key': 'risk_compliance',
        'name': '风险合规部',
        'icon': '⚖️',
        'config_file': 'config_risk_compliance.json',
        'output_dir': os.path.join(GENERATED_DIR, '风险合规部')
    },
    'business': {
        'key': 'business',
        'name': '业务部',
        'icon': '💼',
        'config_file': 'config_business.json',
        'output_dir': os.path.join(GENERATED_DIR, '业务部')
    }
}

# 初始化通知模块
notification = Notification({
    'audit_log_file': AUDIT_LOG_FILE,
    'webhook_url': '',  # 可在配置中设置
    'app_name': '山东金融资产智能文书系统'
})

# ==================== 工具函数 ====================

def load_dept_config(dept_key):
    """加载部门配置"""
    dept = DEPT_CONFIG.get(dept_key)
    if not dept:
        return None
    
    config_path = os.path.join(CONFIG_DIR, dept['config_file'])
    if not os.path.exists(config_path):
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            config['output_dir'] = dept['output_dir']
            config['dept_key'] = dept_key
            config['dept_name'] = dept['name']
            config['dept_icon'] = dept['icon']
            
            # 将模板路径转换为绝对路径
            if 'templates' in config:
                for template_key, template_info in config['templates'].items():
                    if 'path' in template_info:
                        template_path = template_info['path']
                        if not os.path.isabs(template_path):
                            template_info['path'] = os.path.join(BASE_DIR, template_path)
            
            # 兼容旧配置的单模板路径
            if 'template_path' in config:
                if not os.path.isabs(config['template_path']):
                    config['template_path'] = os.path.join(BASE_DIR, config['template_path'])
            
            return config
    except Exception as e:
        print(f"加载配置失败: {e}")
        return None


def clean_old_files(dept_name, hours=24):
    """清理超过指定小时的旧文件"""
    dept_dir = os.path.join(GENERATED_DIR, dept_name)
    if not os.path.exists(dept_dir):
        return
    
    now = time.time()
    for filepath in glob.glob(os.path.join(dept_dir, '*.docx')):
        if os.path.isfile(filepath):
            file_time = os.path.getmtime(filepath)
            if (now - file_time) > (hours * 3600):
                try:
                    os.remove(filepath)
                except:
                    pass


def get_client_ip():
    """获取客户端 IP"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'


# ==================== 路由 ====================

@app.route('/')
def index():
    """首页 - 部门选择"""
    return render_template('index.html')


@app.route('/risk_compliance')
def risk_compliance():
    """风险合规部页面"""
    config = load_dept_config('risk_compliance')
    if not config:
        return render_template('dept_form.html',
            dept_key='risk_compliance',
            dept_name='风险合规部',
            dept_icon='⚖️',
            variables=[],
            templates=None,
            default_template=None,
            sample_data=None,
            error_msg='⚠️ 配置文件缺失：config_风险合规部.json')
    
    sample = config.get('sample_data')
    return render_template('dept_form.html',
        dept_key='risk_compliance',
        dept_name=config.get('dept_name', '风险合规部'),
        dept_icon=config.get('dept_icon', '⚖️'),
        variables=config.get('variables', []),
        templates=config.get('templates'),
        default_template=config.get('default_template'),
        sample_data=sample,
        error_msg=None)


@app.route('/business')
def business():
    """业务部页面"""
    config = load_dept_config('business')
    if not config:
        return render_template('dept_form.html',
            dept_key='business',
            dept_name='业务部',
            dept_icon='💼',
            variables=[],
            templates=None,
            default_template=None,
            sample_data=None,
            error_msg='⚠️ 配置文件缺失：config_业务部.json')
    
    sample = config.get('sample_data')
    return render_template('dept_form.html',
        dept_key='business',
        dept_name=config.get('dept_name', '业务部'),
        dept_icon=config.get('dept_icon', '💼'),
        variables=config.get('variables', []),
        templates=config.get('templates'),
        default_template=config.get('default_template'),
        sample_data=sample,
        error_msg=None)


@app.route('/api/convert_amount', methods=['POST'])
def convert_amount():
    """API：金额转中文大写"""
    data = request.get_json()
    amount = data.get('amount', '')
    
    formatter = FormatUtils()
    result = formatter.amount_to_chinese(amount)
    
    return jsonify({
        'success': True,
        'result': result
    })


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API：生成文书"""
    try:
        data = request.get_json()
        dept_key = data.get('dept')
        form_data = data.get('data', {})
        template_key = data.get('template', 'default')  # 获取选择的模板
        
        # 加载部门配置
        config = load_dept_config(dept_key)
        if not config:
            return jsonify({'success': False, 'message': '部门配置不存在'})
        
        # 清理旧文件
        clean_old_files(config['dept_name'])
        
        # 智能识别业务类型并选择模板
        templates = config.get('templates', {})
        
        # 根据填写的字段自动判断业务类型
        auto_detected_template = None
        if 'occupancy_rate' in form_data and form_data['occupancy_rate'] and str(form_data['occupancy_rate']).strip():
            # 如果填写了资金占用费率，自动选择分期处置批复
            auto_detected_template = 'fenqi'
            print(f"[DEBUG] 自动识别为分期处置业务（occupancy_rate={form_data['occupancy_rate']}）")
        elif 'business_type' in form_data and form_data['business_type']:
            business_type = str(form_data['business_type']).lower()
            if '分期' in business_type or 'fenqi' in business_type:
                auto_detected_template = 'fenqi'
                print(f"[DEBUG] 自动识别为分期处置业务（business_type={form_data['business_type']}）")
        
        # 优先使用用户选择的模板，如果没有选择则使用自动识别的
        if template_key in templates:
            selected_template = template_key
        elif auto_detected_template and auto_detected_template in templates:
            selected_template = auto_detected_template
        elif 'yicixing' in templates:
            selected_template = 'yicixing'
        elif 'default' in templates:
            selected_template = 'default'
        else:
            # 兼容旧配置（单模板）
            selected_template = None
            template_path = config.get('template_path')
        
        # 获取模板路径
        if selected_template:
            template_path = templates[selected_template]['path']
            template_name = templates[selected_template]['name']
            print(f"[DEBUG] 使用模板：{template_name}（{selected_template}）")
        else:
            template_name = '默认模板'
        
        # 将相对路径转换为绝对路径
        if template_path and not os.path.isabs(template_path):
            template_path = os.path.join(BASE_DIR, template_path)
        
        if not template_path or not os.path.exists(template_path):
            return jsonify({'success': False, 'message': f'模板文件不存在：{template_path}'})
        
        # 创建生成器
        generator = DocumentGenerator(
            template_path=template_path,
            output_dir=config['output_dir']
        )
        
        # 准备上下文（使用 FormatUtils 处理数据）
        formatter = FormatUtils()
        context = {}
        
        # 基础字段
        for key, value in form_data.items():
            context[key] = value
        
        # 清理百分比字段（移除 % 符号）
        percent_fields = ['interest_rate', 'penalty_percent_10_3_2', 'penalty_percent_10_3_3']
        for field in percent_fields:
            if field in context and context[field]:
                # 移除 % 符号和 /年 等后缀，只保留数字
                value = str(context[field]).strip()
                value = value.replace('%', '').replace('/年', '').replace('％', '')
                value = value.strip()
                context[field] = value
                print(f"[DEBUG] 清理百分比字段 {field}: {form_data.get(field)} -> {value}")
        
        # 模板变量已统一为 penalty_percent_10_3_2 和 penalty_percent_10_3_3
        # 无需额外映射
        
        # 调试：打印接收到的数据
        print(f"[DEBUG] 接收到的数据: {form_data}")
        print(f"[DEBUG] context: {context}")
        
        # 生成 doc_full_no（用于文件名）
        if 'approval_no' in context and context['approval_no']:
            approval_no = context['approval_no'].strip()
            import re
            match = re.search(r'〔(\d{4})〕(\d+)', approval_no)
            if match:
                year = match.group(1)
                seq = match.group(2).zfill(3)
                context['doc_full_no'] = f"鲁金资管审复〔{year}〕{seq}号"
            else:
                context['doc_full_no'] = approval_no
            print(f"[DEBUG] 生成的 doc_full_no: {context.get('doc_full_no')}")
        
        # 生成 approval_date（批复日期，当前日期），格式：YYYY年M月D日（不带前导零）
        from datetime import datetime
        now = datetime.now()
        context['approval_date'] = f"{now.year}年{now.month}月{now.day}日"
        print(f"[DEBUG] 生成的 approval_date: {context.get('approval_date')}")
        
        # 金额字段列表（通用）
        amount_fields = ['principal_amount', 'interest_amount', 'other_fees_amount', 
                        'total_claim_amount', 'reserve_price', 'deposit_amount', 'remaining_amount']
        
        # 业务部合同特有的金额字段
        contract_amount_fields = ['transfer_price', 'remaining_price']
        
        # 金额字段到中文大写变量名的映射（模板中使用简写）
        amount_cn_mapping = {
            'principal_amount': 'principal_cn',
            'interest_amount': 'interest_cn',
            'other_fees_amount': 'other_fees_cn',
            'total_claim_amount': 'total_claim_cn',
            'reserve_price': 'reserve_price_cn',
            'deposit_amount': 'deposit_cn',
            'remaining_amount': 'remaining_cn',
            'transfer_price': 'transfer_price_cn',
            'remaining_price': 'remaining_cn'
        }
        
        # 格式化所有金额字段为千分位（并生成大写）
        for field in amount_fields:
            if field in context and context[field]:
                # 清理输入（移除已有的逗号和空格）
                raw_value = str(context[field]).replace(',', '').replace(' ', '').strip()
                # 格式化为千分位显示
                formatted = formatter.format_thousand(raw_value)
                context[field] = formatted
                # 生成中文大写金额（使用模板中的变量名）
                cn_field = amount_cn_mapping.get(field, field + '_cn')
                cn_value = formatter.amount_to_chinese(raw_value)
                context[cn_field] = cn_value
                print(f"[DEBUG] {field}: {raw_value} -> {formatted} -> {cn_field}: {cn_value}")
        
        # 格式化业务部合同特有的金额字段
        for field in contract_amount_fields:
            if field in context and context[field]:
                raw_value = str(context[field]).replace(',', '').replace(' ', '').strip()
                formatted = formatter.format_thousand(raw_value)
                context[field] = formatted
                cn_field = amount_cn_mapping.get(field, field + '_cn')
                cn_value = formatter.amount_to_chinese(raw_value)
                context[cn_field] = cn_value
                print(f"[DEBUG] {field}: {raw_value} -> {formatted} -> {cn_field}: {cn_value}")
        
        # ==================== 条款选择处理 ====================
        # 根据模板类型判断是分期还是非分期
        is_fenqi = selected_template == 'fenqi'
        
        # 7.4.1 条款 - 过渡期内标的债权收益归属
        transition_income_texts = {
            '1': '在过渡期内，如对标的债权进行处置实现了现金及非现金回收的，该等收入归甲方所有。',
            '2': '在过渡期内，如对标的债权进行处置实现了现金及非现金回收的，该等回收归乙方所有，则甲方应将回收的现金及非现金资产扣除甲方垫付的处置费用（如有）在交割日后10个工作日内移交给乙方。如回收的现金及非现金不足以抵扣甲方已垫付处置费用的，乙方应在交割日后10个工作日内将抵扣后剩余的处置费用支付给甲方。'
        }
        
        # 根据模板类型选择对应的变量和条款内容
        if is_fenqi:
            # 分期合同有3个选项
            fenqi_transition_income_texts = {
                '1': '在过渡期内，如对标的债权进行处置实现了现金及非现金回收的，该等收入归甲方所有。',
                '2': '在过渡期内，如对标的债权进行处置实现了现金及非现金回收的，该等回收归乙方所有，则甲方应将回收的现金及非现金资产扣除甲方垫付的处置费用（如有）在交割日后10个工作日内移交给乙方。如回收的现金及非现金不足以抵扣甲方已垫付处置费用的，乙方应在交割日后10个工作日内将抵扣后剩余的处置费用支付给甲方。',
                '3': '在过渡期内，如对标的债权进行处置实现了现金及非现金回收的，该等回收归乙方所有，交割日前，现金回收部分按照本合同第6.2.5条约定冲抵乙方应付款项；交割日后，甲方应将剩余的现金回收（如有）扣除甲方垫付的处置费用（如有）后与回收的非现金资产一并移交给乙方。如回收的现金及非现金不足以抵扣甲方已垫付处置费用的，乙方应在交割日后10个工作日内将抵扣后剩余的处置费用支付给甲方。'
            }
            selection = context.get('fenqi_transition_income', '').strip()
            clause_key = 'fenqi_transition_income_clause'
            texts_dict = fenqi_transition_income_texts
        else:
            # 非分期合同只有2个选项
            selection = context.get('yicixing_transition_income', '').strip()
            clause_key = 'transition_income_clause'
            texts_dict = transition_income_texts
        
        if selection in texts_dict:
            context[clause_key] = texts_dict[selection]
            print(f"[DEBUG] {'分期' if is_fenqi else '非分期'} 7.4.1条款选择: {selection}")
        else:
            context[clause_key] = texts_dict['1']
            print(f"[DEBUG] {'分期' if is_fenqi else '非分期'} 7.4.1条款默认选择: 1")
        
        # 8.5 条款 - 过渡期内处置费用承担
        disposal_fee_texts = {
            '1': '甲方承担。',
            '2': '乙方承担，自本合同生效之日起甲方不进行垫付。对于已由甲方垫付的费用，乙方应在交割日后的5个工作日内足额偿付给甲方。甲方有权从任何应支付给乙方的款项或应移交的回收款中直接扣除该等费用。'
        }
        
        if is_fenqi:
            # 分期合同有3个选项
            fenqi_disposal_fee_texts = {
                '1': '甲方承担。',
                '2': '乙方承担，自本合同生效之日起甲方不进行垫付。对于已由甲方垫付的费用，乙方应在交割日后的5个工作日内足额偿付给甲方。甲方有权从任何应支付给乙方的款项或应移交的回收款中直接扣除该等费用。',
                '3': '乙方承担，经乙方申请甲方可进行垫付，并按照本合同约定进行结算。'
            }
            selection = context.get('fenqi_disposal_fee', '').strip()
            clause_key = 'fenqi_disposal_fee_clause'
            texts_dict = fenqi_disposal_fee_texts
        else:
            # 非分期合同只有2个选项
            selection = context.get('yicixing_disposal_fee', '').strip()
            clause_key = 'disposal_fee_clause'
            texts_dict = disposal_fee_texts
        
        if selection in texts_dict:
            context[clause_key] = texts_dict[selection]
            print(f"[DEBUG] {'分期' if is_fenqi else '非分期'} 8.5条款选择: {selection}")
        else:
            context[clause_key] = texts_dict['2']
            print(f"[DEBUG] {'分期' if is_fenqi else '非分期'} 8.5条款默认选择: 2")
        
        # ==================== 条款选择处理结束 ====================
        
        # 生成文件名
        from datetime import datetime
        current_date = datetime.now().strftime("%Y.%m.%d")
        
        if dept_key == 'business':
            # 业务部合同命名规则：生成日期YYYY.MM.DD_债权转让合同（受让方名称）_合同编号
            party_b_name = context.get('party_b_name', '')
            contract_no = context.get('contract_no', '')
            # 清理文件名中的非法字符
            party_b_name = str(party_b_name).replace('/', '_').replace('\\', '_').replace(':', '_')
            contract_no = str(contract_no).replace('/', '_').replace('\\', '_').replace(':', '_')
            filename_pattern = f"{current_date}_债权转让合同（{party_b_name}）_{contract_no}.docx"
        else:
            # 风险合规部批复命名规则：批复编号_项目名称
            approval_no = context.get('approval_no', '')
            project_name = context.get('project_name', '')
            # 清理文件名中的非法字符
            approval_no = str(approval_no).replace('/', '_').replace('\\', '_').replace(':', '_')
            project_name = str(project_name).replace('/', '_').replace('\\', '_').replace(':', '_')
            filename_pattern = f"{approval_no}_{project_name}.docx"
        
        # 确保文件名安全（直接使用已导入的 FormatUtils）
        filename_pattern = FormatUtils.safe_filename(filename_pattern)
        
        # 生成文档（纯文本填充，保留模板原格式）
        print(f"[DEBUG] 开始生成文档...")
        print(f"[DEBUG] 模板路径: {template_path}")
        print(f"[DEBUG] 输出目录: {config['output_dir']}")
        print(f"[DEBUG] 文件名: {filename_pattern}")
        print(f"[DEBUG] 上下文键: {list(context.keys())}")
        
        file_path, filename = generator.generate(
            context=context,
            filename_pattern=filename_pattern
        )
        
        if not file_path:
            print(f"[ERROR] 生成失败: {filename}")
            return jsonify({'success': False, 'message': filename})  # filename 这里是错误信息
        
        print(f"[DEBUG] 生成成功: {file_path}")
        
        # 记录审计日志
        notification.log_generation(
            dept=config['dept_name'],
            filename=filename,
            context=context,
            client_ip=get_client_ip()
        )
        
        # 返回文件信息
        relative_path = os.path.join(config['dept_name'], filename)
        return jsonify({
            'success': True,
            'template_used': template_name if selected_template else '默认模板',
            'files': [{
                'name': filename,
                'url': f'/download/{config["dept_name"]}/{filename}'
            }]
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'生成失败：{str(e)}'})


@app.route('/api/import_excel', methods=['POST'])
def api_import_excel():
    """API：导入 Excel 文件"""
    try:
        dept_key = request.form.get('dept')
        file = request.files.get('file')
        
        if not file:
            return jsonify({'success': False, 'message': '未选择文件'})
        
        # 保存上传的文件
        temp_path = os.path.join(BASE_DIR, 'temp_upload.xlsx')
        file.save(temp_path)
        
        # 读取 Excel
        handler = ExcelHandler(temp_path)
        if not handler.read():
            os.remove(temp_path)
            return jsonify({'success': False, 'message': '读取 Excel 失败'})
        
        # 获取第一条记录
        pending = handler.get_pending_records()
        if pending is not None and len(pending) > 0:
            row_data = pending.iloc[0]
        else:
            # 如果没有标记为"立即生成"的，取第一条数据
            row_data = handler.get_row_data(0)
        
        if row_data is None:
            os.remove(temp_path)
            return jsonify({'success': False, 'message': 'Excel 中没有数据'})
        
        # 转换为表单格式
        formatter = FormatUtils()
        
        result = {
            # 基本信息
            'approval_no': str(row_data.get('批复编号', '')),
            'meeting_date': formatter.excel_date_to_str(row_data.get('会议/审批日')),
            'meeting_seq': formatter.meeting_seq_to_str(row_data.get('会次', '')),
            'business_type': str(row_data.get('业务分类', '')),
            'project_name': str(row_data.get('项目名称', '')),
            'reviewers': str(row_data.get('审核人员', '')),
            'report_name': str(row_data.get('尽调报告名称', row_data.get('报告名称', ''))),
            'department': str(row_data.get('部门', '')),
            'project_leaders': str(row_data.get('项目负责人', row_data.get('项目负责人名称', ''))),
            
            # 债务人信息
            'debtor_name': str(row_data.get('债务人名称', '')),
            'debtor_count': str(row_data.get('户数', '')),
            'base_date': formatter.excel_date_to_str(row_data.get('基准日')),
            
            # 金额信息
            'principal_amount': formatter.format_thousand(row_data.get('债权本金金额', 0)),
            'interest_amount': formatter.format_thousand(row_data.get('利息金额', row_data.get('债权利息金额', 0))),
            'other_fees_amount': formatter.format_thousand(row_data.get('其他费用金额', 0)),
            'total_claim_amount': formatter.format_thousand(row_data.get('债权总额', row_data.get('总额', 0))),
            
            # 交易信息
            'reserve_price': formatter.format_thousand(row_data.get('拟转让价格（元）', row_data.get('拟转让价格', 0))),
            'fee_bearer': str(row_data.get('交易费用承担主体', '')),
            'deposit_amount': formatter.format_thousand(row_data.get('保证金金额（元）', row_data.get('保证金金额', 0))),
            'remaining_amount': formatter.format_thousand(row_data.get('剩余交易价款金额（元）', 0)),
            'final_payment_deadline': str(row_data.get('尾款支付期限', '')),
            'occupancy_rate': str(row_data.get('资金占用费率', '')),
        }
        
        # 清理临时文件
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '导入成功'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'导入失败：{str(e)}'})


@app.route('/download/<dept_name>/<filename>')
def download_file(dept_name, filename):
    """下载生成的文件"""
    try:
        # 构建文件路径（不进行 secure_filename 转换，直接拼接）
        file_path = os.path.join(GENERATED_DIR, dept_name, filename)
        
        # 安全检查：确保路径在 GENERATED_DIR 下
        real_path = os.path.abspath(file_path)
        real_base = os.path.abspath(GENERATED_DIR)
        if not real_path.startswith(real_base):
            return '非法路径', 403
        
        if not os.path.exists(real_path):
            return f'文件不存在: {filename}', 404
        
        # 使用 send_file 下载
        return send_file(
            real_path,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        return f'下载错误: {str(e)}', 500


@app.route('/audit_log', methods=['GET', 'POST'])
def audit_log_page():
    """审计日志页面 - 密码保护"""
    # 检查是否已登录
    if session.get('audit_logged_in'):
        return render_template('audit_log.html')
    
    # 处理登录表单
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == AUDIT_PASSWORD:
            session['audit_logged_in'] = True
            return redirect(url_for('audit_log_page'))
        else:
            return render_template('audit_login.html', error='密码错误')
    
    # 显示登录页面
    return render_template('audit_login.html')


@app.route('/api/audit_logs')
def api_audit_logs():
    """API：获取审计日志 - 需要登录"""
    # 检查登录状态
    if not session.get('audit_logged_in'):
        return jsonify({'success': False, 'message': '未授权访问'}), 403
    
    try:
        logs = []
        
        if os.path.exists(AUDIT_LOG_FILE):
            with open(AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 解析日志格式：timestamp | ip | dept | action | filename | summary
                    parts = line.split(' | ')
                    if len(parts) >= 6:
                        logs.append({
                            'timestamp': parts[0],
                            'ip': parts[1],
                            'dept': parts[2],
                            'action': parts[3],
                            'filename': parts[4],
                            'summary': parts[5] if len(parts) > 5 else ''
                        })
        
        # 按时间倒序排列
        logs.reverse()
        
        return jsonify({
            'success': True,
            'logs': logs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'读取日志失败：{str(e)}'
        })


@app.route('/audit_logout')
def audit_logout():
    """退出审计日志"""
    session.pop('audit_logged_in', None)
    return redirect(url_for('audit_log_page'))


# ==================== 启动 ====================

def get_local_ip():
    """获取本机局域网 IP 地址"""
    try:
        import socket
        # 创建一个 UDP 连接来获取本机 IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    local_ip = get_local_ip()
    
    print("=" * 60)
    print(f"山东金融资产智能文书系统 v{__version__}")
    print("=" * 60)
    print(f"\n访问地址：")
    print(f"  - 本机：http://127.0.0.1:5000")
    print(f"  - 局域网：http://{local_ip}:5000")
    print(f"\n按 CTRL+C 停止服务")
    print("=" * 60 + "\n")
    
    # 使用 Waitress 生产服务器（支持多人同时访问）
    try:
        from waitress import serve
        print("[INFO] 使用 Waitress 生产服务器启动，支持多人同时访问\n")
        serve(app, host='0.0.0.0', port=5000, threads=8)
    except ImportError:
        print("[WARNING] Waitress 未安装，使用 Flask 开发服务器（仅支持单用户）")
        print("[INFO] 安装 Waitress：pip install waitress\n")
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
