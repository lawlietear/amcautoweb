#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
山东金融资产智能文书系统
整合原 app.py 和 generate_pifu.py 的功能

版本: 2.0.0
发布日期: 2026-03-12
作者: Kimi Code CLI & Taozheng（Product Owner）
"""

__version__ = "2.0.0"

import os
import sys
import json
import glob
import time
import re
import traceback
import logging
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, send_file, send_from_directory, jsonify, session, redirect, url_for, abort
from werkzeug.utils import secure_filename

# 导入核心模块
from core import DocumentGenerator, FormatUtils, ExcelHandler, Notification, config


# ==================== 日志配置 ====================

def setup_logging():
    """配置日志系统"""
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s: %(message)s'
    )

    # 文件日志（轮转，最大10MB，保留5个备份）
    file_handler = RotatingFileHandler(
        'app.log', maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if os.getenv('FLASK_DEBUG') else logging.INFO)

    # 根日志配置
    logger = logging.getLogger('autodocweb')
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)

    return logger


logger = setup_logging()

# ==================== Flask 配置 ====================

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['TEMPLATES_AUTO_RELOAD'] = True  # 禁用模板缓存

# 强制 Jinja2 不缓存模板
app.jinja_env.auto_reload = True
app.jinja_env.cache = None
app.secret_key = config.SECRET_KEY
app.logger.handlers = logger.handlers  # 使用统一日志配置

# 禁用浏览器缓存
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# 从配置模块导入
AUDIT_PASSWORD = config.AUDIT_PASSWORD
BASE_DIR = str(config.BASE_DIR)
CONFIG_DIR = str(config.CONFIG_DIR)
GENERATED_DIR = str(config.GENERATED_DIR)
AUDIT_LOG_FILE = str(config.AUDIT_LOG_FILE)
DEPT_CONFIG = config.DEPT_CONFIG
CLAUSE_CONFIG = config.CLAUSE_CONFIG

# 确保目录存在
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(os.path.join(GENERATED_DIR, '风险合规部'), exist_ok=True)
os.makedirs(os.path.join(GENERATED_DIR, '业务部'), exist_ok=True)

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
        logger.error(f"加载配置失败: {e}")
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
                    logger.debug(f"清理旧文件: {filepath}")
                except Exception as e:
                    logger.warning(f"清理旧文件失败: {filepath}, 错误: {e}")


def get_client_ip():
    """获取客户端 IP"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'


# ==================== 路由 ====================

# ==================== 路由 ====================

@app.route('/')
def index():
    """首页 - 部门选择"""
    return render_template('index.html')


@app.route('/<dept_key>')
def dept_page(dept_key):
    """统一部门页面路由 - 合并原 risk_compliance 和 business"""
    if dept_key not in DEPT_CONFIG:
        abort(404)

    dept_info = DEPT_CONFIG[dept_key]
    dept_config = load_dept_config(dept_key)

    if not dept_config:
        return render_template('dept_form.html',
            dept_key=dept_key,
            dept_name=dept_info['name'],
            dept_icon=dept_info['icon'],
            variables=[],
            templates=None,
            default_template=None,
            sample_data=None,
            error_msg=f"⚠️ 配置文件缺失：{dept_info['config_file']}")

    sample = dept_config.get('sample_data')
    return render_template('dept_form.html',
        dept_key=dept_key,
        dept_name=dept_config.get('dept_name', dept_info['name']),
        dept_icon=dept_config.get('dept_icon', dept_info['icon']),
        variables=dept_config.get('variables', []),
        templates=dept_config.get('templates'),
        default_template=dept_config.get('default_template'),
        sample_data=sample,
        error_msg=None)


# 保持向后兼容的旧路由
@app.route('/risk_compliance')
def risk_compliance():
    """风险合规部页面（兼容旧路由）"""
    return dept_page('risk_compliance')


@app.route('/business')
def business():
    """业务部页面（兼容旧路由）"""
    return dept_page('business')


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


# ==================== API 生成辅助函数 ====================

def _select_template(dept_config, template_key, form_data):
    """步骤1: 根据配置和表单数据选择模板"""
    templates = dept_config.get('templates', {})

    # 自动识别业务类型（分期/非分期）
    auto_detected = None
    occupancy_rate = form_data.get('occupancy_rate', '')
    business_type = str(form_data.get('business_type', '')).lower()

    if occupancy_rate and str(occupancy_rate).strip():
        auto_detected = 'fenqi'
        logger.debug(f"自动识别为分期处置业务（occupancy_rate={occupancy_rate}）")
    elif '分期' in business_type or 'fenqi' in business_type:
        auto_detected = 'fenqi'
        logger.debug(f"自动识别为分期处置业务（business_type={business_type}）")

    # 优先级：用户选择 > 自动识别 > 默认模板
    if template_key in templates:
        selected = template_key
    elif auto_detected and auto_detected in templates:
        selected = auto_detected
    elif 'yicixing' in templates:
        selected = 'yicixing'
    elif 'default' in templates:
        selected = 'default'
    else:
        # 兼容旧配置（单模板）
        return dept_config.get('template_path'), '默认模板'

    template_info = templates[selected]
    logger.debug(f"使用模板：{template_info['name']}（{selected}）")
    return template_info['path'], template_info['name']


def _generate_doc_full_no(approval_no):
    """生成完整批复编号"""
    if not approval_no:
        return None
    approval_no = str(approval_no).strip()
    match = re.search(r'〔(\d{4})〕(\d+)', approval_no)
    if match:
        return f"鲁金资管审复〔{match.group(1)}〕{match.group(2).zfill(3)}号"
    return approval_no


def _format_amount_fields(context, formatter):
    """格式化金额字段（千分位 + 中文大写）"""
    all_amount_fields = config.AMOUNT_FIELDS + config.CONTRACT_AMOUNT_FIELDS

    for field in all_amount_fields:
        if field in context and context[field]:
            # 清理输入
            raw_value = str(context[field]).replace(',', '').replace(' ', '').strip()
            # 千分位格式
            formatted = formatter.format_thousand(raw_value)
            context[field] = formatted
            # 中文大写
            cn_field = config.AMOUNT_CN_MAPPING.get(field, field + '_cn')
            context[cn_field] = formatter.amount_to_chinese(raw_value)
            logger.debug(f"{field}: {raw_value} -> {formatted} -> {cn_field}: {context[cn_field]}")

    return context


def _prepare_context(form_data):
    """步骤2: 准备上下文数据"""
    formatter = FormatUtils()
    context = dict(form_data)  # 复制基础字段

    # 清理百分比字段
    for field in config.PERCENT_FIELDS:
        if field in context and context[field]:
            value = str(context[field]).strip()
            value = value.replace('%', '').replace('/年', '').replace('％', '').strip()
            context[field] = value
            logger.debug(f"清理百分比字段 {field}: {form_data.get(field)} -> {value}")

    # 生成批复编号
    if context.get('approval_no'):
        context['doc_full_no'] = _generate_doc_full_no(context['approval_no'])
        logger.debug(f"生成的 doc_full_no: {context.get('doc_full_no')}")

    # 生成批复日期
    now = datetime.now()
    context['approval_date'] = f"{now.year}年{now.month}月{now.day}日"
    logger.debug(f"生成的 approval_date: {context.get('approval_date')}")

    # 格式化金额
    context = _format_amount_fields(context, formatter)

    return context


def _apply_clause_logic(context, is_fenqi):
    """步骤3: 应用条款逻辑"""
    # 7.4.1 条款 - 过渡期内标的债权收益归属
    if is_fenqi:
        selection = str(context.get('fenqi_transition_income', '')).strip()
        texts = CLAUSE_CONFIG['fenqi_transition_income']
        clause_key = 'fenqi_transition_income_clause'
    else:
        selection = str(context.get('yicixing_transition_income', '')).strip()
        texts = CLAUSE_CONFIG['transition_income']
        clause_key = 'transition_income_clause'

    context[clause_key] = texts.get(selection, texts['1'])
    logger.debug(f"{'分期' if is_fenqi else '非分期'} 7.4.1条款选择: {selection or '1'}")

    # 8.5 条款 - 过渡期内处置费用承担
    if is_fenqi:
        selection = str(context.get('fenqi_disposal_fee', '')).strip()
        texts = CLAUSE_CONFIG['fenqi_disposal_fee']
        clause_key = 'fenqi_disposal_fee_clause'
        default = '2'
    else:
        selection = str(context.get('yicixing_disposal_fee', '')).strip()
        texts = CLAUSE_CONFIG['disposal_fee']
        clause_key = 'disposal_fee_clause'
        default = '2'

    context[clause_key] = texts.get(selection, texts[default])
    logger.debug(f"{'分期' if is_fenqi else '非分期'} 8.5条款选择: {selection or default}")

    return context


def _build_filename(context, dept_key):
    """步骤4: 构建文件名"""
    current_date = datetime.now().strftime("%Y.%m.%d")

    if dept_key == 'business':
        # 业务部合同命名
        party_b = str(context.get('party_b_name', '')).replace('/', '_').replace('\\', '_').replace(':', '_')
        contract_no = str(context.get('contract_no', '')).replace('/', '_').replace('\\', '_').replace(':', '_')
        filename = f"{current_date}_债权转让合同（{party_b}）_{contract_no}.docx"
    else:
        # 风险合规部批复命名
        approval_no = str(context.get('approval_no', '')).replace('/', '_').replace('\\', '_').replace(':', '_')
        project_name = str(context.get('project_name', '')).replace('/', '_').replace('\\', '_').replace(':', '_')
        filename = f"{approval_no}_{project_name}.docx"

    return FormatUtils.safe_filename(filename)


# ==================== API 路由 ====================

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API：生成文书 - 主入口"""
    try:
        data = request.get_json()
        dept_key = data.get('dept')
        form_data = data.get('data', {})
        template_key = data.get('template', 'default')

        logger.info(f"开始生成文档: dept={dept_key}, template={template_key}")
        logger.debug(f"接收到的数据: {form_data}")

        # 加载部门配置
        dept_config = load_dept_config(dept_key)
        if not dept_config:
            return jsonify({'success': False, 'message': '部门配置不存在'})

        # 清理旧文件
        clean_old_files(dept_config['dept_name'])

        # 步骤1: 选择模板
        template_path, template_name = _select_template(dept_config, template_key, form_data)

        # 转换相对路径为绝对路径
        if template_path and not os.path.isabs(template_path):
            template_path = os.path.join(BASE_DIR, template_path)

        if not template_path or not os.path.exists(template_path):
            return jsonify({'success': False, 'message': f'模板文件不存在：{template_path}'})

        # 步骤2: 准备上下文
        context = _prepare_context(form_data)

        # 步骤3: 应用条款逻辑
        is_fenqi = template_name == '分期' or 'fenqi' in str(template_path).lower()
        context = _apply_clause_logic(context, is_fenqi)

        # 步骤4: 构建文件名
        filename_pattern = _build_filename(context, dept_key)

        # 步骤5: 生成文档
        logger.info(f"开始生成文档: template={template_path}, filename={filename_pattern}")
        logger.debug(f"上下文键: {list(context.keys())}")

        generator = DocumentGenerator(
            template_path=template_path,
            output_dir=dept_config['output_dir']
        )

        file_path, filename = generator.generate(
            context=context,
            filename_pattern=filename_pattern
        )

        if not file_path:
            logger.error(f"生成失败: {filename}")
            return jsonify({'success': False, 'message': filename})

        logger.info(f"生成成功: {file_path}")

        # 记录审计日志
        notification.log_generation(
            dept=dept_config['dept_name'],
            filename=filename,
            context=context,
            client_ip=get_client_ip()
        )

        # 返回文件信息
        return jsonify({
            'success': True,
            'template_used': template_name,
            'files': [{
                'name': filename,
                'url': f'/download/{dept_config["dept_name"]}/{filename}'
            }]
        })

    except Exception as e:
        logger.exception("生成文档失败")
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
        logger.exception("Excel导入失败")
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
    
    # 使用 Flask 开发服务器（启用多线程支持多人访问）
    # 注意：模板修改后需要重启服务器才能生效
    print("[INFO] 使用 Flask 开发服务器启动（多线程模式，支持多人访问）\n")
    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True,  # 启用多线程支持并发
        use_reloader=False  # 禁用重载器避免双进程
    )

