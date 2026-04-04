# 项目进展

AMC Doc Generator - 山东金融资产智能文书系统

---

## 2026-04-02 代码优化完成 + 项目重命名

### 重命名记录
- 原名称：`autodocweb_v2`
- 新名称：`amc-doc-generator`
- 原因：产品成熟，去掉版本号，更专业简洁

### 修改文件
- ✅ `start.bat` - 更新窗口标题
- ✅ `docs/progress.md` - 更新文档

### 已完成
- ✅ 代码审查与性能优化
- ✅ 配置集中化（新建 `core/config.py`）
- ✅ 日志系统重构（`print` → `logging`）
- ✅ `api_generate()` 函数拆分（5个辅助函数）
- ✅ 路由合并与向后兼容
- ✅ Excel 增量更新优化
- ✅ 所有文档更新（CHANGELOG.md、本文件）

### 技术决策
| 决策 | 原因 |
|------|------|
| 使用 `logging` 替代 `print` | 支持日志轮转、级别控制、结构化输出 |
| 拆分 `api_generate()` | 单函数286行过长，难以维护；拆分后职责清晰 |
| 保留旧路由兼容 | 避免前端模板修改，降低回归风险 |
| Excel增量更新 | 避免全量读写大文件，提升性能 |
| 配置集中管理 | 硬编码分散在多处，修改易遗漏 |

### 代码统计
```
app.py:         719行 → 674行   (-45行)
api_generate:   289行 → 80行    (-72%)
新增:           core/config.py   (+99行)
```

### 待办
- [ ] 测试环境验证所有功能
- [ ] 考虑添加单元测试覆盖核心逻辑
- [ ] 评估是否需要异步处理大文件上传

---

## 系统架构

### 功能模块

```
┌─────────────────────────────────────────┐
│           首页 (index.html)              │
│  ├─ 部门选择：风险合规部 / 业务部         │
│  ├─ 审计日志入口（右下角浮动按钮）        │
│  └─ Logo + 系统标题                      │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────┐      ┌───────────────┐
│  风险合规部    │      │    业务部      │
│ (批复文档)    │      │  (合同文档)    │
│               │      │               │
│ 单表格模式    │      │ 双表格模式    │
│ 24个变量      │      │ 30个变量      │
└───────────────┘      └───────────────┘
```

### 双部门对比

| 部门 | 功能 | 变量数 | 表格模式 | 模板文件 |
|------|------|--------|---------|---------|
| **风险合规部** | 批复文档生成 | 24个 | 单表格 | 一次性/分期/收购业务批复 |
| **业务部** | 合同文档生成 | 30个 | 双表格 | 债权转让协议（分期/非分期）|

---

## 数据结构设计

### 业务部变量（30个）

**批复信息表（9列）**：
- 基准日、债权本金金额、债权利息金额、其他费用金额
- 债权总额、保证金金额、转让价格、剩余交易价款、资金占用费率

**合同信息表（21列）**：
- 乙方名称、法定代表人、注册地
- 合同编号、收款银行、银行账户名称、银行账号
- 甲方联系人/电话/传真/地址/邮编/邮箱
- 乙方联系人/电话/传真/地址/邮编/邮箱
- 资金占用起算日、违约金比例（10.3.2/10.3.3条款）

### 风险合规部变量（24个）

- 批复编号、会议日期、会次、业务分类、项目名称
- 审核人员、尽调报告名称、部门、项目负责人
- 债务人名称、户数、基准日
- 债权本金金额、债权利息金额、其他费用金额、债权总额
- 拟转让价格、交易费用承担主体、保证金金额、剩余交易价款
- 尾款支付期限、资金占用费率

### 金额字段自动处理

```python
# 自动格式化千分位 + 生成中文大写
AMOUNT_FIELDS = [
    'principal_amount',      # → principal_cn
    'interest_amount',       # → interest_cn
    'other_fees_amount',     # → other_fees_cn
    'total_claim_amount',    # → total_claim_cn
    'deposit_amount',        # → deposit_cn
    'transfer_price',        # → transfer_price_cn
    'remaining_price'        # → remaining_cn
]
```

---

## 关键实现细节

### 智能模板选择逻辑

```python
if form_data.get('occupancy_rate'):
    auto_detected = 'fenqi'  # 分期
elif '分期' in business_type:
    auto_detected = 'fenqi'
else:
    auto_detected = 'yicixing'  # 一次性
```

### 双表格行数同步（JavaScript）

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

### 百分比字段清理

```python
PERCENT_FIELDS = ['interest_rate', 'penalty_percent_10_3_2', 'penalty_percent_10_3_3']
# 用户填写 "8%/年" → 自动清理为 "8"
```

---

## 访问地址

| 页面 | 地址 |
|------|------|
| 首页 | http://localhost:5000 |
| 风险合规部 | http://localhost:5000/risk_compliance |
| 业务部 | http://localhost:5000/business |
| 审计日志 | http://localhost:5000/audit_log（密码：amc2026）|

---

## 历史版本

### 2026-03-12 v2.0.0 发布
- ✅ Waitress 生产服务器支持多用户并发
- ✅ 收购业务模板
- ✅ 隐私保护模式
- ✅ 部署文档

### 2026-03-09
- 业务部界面重构（双表格设计）
- 默认值保存功能

### 2026-03-01 v1.0.0 初始版本
- 风险合规部批复生成
- 业务部合同生成
- Excel 批量导入
- 金额转中文大写

### 已完成
- ✅ Waitress 生产服务器支持多用户并发
- ✅ 收购业务模板
- ✅ 隐私保护模式
- ✅ 部署文档

---

## 2026-03-01 v1.0.0 初始版本

### 功能
- 风险合规部批复生成
- 业务部合同生成
- Excel 批量导入
- 金额转中文大写

---

## 2026-04-03 必填字段高亮优化

### 问题：必填字段高亮方案重构
**现象**：JavaScript renderer 方案在业务部双表格模式下失效

**尝试过的方案**：
1. ❌ Handsontable `renderer` 属性 - 双表格模式下不生效
2. ❌ `afterRenderer` 回调 - 未被调用
3. ✅ 纯 CSS `:empty` + `nth-child` 方案 - 工作正常

**最终方案**：
- 使用 CSS `:empty` 伪类检测空单元格
- 使用 `nth-child(n)` 精确定位必填列
- 移除所有 JavaScript 渲染逻辑

**修复后的正确映射**：
| 表格 | 必填列 | 来源配置 |
|------|--------|----------|
| 批复信息表 (pifu) | 1-7 | `config_business.json` 前7个字段 |
| 合同信息表 (hetong) | 1 | `party_b_name` |
| 甲方信息表 (defaults) | 1 | `contract_no` |
| 风险合规部 | 1,3-16 | `config_risk_compliance.json` (第2列非必填) |

**修改文件**：`static/css/style.css`

---

## 2026-04-02 Bug修复

### 问题：业务部必填字段高亮不显示
**现象**：页面提示"必填字段会高亮显示"，但业务部表格实际没有高亮效果

**原因**：
- 风险合规部（单表格）配置了 `renderer` 实现高亮
- 业务部（双表格）的 `hotPifu`、`hotHetong`、`hotDefaults` 没有配置 `renderer`

**修复**：
- 在 `initBusinessDualTables()` 中添加通用的 `requiredRenderer` 函数
- 为 `pifuColumns`、`hetongColumns`、`defaultsColumns` 都添加 `renderer: requiredRenderer`

**修改文件**：`templates/dept_form.html`
