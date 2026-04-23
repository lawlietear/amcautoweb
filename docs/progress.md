# 项目进展

AMC Doc Generator - 山东金融资产智能文书系统

---

## 2026-04-23 分期条款修复 + 银行默认值 + 6.2.5 条款新增

### 修复分期合同条款变量空白
**现象**：分期合同生成后，7.4.1 和 8.5 条款变量显示为空白。

**原因**：
- 后端 `is_fenqi` 使用 `template_name == '分期' or 'fenqi' in path` 判断，但 `template_name` 为完整中文名、路径不含 `fenqi`，导致判断永远失败，后端赋值给非分期变量名。
- 前端 `collectData()` 中额外判断 `dataset.type === 'fenqi'`，分期模式下即使选了通用选项也不收集。

**修复**：
- 后端：`is_fenqi = template_key == 'fenqi'`，与前端正交。
- 前端：移除 `dataset.type` 过滤，直接按 `isFenqi` 决定存入的 key。

**修改文件**：`app.py`、`templates/dept_form.html`

### 银行信息纳入默认值保存
**现象**：收款银行、银行账户名称、银行账号每次都需要重新填写。

**原因**：这三个字段在 `HETONG_KEYS`（乙方信息，不可保存默认值）中，不在 `DEFAULT_KEYS` / `DEFAULT_VALUE_KEYS` 中。

**修复**：将三个字段从 `HETONG_KEYS` 移出，加入 `DEFAULT_KEYS` 和 `DEFAULT_VALUE_KEYS`，使其进入 localStorage 持久化链路。数据填充/收集/清空逻辑均通过 `propToCol` 动态适配，无需额外调整。

**修改文件**：`templates/dept_form.html`

### 新增 6.2.5 清收回款冲抵安排条款
**需求**：分期合同 6.2.5 条需要三选一变量替换。

**实现**：
- 前端：在 7.4.1 条款上方新增 radio 组，三个选项，默认选项 3，带 `fenqi-only` class。
- 后端：`CLAUSE_CONFIG` 新增 `fenqi_collection_recovery`；`_apply_clause_logic()` 新增仅分期分支处理。
- 修复 `getClauseSelection()` 和 radio change 监听器遗漏该字段的问题，确保 `collectAllRowsData()` 生成请求时携带。

**修改文件**：`core/config.py`、`app.py`、`templates/dept_form.html`

### Word 模板修复
**现象**：`template_一次性业务批复.docx` 打开提示"无法读取的内容"。

**原因**：`docProps/app.xml` 中包含 `HeadingPairs`、`TitlesOfParts`、`HyperlinkBase` 三个异常元素，且 `Template` 值为 `AMC_System_Template`。

**修复**：移除三个异常元素，修正 `Template` 为 `Normal.dotm`。

**修改文件**：`word_templates/template_一次性业务批复_fixed.docx`

---

## 2026-04-14 修复已填字段默认计数异常 + 分期违约金列只读
**现象**：页面初始加载时，业务部显示"已填字段 2"，风险合规部显示"已填字段 1"，但用户并未输入任何内容。

**原因**：
- 业务部：`setClauseDefaults()` 给 radio 条款按钮设置了默认值，`collectData()` 收集后算入统计。
- 风险合规部：`fillAutoDateFields()` 自动填充了 `readonly` 的 `approval_date`（当前日期），算入统计。

**修复**：
- 在 `updateStats()` 的 `shouldCountField()` 中排除所有 `readonly` 字段。
- 排除系统默认的条款 radio 字段（`yicixing_transition_income`、`yicixing_disposal_fee`、`fenqi_transition_income`、`fenqi_disposal_fee`）。
- 确保"已填字段"仅统计用户实际可编辑并输入的内容。

**修改文件**：`templates/dept_form.html`

### 分期模板下禁用违约金比例最后两列
**完成内容**：
- 新增 `updatePenaltyColumnsReadOnly()`，在分期模板（`fenqi`）下将违约金比例最后两列设为 `readOnly`。
- 添加深灰色背景 `.read-only-penalty` 作为视觉提示。
- 在 `onTemplateChange()` 和 `hotDefaults` 初始化后调用该函数。
- 修复 `detectBusinessType()` 自动识别模板后未触发 `onTemplateChange()` 的遗漏。
- 将 Handsontable 实例暴露到 `window`，便于调试和自动化测试。

**修改文件**：`templates/dept_form.html`、`app.py`

### 生产环境部署优化
- 新增 `启动-生产环境.bat`，双击即用 waitress 生产服务器（12 线程）。
- `app.py` 自动识别 waitress 启动方式并切换为生产配置（关闭模板缓存、启用静态资源缓存）。

**修改文件**：`启动-生产环境.bat`、`start.bat`、`app.py`

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

## 2026-04-04 文档全面升级 + 必填字段修复

### 新增：业务部快速上手指南
**目标**：让业务人员5分钟内学会使用系统

**文档亮点**：
- **3分钟学会｜5秒生成** —— 直击效率痛点
- **四种录入方式** —— 直接填写、Excel粘贴、加载示例、批量导入
- **5个进阶技巧** —— 自动保存、企业微信导入、必填项提示、批量生成、隐私清除
- **效率对比表** —— 传统15分钟 vs 系统5秒，量化价值

**文件**：`docs/业务部快速上手指南.md`

### 更新：README 全面重构
- 添加核心亮点表格（一键生成、智能记忆、Excel互通等）
- 添加部门直达链接
- 添加项目更名说明
- 更简洁的文档导航

### 修复：风险合规部示例加载
- 修复单表格模式示例数据不填充问题
- 统一使用 `hot.propToCol()` 方法

---

## 2026-04-04 必填字段高亮彻底修复 + 企业微信集成

### 问题修复：必填字段高亮状态错乱
**现象**：填写多个必填字段时，只有最后填写的字段显示绿色，之前填好的会变回红色

**根本原因**：
- Handsontable 使用虚拟渲染，只渲染可见区域的单元格
- `afterChange` 回调在虚拟滚动时无法正确追踪所有单元格状态
- 直接操作 DOM 的元素在重新渲染后可能已被回收

**最终方案**：
- 使用 `afterRenderer` 回调替代 `afterChange`
- 在每次单元格渲染时根据当前值动态添加/移除 CSS 类
- 所有 4 个表格实例（pifu/hetong/defaults/single）统一实现

**修改文件**：`templates/dept_form.html`

### 功能新增：风险合规部企业微信按钮
**需求**：为风险合规部添加与业务部一致的快捷入口

**实现**：
- 按钮样式：SVG 图标 + 文字，与业务部保持一致
- 链接：`https://doc.weixin.qq.com/smartsheet/s3_AR8AOAZeAMgCNKpEHKoDWRtOU8QXM...`
- 交互：点击新开标签页，显示 Toast 提示用户复制信息后返回

**修改文件**：`templates/dept_form.html`

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
