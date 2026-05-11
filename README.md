# 项目代码打包工具

将整个项目代码打包为单个文本文件，便于上传给 AI 进行分析、重构或架构审查。

## ✨ 功能特点

- 📁 **智能扫描**：自动遍历项目目录，过滤无关文件
- 🎯 **文件过滤**：只打包代码和文本文件，可自定义扩展名
- 🚫 **忽略目录**：自动跳过 `.git`、`node_modules` 等无需打包的目录
- 🌳 **目录结构**：在文件开头生成清晰的目录树
- 🤖 **AI 提示词**：自动添加适合 AI 理解的提示词
- 🔒 **安全读取**：自动尝试多种编码，避免读取失败
- 📊 **统计信息**：显示处理进度和最终统计

## 📦 使用方法

### 基础用法

只需要把exe文件放到要生成txt文件的文件夹然后运行就可以生成txt文件

### 自定义配置

编辑 `main()` 函数中的配置：

```python
def main():
    # 自定义输出文件名
    OUTPUT_NAME = "my_project.txt"
    
    # 添加更多忽略目录
    ignore_dirs = DEFAULT_IGNORE_DIRS | {'logs', 'temp'}
    
    # 添加更多文件类型
    extensions = DEFAULT_EXTENSIONS | {'.rs', '.rb'}
    
    # 限制单个文件最大 5MB
    max_file_size_mb = 5
    
    generate_project_txt(
        root_dir=PROJECT_PATH,
        output_file=OUTPUT_NAME,
        extensions=extensions,
        ignore_dirs=ignore_dirs,
        max_file_size_mb=max_file_size_mb,
    )
```

## 📝 输出格式

生成的文本文件包含以下部分：

1. **AI 提示词**：告诉 AI 如何理解文件结构
2. **目录结构**：项目的目录树（仅包含目标文件）
3. **文件内容**：每个文件的内容被以下标记包裹：
   ```
   --- START OF FILE: path/to/file.py ---
   文件内容...
   --- END OF FILE: path/to/file.py ---
   ```
4. **统计信息**：处理文件数、成功数、跳过数

## ⚙️ 默认配置

### 忽略的目录

- `.git`、`__pycache__`、`node_modules`、`venv`
- `.idea`、`.vscode`、`dist`、`bin`
- `.next`、`build`、`coverage`、`.pytest_cache`

### 包含的文件类型

- **后端**：`.go`、`.py`、`.java`、`.kt`、`.swift`、`.c`、`.cpp`、`.h`
- **前端**：`.js`、`.ts`、`.jsx`、`.tsx`、`.vue`、`.svelte`、`.html`、`.css`
- **配置**：`.json`、`.yaml`、`.yml`、`.xml`、`.md`、`.sql`
- **脚本**：`.sh`、`.bash`、`.zsh`、`.ps1`、`.bat`

## 🔧 系统要求

- Python 3.10+（使用了 `str | Path` 类型提示语法）
- 无需额外依赖（仅使用标准库）

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**作者**：AI Assistant  
**创建时间**：2026-05-11
