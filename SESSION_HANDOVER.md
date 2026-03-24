# 会话交接文档 - 山东金融资产智能文书系统

> 生成时间：2026-03-09
> 用途：新会话快速恢复项目上下文

---

## 1. 项目基本信息

| 项目 | 内容 |
|------|------|
| **项目名称** | 山东金融资产智能文书系统（原AMC文书生成器） |
| **代码路径** | `G:\Workfile-TZ01\WorkDock\autodocweb_v2` |
| **技术栈** | Flask + Handsontable 14.0.0 + python-docx/docxtpl |
| **运行方式** | `python app.py` → http://localhost:5000 |

---

## 2. 已完成的核心功能

### 2.1 双部门系统

| 部门 | 功能 | 变量数 | 表格模式 |
|------|------|--------|---------|
| **风险合规部** | 批复文档生成 | 24个 | 单表格 |
| **业务部** | 合同文档生成 | 30个 | 双表格（批复+合同） |

### 2.2 关键功能

- ✅ 智能模板选择（根据`资金占用费率`自动识别分期/一次性）
- ✅ 双表格行数同步（批复表和合同表行数联动）
- ✅ 金额千分位格式化 + 中文大写自动转换
- ✅ 行数动态增减（默认1行，可批量生成）
- ✅ 默认值保存/恢复（LocalStorage）
- ✅ 审计日志系统（密码：amc2026）
- ✅ 百分比字段自动清理（移除%符号）

---

## 3. 文件结构

```
autodocweb_v2/
├── app.py                      # Flask主程序
├── core/
│   ├── document_generator.py   # Word生成
│   ├── format_utils.py         # 金额格式化
│   ├── excel_handler.py        # Excel导入
│   └── notification.py         # 审计日志
├── config/
│   ├── config_risk_compliance.json  # 风险合规部配置
│   └── config_business.json         # 业务部配置（30变量）
├── templates/
│   ├── index.html              # 首页
│   ├── dept_form.html          # 数据录入页
│   ├── audit_log.html          # 审计日志
│   └── audit_login.html        # 登录页
├── static/
│   ├── css/style.css           # 样式文件
│   ├── images/
│   │   └── logo.svg            # Logo（右上角显示）
│   └── art-deco-preview.html   # Art Deco预览（待应用）
├── word_templates/             # Word模板
│   ├── template_一次性业务批复.docx
│   ├── template_分期业务批复.docx
│   ├── template_债权转让协议_非分期.docx
│   └── template_债权转让协议_分期处置.docx
└── generated/                  # 生成文件输出
    ├── 风险合规部/
    └── 业务部/
```

---

## 4. Art Deco 改造任务（待完成）

### 4.1 已完成的设计预览

**文件位置**：`static/art-deco-preview.html`

**设计特点**：
- **配色**：奶油色背景 (#F5F0E8) + 香槟金 (#C9A96E) + 黑色文字
- **字体**：Playfair Display（英文）+ 思源宋体（中文）
- **背景**：金色太阳光芒旋转动画 + 几何网格
- **装饰**：双层边框、45°切角、几何边角装饰

### 4.2 需要应用的文件

| 文件 | 改造内容 |
|------|---------|
| `static/css/style.css` | 更新Art Deco配色、字体、背景动画 |
| `templates/index.html` | 调整布局、Logo位置、标题样式 |
| `templates/dept_form.html` | 表格美化、按钮样式、整体配色 |
| `templates/audit_log.html` | 统一Art Deco风格 |
| `templates/audit_login.html` | 登录页风格统一 |

### 4.3 关键CSS变量

```css
:root {
    --deco-gold: #C9A96E;           /* 香槟金 */
    --deco-gold-light: #E8D5A3;     /* 浅金 */
    --deco-gold-dark: #8B7355;      /* 深金 */
    --deco-cream: #F5F0E8;          /* 奶油色背景 */
    --deco-black: #1A1A1A;          /* 黑色文字 */
    --deco-charcoal: #2D2D2D;       /* 炭灰 */
}
```

---

## 5. 数据字段配置

### 5.1 业务部关键字段（30个）

**批复信息表（9列）**：
- `base_date` - 基准日
- `principal_amount` - 债权本金金额
- `interest_amount` - 债权利息金额
- `other_fees_amount` - 其他费用金额
- `total_claim_amount` - 债权总额
- `deposit_amount` - 保证金金额
- `transfer_price` - 转让价格
- `remaining_price` - 剩余交易价款
- `interest_rate` - 资金占用费率（只填数字）

**合同信息表（21列）**：
- `party_b_name` - 乙方名称
- `party_b_legal_rep` - 法定代表人
- `party_b_address` - 乙方地址（注册地）
- `contract_no` - 合同编号
- `bank_name` - 收款银行
- `bank_account_name` - 银行账户名称
- `bank_account` - 银行账号
- 甲方联系信息（6个字段）
- 乙方联系信息（5个字段）
- `funding_start_date` - 资金占用起算日
- `penalty_percent_10_3_2` - 违约金比例（10.3.2条款）
- `penalty_percent_10_3_3` - 违约金比例（10.3.3条款）

### 5.2 金额字段（自动转大写）

```python
amount_fields = [
    'principal_amount',   # → principal_cn
    'interest_amount',    # → interest_cn
    'other_fees_amount',  # → other_fees_cn
    'total_claim_amount', # → total_claim_cn
    'deposit_amount',     # → deposit_cn
    'transfer_price',     # → transfer_price_cn
    'remaining_price'     # → remaining_cn
]
```

---

## 6. 重要代码片段

### 6.1 双表格行数同步

```javascript
function addRowDual() {
    const pifuData = hotPifu.getData();
    const hetongData = hotHetong.getData();
    pifuData.push(new Array(pifuData[0].length).fill(''));
    hetongData.push(new Array(hetongData[0].length).fill(''));
    hotPifu.loadData(pifuData);
    hotHetong.loadData(hetongData);
}
```

### 6.2 百分比字段清理

```python
percent_fields = [
    'interest_rate',
    'penalty_percent_10_3_2',
    'penalty_percent_10_3_3'
]
for field in percent_fields:
    value = str(context[field]).replace('%', '').replace('/年', '')
```

---

## 7. Token 消耗评估

### 7.1 Art Deco 改造工程量

| 任务 | 预估 Token | 说明 |
|------|-----------|------|
| 更新 style.css | ~1,500 | 全局样式、动画、响应式 |
| 改造 index.html | ~800 | 首页布局、Logo、标题 |
| 改造 dept_form.html | ~1,200 | 表格样式、按钮、配色 |
| 改造 audit_log.html | ~600 | 审计日志页统一风格 |
| 改造 audit_login.html | ~400 | 登录页统一风格 |
| 调试优化 | ~500 | 细节调整 |
| **总计** | **~5,000** | 完整视觉改造 |

### 7.2 建议策略

**新会话执行步骤**：
1. 读取本交接文档（快速恢复上下文）
2. 查看 `art-deco-preview.html` 确认设计
3. 分文件逐步改造（每次修改后验证）
4. 最后整体调试

---

## 8. 快速开始指令

**新会话时，请告诉 Kimi：**

> "读取 `G:\Workfile-TZ01\WorkDock\autodocweb_v2\SESSION_HANDOVER.md` 恢复项目上下文，然后应用 Art Deco 风格改造网站视觉设计。"

---

## 9. 当前待确认事项

- [ ] Art Deco 奶油色方案已确认
- [ ] 需要应用到所有页面
- [ ] 保留现有功能和数据结构

---

*本文档用于会话交接，请妥善保存*
