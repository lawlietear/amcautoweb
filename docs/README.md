# 山东金融资产智能文书系统

> AMC 文书生成器 Web 版 v2.1.0

基于 Flask + Handsontable 的智能文书生成系统，支持风险合规部批复文档和业务部合同文档的批量生成。

---

## 功能特性

- **双部门支持**：风险合规部（批复）+ 业务部（合同）
- **智能模板**：自动识别分期/一次性业务类型
- **双表格设计**：批复信息与合同信息同步录入
- **批量生成**：支持 Excel 导入、多行数据批量生成
- **金额自动化**：千分位格式化 + 中文大写自动转换
- **审计日志**：完整的操作记录与密码保护
- **并发支持**：Waitress 生产服务器，支持多人同时访问

---

## 快速开始

### 安装依赖

```bash
pip install flask docxtpl pandas openpyxl waitress
```

### 启动服务

```bash
python app.py
```

访问 http://127.0.0.1:5000

---

## 使用文档

| 文档 | 说明 | 目标读者 |
|------|------|---------|
| [📘 用户手册](docs/用户手册.md) | 详细操作指南 | 最终用户 |
| [📗 部署指南](docs/部署指南.md) | 环境配置、安装步骤 | 系统管理员 |
| [📙 开发文档](docs/开发文档.md) | 架构、数据结构、实现细节 | 开发者 |
| [📕 CHANGELOG](CHANGELOG.md) | 版本变更历史 | 所有用户 |
| [📊 Progress](progress.md) | 开发进展记录 | 开发者 |

---

## 项目结构

```
autodocweb_v2/
├── app.py                 # Flask 主程序
├── core/                  # 核心模块
│   ├── config.py         # 统一配置（v2.1新增）
│   ├── document_generator.py  # 文档生成
│   ├── format_utils.py   # 格式化工具
│   ├── excel_handler.py  # Excel处理
│   └── notification.py   # 通知日志
├── config/                # 部门配置（JSON）
├── templates/             # HTML 模板
├── static/                # 静态资源（CSS、图片）
├── word_templates/        # Word 模板（.docx）
├── generated/             # 生成文件输出
└── docs/                  # 项目文档
```

---

## 技术栈

- **后端**: Flask + Waitress
- **前端**: Handsontable 14.0.0
- **文档处理**: python-docx / docxtpl
- **Excel 处理**: pandas / openpyxl
- **日志**: Python logging + RotatingFileHandler

---

## 默认访问信息

- **首页**: http://localhost:5000
- **审计日志**: http://localhost:5000/audit_log
- **审计密码**: `amc2026`

---

## 相关文档

- [CHANGELOG](CHANGELOG.md) - 版本变更记录
- [progress.md](progress.md) - 开发进展记录
- [docs/用户手册.md](docs/用户手册.md) - 用户操作指南
- [docs/部署指南.md](docs/部署指南.md) - 系统部署说明
- [docs/开发文档.md](docs/开发文档.md) - 开发者技术文档
