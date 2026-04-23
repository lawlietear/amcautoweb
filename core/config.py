# -*- coding: utf-8 -*-
"""
统一配置管理模块
支持环境变量覆盖，提供默认值
"""

import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent.parent

# Flask 配置
SECRET_KEY = os.getenv('AMC_SECRET_KEY', 'amc-secret-key-2024')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 上传限制

# 审计配置
AUDIT_PASSWORD = os.getenv('AMC_AUDIT_PASSWORD', 'amc2026')
AUDIT_LOG_FILE = BASE_DIR / 'audit.log'

# 目录配置
GENERATED_DIR = BASE_DIR / 'generated'
CONFIG_DIR = BASE_DIR / 'config'

# 部门配置映射
DEPT_CONFIG = {
    'risk_compliance': {
        'key': 'risk_compliance',
        'name': '风险合规部',
        'icon': '⚖️',
        'config_file': 'config_risk_compliance.json',
        'output_dir': GENERATED_DIR / '风险合规部'
    },
    'business': {
        'key': 'business',
        'name': '业务部',
        'icon': '💼',
        'config_file': 'config_business.json',
        'output_dir': GENERATED_DIR / '业务部'
    }
}

# 条款文本配置（从 app.py 提取，集中管理）
CLAUSE_CONFIG = {
    'transition_income': {
        '1': '在过渡期内，如对标的债权进行处置实现了现金及非现金回收的，该等收入归甲方所有。',
        '2': '在过渡期内，如对标的债权进行处置实现了现金及非现金回收的，该等回收归乙方所有，则甲方应将回收的现金及非现金资产扣除甲方垫付的处置费用（如有）在交割日后10个工作日内移交给乙方。如回收的现金及非现金不足以抵扣甲方已垫付处置费用的，乙方应在交割日后10个工作日内将抵扣后剩余的处置费用支付给甲方。'
    },
    'fenqi_transition_income': {
        '1': '在过渡期内，如对标的债权进行处置实现了现金及非现金回收的，该等收入归甲方所有。',
        '2': '在过渡期内，如对标的债权进行处置实现了现金及非现金回收的，该等回收归乙方所有，则甲方应将回收的现金及非现金资产扣除甲方垫付的处置费用（如有）在交割日后10个工作日内移交给乙方。如回收的现金及非现金不足以抵扣甲方已垫付处置费用的，乙方应在交割日后10个工作日内将抵扣后剩余的处置费用支付给甲方。',
        '3': '在过渡期内，如对标的债权进行处置实现了现金及非现金回收的，该等回收归乙方所有，交割日前，现金回收部分按照本合同第6.2.5条约定冲抵乙方应付款项；交割日后，甲方应将剩余的现金回收（如有）扣除甲方垫付的处置费用（如有）后与回收的非现金资产一并移交给乙方。如回收的现金及非现金不足以抵扣甲方已垫付处置费用的，乙方应在交割日后10个工作日内将抵扣后剩余的处置费用支付给甲方。'
    },
    'disposal_fee': {
        '1': '甲方承担。',
        '2': '乙方承担，自本合同生效之日起甲方不进行垫付。对于已由甲方垫付的费用，乙方应在交割日后的10个工作日内足额偿付给甲方。甲方有权从任何应支付给乙方的款项或应移交的回收款中直接扣除该等费用。'
    },
    'fenqi_disposal_fee': {
        '1': '甲方承担。',
        '2': '乙方承担，自本合同生效之日起甲方不进行垫付。对于已由甲方垫付的费用，乙方应在交割日后的10个工作日内足额偿付给甲方。甲方有权从任何应支付给乙方的款项或应移交的回收款中直接扣除该等费用。',
        '3': '乙方承担，经乙方申请甲方可进行垫付，并按照本合同约定进行结算。'
    },
    'fenqi_collection_recovery': {
        '1': '双方同意，过渡期内标的债权产生的清收回款归甲方所有，须汇入甲方指定账户，不得用于冲抵乙方应付款项。',
        '2': '双方同意，过渡期内标的债权产生的清收回款归乙方所有，但须汇入甲方指定账户，不得用于冲抵乙方应付款项，甲方按照本合同7.4.1条约定在交割日后10个工作日内移交给乙方。',
        '3': '双方同意，过渡期内标的债权产生的清收回款须汇入甲方指定账户，用于冲抵乙方应付款项，并按照6.2.4条约定的顺序进行冲抵，当期资金占用费计提至冲抵之日，当期应付资金占用费均已结清时，可继续冲抵待付转让价款。'
    }
}

# 金额字段配置
AMOUNT_FIELDS = [
    'principal_amount', 'interest_amount', 'other_fees_amount',
    'total_claim_amount', 'reserve_price', 'deposit_amount', 'remaining_amount'
]

CONTRACT_AMOUNT_FIELDS = ['transfer_price', 'remaining_price']

# 金额字段到中文大写变量名的映射
AMOUNT_CN_MAPPING = {
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

# 百分比字段（需要清理 % 符号）
PERCENT_FIELDS = ['interest_rate', 'penalty_percent_10_3_2', 'penalty_percent_10_3_3']
