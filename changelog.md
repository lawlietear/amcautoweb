# Changelog

## 2026-04-13

### 分期模板下禁用违约金比例最后两列

**完成内容**：
- 在 `templates/dept_form.html` 新增 `updatePenaltyColumnsReadOnly()` 函数，根据模板类型控制甲方信息表格最后两列（`penalty_percent_10_3_2`、`penalty_percent_10_3_3`）的只读状态。
- 当选择分期付款模板（`fenqi`）时，这两列设为 `readOnly` 并添加深灰色背景（`.read-only-penalty`），不可编辑；切换回非分期模板时恢复可编辑并移除背景色。
- 在 `onTemplateChange()` 和 `hotDefaults` 初始化完成后均调用该函数，确保切换和首次加载时状态正确。
- 修复 `detectBusinessType()` 函数：在自动修改 `templateSelect.value` 后，追加调用 `onTemplateChange()`，防止模板切换后只读状态、条款默认值等 UI 未同步的问题。
- 将 `hotDefaults` 等 Handsontable 实例暴露到 `window`，便于浏览器调试和 Playwright 自动化测试。

**关键决策**：
- 复用现有的 `templateSelect` 和 `hotDefaults` 架构，通过 Handsontable 的 `setCellMeta(0, colIdx, 'readOnly', true/false)` + `className` + `render()` 实现动态禁用和视觉提示，无需重建整个 `columns` 配置。

**验证方式**：
- 启动 Flask 服务后，在浏览器中切换业务部门页面的模板选择器，观察最后两列的编辑状态变化和深灰背景。
- 运行 Playwright 回归测试脚本，验证 `fenqi` 下 `readOnly` + `className` 正确设置，切回 `yicixing` 后完全恢复。

### 修复金额中文大写转换逻辑

**完成内容**：
- 修复 `core/format_utils.py` 中 `amount_to_chinese` 及 `_int_to_chinese` 方法的多处缺陷。

**关键决策**：
- 发现三个互相影响的 Bug：
  1. 跨 4 位分组（万/亿）时低位不足 1000 未正确补 "零"；
  2. 存在 `replace('零万', '万')` 等破坏性字符串替换，误删合法 "零"；
  3. 小数部分 "有分无角" 且整数部分非零时未补 "零"。
- 一并修复 `amount_to_chinese` 中 `0` 因 `if not amount` 判断返回空字符串的问题。

**验证方式**：
- 累计运行 71 组测试，覆盖：
  - 1-6 位小额
  - 7-9 位中额
  - 8 位以上带两位小数大额
  - 低位分组恰好为 1000 的边界场景
- 全部通过，测试脚本及结果存于 `../../03_Temp/amount_test_*.txt`。

**还有什么待解决**：
- 合同中 "过渡期内标的债权收益归属和费用承担" 条款的存储与注入机制已梳理清楚（见下），暂无需代码变更。

### 梳理条款文本存储与注入链路

**完成内容**：
- 明确网站前端选择项（`templates/dept_form.html` radio 按钮）→ `app.py` `_apply_clause_logic` → 从 `core/config.py` 的 `CLAUSE_CONFIG` 字典读取硬编码文本 → 注入 docx 模板占位符（`{{ transition_income_clause }}` / `{{ fenqi_transition_income_clause }}` 等）。

**关键决策**：
- 条款文本目前以硬编码字典形式维护，如需修改直接编辑 `core/config.py` 即可；模板文件（`word_templates/template_债权转让协议_*.docx`）仅含占位符，不含实际条款内容。
