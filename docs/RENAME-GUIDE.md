# 项目重命名指南

## 从 `autodocweb_v2` 重命名为 `amc-doc-generator`

---

## 步骤 1：停止服务

```powershell
# 停止所有 Python 进程
taskkill /F /IM python.exe
```

---

## 步骤 2：重命名文件夹

### 方法 A：Windows 资源管理器（推荐）
1. 关闭 VS Code / 其他编辑器
2. 右键文件夹 → 重命名
3. `autodocweb_v2` → `amc-doc-generator`

### 方法 B：命令行
```powershell
cd Z:\Work\WorkDock\01_Active
rename autodocweb_v2 amc-doc-generator
```

---

## 步骤 3：重新创建虚拟环境（推荐）

虚拟环境包含硬编码路径，重命名后建议重建：

```powershell
cd Z:\Work\WorkDock\01_Active\amc-doc-generator

# 备份旧环境（可选）
rename .venv .venv.old

# 创建新虚拟环境
python -m venv .venv

# 激活并安装依赖
.venv\Scripts\activate
pip install -r requirements.txt
```

> **注意**：如果 `.venv` 中有重要配置，可以尝试直接修改 `.venv\Scripts\activate.bat` 中的路径

---

## 步骤 4：更新快捷方式（如有）

如果桌面或任务栏有快捷方式，需要更新目标路径：

```
旧目标：Z:\Work\WorkDock\01_Active\autodocweb_v2\start.bat
新目标：Z:\Work\WorkDock\01_Active\amc-doc-generator\start.bat
```

---

## 步骤 5：重新打开项目

1. 在 VS Code 中：
   - 关闭旧项目
   - File → Open Folder → 选择 `amc-doc-generator`

2. 启动服务：
   ```powershell
   .\start.bat
   ```

---

## 已同步修改的文件

以下文件已在重命名前更新：

| 文件 | 修改内容 |
|------|----------|
| `start.bat` | 窗口标题改为 "AMC Doc Generator" |
| `docs/progress.md` | 添加重命名记录 |

---

## 可选：删除临时文件

重命名后可以安全删除的文件：

```powershell
# 临时修复脚本
del fix_risk.py
del fix_template.py
del fix_setup.py
del verify_setup.py
del extract_variables.py

# 备份文件
del templates\dept_form.html.bak*

# 旧虚拟环境（确认新环境正常后）
rmdir /S /Q .venv.old
```

---

## 故障排除

### 问题 1：`ModuleNotFoundError`
**原因**：虚拟环境路径错误
**解决**：按步骤 3 重新创建虚拟环境

### 问题 2：Flask 启动但页面空白
**原因**：模板缓存
**解决**：
```powershell
.venv\Scripts\activate
pip install --force-reinstall -r requirements.txt
```

### 问题 3：快捷方式失效
**原因**：路径硬编码
**解决**：重新创建快捷方式或修改目标路径

---

## 验证清单

- [ ] 文件夹已重命名
- [ ] 虚拟环境已重建或更新
- [ ] `start.bat` 能正常启动
- [ ] http://127.0.0.1:5000 能访问
- [ ] 风险合规部和业务部功能正常
- [ ] 文档生成正常

---

**最后更新**：2026-04-04
