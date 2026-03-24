# AMC 文书生成器 - Web 版（重构版）

## 项目结构

```
autodocweb_v2/
├── app.py                      # Flask 主入口
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── document_generator.py   # 文档生成（整合公文格式）
│   ├── format_utils.py         # 格式化工具（金额、日期）
│   ├── excel_handler.py        # Excel 处理
│   └── notification.py         # 通知和日志
├── templates/                  # HTML 模板
│   ├── index.html              # 首页
│   └── dept_form.html          # 部门表单页
├── static/                     # 静态资源
│   └── css/
│       └── style.css           # 样式表
├── config/                     # 配置文件
│   ├── config_风险合规部.json
│   └── config_业务部.json
├── generated/                  # 生成文件目录
│   ├── 风险合规部/
│   └── 业务部/
├── start.bat                   # Windows 启动脚本
└── README.md                   # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
pip install flask docxtpl pandas openpyxl python-docx requests
```

### 2. 配置模板

将 Word 模板文件路径配置到 `config/` 目录的 JSON 文件中：

```json
{
    "dept_name": "风险合规部",
    "template_path": "G:/Templates/批复模板.docx",
    "variables": [...]
}
```

### 3. 启动服务

双击 `start.bat` 或在命令行运行：

```bash
python app.py
```

访问 http://127.0.0.1:5000

## 功能特性

### 与原版的改进

1. **代码结构清晰**
   - 核心功能拆分到独立模块
   - HTML 模板外置，易于维护
   - CSS 独立，方便调整样式

2. **功能整合**
   - 整合了 `generate_pifu.py` 的公文格式处理
   - 支持 Excel 批量导入
   - 完整的审计日志

3. **易用性提升**
   - 一键启动脚本
   - 更好的错误提示
   - 响应式设计，支持移动端

## 配置文件格式

### 部门配置 (config_*.json)

```json
{
    "dept_name": "风险合规部",
    "dept_icon": "⚖️",
    "template_path": "G:/Templates/批复模板.docx",
    "filename_pattern": "批复_{doc_full_no}.docx",
    "variables": [
        {
            "key": "doc_full_no",
            "label": "批复文号",
            "type": "text",
            "required": true,
            "category": "基本信息"
        }
    ]
}
```

## 与原版的差异

| 功能 | 旧版 (app.py) | 新版 (autodocweb_v2) |
|------|--------------|---------------------|
| 代码组织 | 单文件 1000+ 行 | 模块化，职责分离 |
| HTML 模板 | 内嵌 Python | 外置模板文件 |
| 公文格式 | 不支持 | 完整支持（来自 generate_pifu.py）|
| Excel 导入 | 不支持 | 支持 |
| 样式维护 | 困难 | CSS 独立文件 |
| 扩展性 | 差 | 好（模块化设计）|

## 迁移指南

### 从旧版迁移

1. 复制 `config_*.json` 到 `config/` 目录
2. 确保 `template_path` 指向正确的 Word 模板
3. 运行 `start.bat` 启动

## 故障排除

### 问题：无法加载配置
- 检查 `config/` 目录是否有 `config_风险合规部.json` 等文件
- 检查 JSON 格式是否正确

### 问题：模板找不到
- 检查配置中的 `template_path` 是否为绝对路径
- 检查文件是否存在

### 问题：中文乱码
- 确保文件编码为 UTF-8
- Windows 命令行使用 `chcp 65001` 设置 UTF-8

## 技术栈

- **后端**: Flask (Python)
- **模板引擎**: Jinja2
- **文档处理**: python-docx, docxtpl
- **表格组件**: Handsontable
- **Excel 处理**: pandas, openpyxl
