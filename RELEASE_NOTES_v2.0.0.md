# AMC 文书生成器 v2.0.0 发布说明

**发布日期**: 2026-03-12  
**版本号**: v2.0.0  
**代号**: "协同办公"

---

## 📦 系统要求

| 组件 | 要求 |
|-----|------|
| 操作系统 | Windows 10/11 / Linux / macOS |
| Python | 3.8 或更高版本 |
| 内存 | 建议 8GB 及以上 |
| 网络 | 局域网互通 |

---

## 🚀 主要亮点

### 1. 支持团队协作
**从单用户升级为多用户并发**
- 采用 Waitress 生产服务器（8 线程）
- 支持 5-8 人同时在线操作
- 性能提升 300%，告别排队等待

### 2. 模板库扩展
**风险合规部新增收购业务类型**
- 覆盖一次性业务、分期处置、收购业务三大场景
- 自动识别并填充 14 个关键变量
- 智能金额格式化（千分位+中文大写）

### 3. 隐私保护增强
**敏感信息不再泄露**
- 最近使用脱敏显示（只显示部门+文档类型）
- 不再本地存储债务人名称、合同编号
- 适合公共办公环境使用

---

## 📋 功能清单

### 核心功能 ✅
- [x] 一次性业务批复生成
- [x] 分期处置批复生成
- [x] 收购业务批复生成（新增）
- [x] 债权转让合同生成（分期/非分期）
- [x] Excel 批量导入
- [x] 金额自动转中文大写
- [x] 本地自动保存与恢复

### 筛选与统计 ✅
- [x] 操作日志日期筛选（今天/昨天/7天/30天/自定义）
- [x] 部门筛选（风险合规部/业务部）
- [x] 关键词搜索
- [x] 今日生成统计
- [x] 独立 IP 统计

### 用户体验 ✅
- [x] 最近使用脱敏显示
- [x] Art Deco 风格界面
- [x] 自动生成当日日期
- [x] 必填字段提醒
- [x] 一键加载示例数据

---

## 🔧 安装与启动

### 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
python app.py

# 3. 访问系统
# 本机: http://127.0.0.1:5000
# 局域网: http://<本机IP>:5000
```

### 防火墙配置（Windows）

```powershell
# 以管理员身份运行 PowerShell
netsh advfirewall firewall add rule name="AMC文书系统" dir=in action=allow protocol=tcp localport=5000
```

---

## 📁 文件结构

```
autodocweb_v2/
├── app.py                      # 主程序 (v2.0.0)
├── requirements.txt            # Python依赖
├── CHANGELOG.md               # 版本变更日志
├── DEPLOY_GUIDE.md            # 部署指南
├── RELEASE_NOTES_v2.0.0.md    # 本文件
├── config/                    # 配置文件
│   ├── config_business.json
│   └── config_risk_compliance.json
├── core/                      # 核心模块
│   ├── document_generator.py
│   ├── format_utils.py
│   ├── excel_handler.py
│   └── notification.py
├── templates/                 # HTML模板
├── static/                    # CSS/JS资源
├── word_templates/            # Word模板文件
└── generated/                 # 生成文件输出目录
```

---

## 🐛 已知问题

| 问题 | 状态 | 解决方案 |
|-----|------|---------|
| 静态文件缓存 | ✅ 已解决 | 添加版本号参数 |
| 中文括号文件名 | ✅ 已解决 | 保留原始格式 |
| FormatUtils 作用域 | ✅ 已解决 | 方法内重新导入 |

---

## 🔮 未来规划

### v2.1.0（计划中）
- [ ] 用户登录与权限管理
- [ ] 数据库存储（替代 LocalStorage）
- [ ] 批量生成进度条
- [ ] 模板在线编辑

### v3.0.0（长期）
- [ ] 新增法务部模板
- [ ] 前后端分离架构
- [ ] 云端部署支持
- [ ] 移动端适配

---

## 🤝 贡献与支持

### 问题反馈
如有问题，请检查：
1. Flask 控制台错误日志
2. 浏览器开发者工具 (F12) Console
3. 审计日志页面 `/audit_log`

### 常用命令

```bash
# 查看版本
python -c "import app; print(app.__version__)"

# 清理缓存（浏览器控制台）
localStorage.clear()
```

---

## 📄 许可证

内部系统 · 山东省金融资产管理股份有限公司

---

**感谢使用 AMC 文书生成器！**

如有建议或问题，欢迎反馈。
