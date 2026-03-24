# AMC Document Generator v2 - 项目记忆

> 生成时间：2026-03-09  
> 用途：新会话快速恢复上下文

---

## 1. 项目概况

**项目名称**：山东金融资产智能文书系统（原AMC文书生成器）  
**代码目录**：`G:\Workfile-TZ01\WorkDock\autodocweb_v2`  
**技术栈**：Flask + Handsontable 14.0.0 + python-docx/docxtpl + pandas  
**当前状态**：核心功能已完成，运行正常  
**UI设计**：首页流动渐变动态背景（类似苹果官网风格）

---

## 2. 已完成模块

### 2.1 风险合规部（批复文档）
- **功能**：生成"一次性业务批复"和"分期处置批复"
- **变量数**：24个
- **智能特性**：根据 `occupancy_rate` 字段自动识别分期业务
- **模板**：
  - `template_一次性业务批复.docx`
  - `template_分期业务批复.docx`

### 2.2 业务部（合同文档）- 双表格设计
- **功能**：生成"债权转让协议（分期/非分期）"
- **界面设计**：双表格并排录入
  - **上表（批复信息）**：9个字段，支持Excel批量粘贴
    - 基准日、债权本金、债权利息、其他费用、债权总额、保证金、转让价格、剩余价款、**资金占用费率（只填数字）**
  - **下表（合同信息）**：21个字段，个性化填写
    - 乙方名称、法定代表人、注册地、合同编号、**银行信息**、甲方联系信息、乙方联系信息、违约金比例（10.3.2/10.3.3条款）
  - 两行表行数同步，一行批复信息对应一行合同信息
- **变量数**：30个（9必填 + 21可选）
- **必填项**（仅批复信息类）：
  - 乙方名称、基准日、债权本金、债权利息、其他费用
  - 债权总额、保证金金额、转让价格、合同编号
- **默认值功能**：支持保存/恢复甲方基本信息（不含银行信息）
- **模板**：
  - `template_债权转让协议_非分期.docx`
  - `template_债权转让协议_分期处置.docx`

### 2.3 通用功能
- ✅ Excel批量导入（支持日期、金额自动格式化）
- ✅ 金额千分位格式化 + 自动中文大写转换
- ✅ 审计日志系统（密码保护）
- ✅ 智能模板自动选择
- ✅ 表单数据自动保存/恢复（LocalStorage）
- ✅ Glassmorphism UI 设计

---

## 3. 关键配置

### 3.1 部门配置
```
config/config_risk_compliance.json  - 风险合规部（24变量）
config/config_business.json         - 业务部（30变量）
```

### 3.2 金额字段（自动格式化）
- `principal_amount` / `principal_amount_cn`
- `interest_amount` / `interest_amount_cn`
- `other_fees_amount` / `other_fees_amount_cn`
- `total_claim_amount` / `total_claim_amount_cn`
- `deposit_amount` / `deposit_amount_cn`
- `transfer_price` / `transfer_price_cn`
- `remaining_price` / `remaining_price_cn`

### 3.3 业务部默认值保存功能（已实施）
**方案A**：LocalStorage 本地存储
**固定变量清单**（8个）：
```
party_a_contact, party_a_phone, party_a_fax,
party_a_address, party_a_zip, party_a_email,
penalty_percent_10, penalty_percent_20
```
（银行信息随合同编号后填写，不作为默认值保存）

---

## 4. 文件结构

```
autodocweb_v2/
├── app.py                    # Flask后端主文件
├── core/
│   ├── __init__.py
│   ├── document_generator.py # Word文档生成
│   ├── format_utils.py       # 金额格式化、日期转换
│   ├── excel_handler.py      # Excel导入处理
│   └── notification.py       # 审计日志
├── config/
│   ├── config_risk_compliance.json  # 风险合规部配置
│   └── config_business.json         # 业务部配置（30变量，9必填21可选）
├── templates/
│   ├── index.html            # 部门选择页
│   ├── dept_form.html        # 数据录入表单（风险合规部单表格，业务部双表格）
│   └── audit_log.html        # 审计日志页
├── static/css/style.css      # 样式文件
├── word_templates/           # Word模板目录
│   ├── template_一次性业务批复.docx
│   ├── template_分期业务批复.docx
│   ├── template_债权转让协议_非分期.docx
│   └── template_债权转让协议_分期处置.docx
├── generated/                # 生成文件输出目录
│   ├── 风险合规部/
│   └── 业务部/
└── PROJECT_MEMORY.md         # 本项目文件
```

---

## 5. 待办事项

### 5.1 待实施（高优先级）
- [ ] **业务部默认值保存功能**
  - 使用 LocalStorage 保存甲方信息和银行账户
  - 添加"保存为默认值"和"恢复默认"按钮
  - 12个固定变量：`party_a_*`, `bank_*`, `penalty_percent_*`

### 5.2 已记录需求（未来开发）
- [ ] 批量生成功能（多份合同同时生成）

### 5.3 已知问题
- [ ] 无严重问题，系统运行正常

---

## 6. 快速启动

```bash
cd G:\Workfile-TZ01\WorkDock\autodocweb_v2
python app.py
```

访问：
- 首页：http://localhost:5000
- 风险合规部：http://localhost:5000/risk_compliance
- 业务部：http://localhost:5000/business
- 审计日志：http://localhost:5000/audit_log（需密码访问）

---

## 7. 关键实现细节

### 7.1 金额格式化逻辑（backend/app.py）
```python
amount_fields = ['principal_amount', 'interest_amount', ...]
contract_amount_fields = ['transfer_price', 'remaining_price']

for field in amount_fields + contract_amount_fields:
    raw_value = str(context[field]).replace(',', '').strip()
    context[field] = formatter.format_thousand(raw_value)
    context[field + '_cn'] = formatter.amount_to_chinese(raw_value)
```

**重要修复（2026-03-09）**：
- **问题**：`amount_to_chinese` 函数对"万"位处理有bug，10000000输出"壹仟元"而非"壹仟万元"
- **解决**：重写 `_int_to_chinese` 和 `_four_digit_to_chinese` 方法，正确分组处理万、亿级数字

### 7.2 模板自动选择逻辑
```python
if 'occupancy_rate' in form_data and form_data['occupancy_rate'].strip():
    auto_detected_template = 'fenqi'  # 分期
else:
    auto_detected_template = 'yicixing'  # 一次性
```

### 7.3 数据收集修复（关键bug修复记录）
**问题**：`getSourceData()` 在有分类行时无法正确获取输入  
**解决**：改用 `getDataAtCell(row, col)` 遍历读取

---

## 8. 最后操作记录

- **2026-03-09**：
  - ✅ 业务部界面重构：双表格设计（批复信息+合同信息）
  - ✅ 实施默认值保存功能（LocalStorage）
  - ✅ 新增12个固定变量默认值管理
  - ✅ 优化必填项配置（9必填+21可选）
- **当前状态**：网站功能基本完成，可投入使用

---

## 9. 业务部双表格使用说明

### 界面布局
```
┌─────────────────────────────────────┐
│ 📋 批复信息（可从风险合规部复制）   │ ← 蓝色表头
│ ┌────┬────┬────┬────┬────┐        │
│ │乙方│基准│本金│利息│... │        │ ← 支持多行粘贴
│ └────┴────┴────┴────┴────┘        │
├─────────────────────────────────────┤
│ 📝 合同信息（个性化填写）           │ ← 绿色表头
│ ┌────┬────┬────┬────┬────┐        │
│ │合同│甲方│银行│... │... │        │ ← 行数与上表同步
│ └────┴────┴────┴────┴────┘        │
└─────────────────────────────────────┘
```

### 使用流程
1. **复制批复信息**：从风险合规部批复Excel复制，粘贴到批复信息表
2. **填写合同信息**：在合同信息表对应行填写个性化信息
3. **保存默认值**：点击"保存为默认值"保存甲方信息、银行账户
4. **生成合同**：点击"生成文书"

### 默认值管理
- **自动填充**：打开页面自动填充已保存的默认值到空字段
- **保存**：填写好甲方信息后点击"保存为默认值"
- **恢复**：点击"恢复默认值"填充空字段（不覆盖已有值）

---

*此文件由 Kimi Code 自动生成，用于会话切换时快速恢复项目上下文*
