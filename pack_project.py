#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目代码打包工具
将整个项目代码打包为单个文本文件，便于 AI 分析和处理
"""

import os
from pathlib import Path
from typing import Set, Optional

# ============ 默认配置常量 ============
DEFAULT_IGNORE_DIRS: Set[str] = {
    '.git', '__pycache__', 'node_modules', 'venv', 
    '.idea', '.vscode', 'dist', 'bin', '.exe',
    '.next', 'build', 'coverage', '.pytest_cache'
}

DEFAULT_EXTENSIONS: Set[str] = {
    '.go', '.py', '.js', '.ts', '.jsx', '.tsx',
    '.c', '.cpp', '.h', '.hpp', '.java', '.kt', '.swift',
    '.md', '.sql', '.yaml', '.yml', '.json', '.txt', '.xml',
    '.html', '.css', '.scss', '.less', '.vue', '.svelte',
    '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd'
}

MAX_FILE_SIZE_MB: int = 10  # 最大文件大小限制（MB）

AI_PROMPT_TEMPLATE: str = """我上传了一个包含我整个项目代码的文本文件。

文件开头有整个项目的目录结构。
每个文件的内容被 --- START OF FILE: [路径] --- 和 --- END OF FILE --- 包裹。
请阅读所有代码，并根据我的后续指令（如代码重构、寻找 Bug 或架构分析）进行回答。目前你只需要确认你已完整接收并理解了项目结构即可。

================================================================================
"""


def generate_project_txt(
    root_dir: str | Path,
    output_file: str | Path,
    extensions: Optional[Set[str]] = None,
    ignore_dirs: Optional[Set[str]] = None,
    max_file_size_mb: int = MAX_FILE_SIZE_MB
) -> None:
    """
    将项目文件打包为单个文本文件，并在开头附加 AI 提示词。
    
    Args:
        root_dir: 项目根目录路径
        output_file: 输出文件路径
        extensions: 要包含的文件扩展名集合（含点号，如 '.py'）
        ignore_dirs: 要忽略的目录名集合
        max_file_size_mb: 单个文件最大大小（MB），防止读取超大文件
    """
    # 使用默认配置
    ignore_dirs = ignore_dirs or DEFAULT_IGNORE_DIRS
    extensions = extensions or DEFAULT_EXTENSIONS
    max_file_size_bytes = max_file_size_mb * 1024 * 1024
    
    root_path = Path(root_dir).resolve()
    output_path = Path(output_file)
    
    # 收集所有符合条件的文件
    print(f"🔍 正在扫描项目目录: {root_path}")
    files_to_process = []
    
    for root, dirs, files in os.walk(root_path):
        # 原地修改 dirs，避免进入忽略的目录
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            file_path = Path(root) / file
            ext = file_path.suffix.lower()
            
            if ext in extensions:
                rel_path = file_path.relative_to(root_path)
                files_to_process.append((file_path, rel_path))
    
    print(f"📊 找到 {len(files_to_process)} 个符合条件的文件\n")
    
    # 生成输出文件
    with open(output_path, 'w', encoding='utf-8') as f_out:
        # 1. 写入 AI 提示词
        f_out.write(AI_PROMPT_TEMPLATE)
        
        # 2. 写入目录结构预览
        f_out.write("===== PROJECT STRUCTURE =====\n")
        _write_directory_tree(f_out, root_path, ignore_dirs, extensions)
        
        f_out.write("\n\n===== FILE CONTENTS =====\n")
        
        # 3. 写入文件内容
        processed_count = 0
        skipped_count = 0
        
        for file_path, rel_path in files_to_process:
            try:
                # 检查文件大小
                file_size = file_path.stat().st_size
                if file_size > max_file_size_bytes:
                    print(f"⚠️  跳过 {rel_path} (文件过大: {file_size / 1024 / 1024:.2f} MB)")
                    skipped_count += 1
                    continue
                
                # 读取并写入文件内容
                content = _read_file_safe(file_path)
                if content is not None:
                    f_out.write(f"\n\n--- START OF FILE: {rel_path} ---\n")
                    f_out.write(content)
                    f_out.write(f"\n--- END OF FILE: {rel_path} ---\n")
                    processed_count += 1
                    print(f"✅ 已处理: {rel_path}")
                else:
                    skipped_count += 1
                    
            except Exception as e:
                print(f"❌ 跳过文件 {rel_path} (错误: {e})")
                skipped_count += 1
        
        # 4. 写入统计信息
        f_out.write(f"\n\n===== SUMMARY =====\n")
        f_out.write(f"总文件数: {len(files_to_process)}\n")
        f_out.write(f"成功处理: {processed_count}\n")
        f_out.write(f"跳过文件: {skipped_count}\n")
    
    print(f"\n🎉 打包完成！文件已保存至: {output_path}")
    print(f"📦 输出文件大小: {output_path.stat().st_size / 1024 / 1024:.2f} MB")


def _write_directory_tree(
    f_out,
    root_path: Path,
    ignore_dirs: Set[str],
    extensions: Set[str]
) -> None:
    """写入目录树结构（仅包含目标文件类型）"""
    for root, dirs, files in os.walk(root_path):
        # 过滤忽略的目录
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        level = Path(root).relative_to(root_path).parts
        indent = ' ' * 4 * len(level)
        
        # 写入目录名
        dir_name = os.path.basename(root) if root != str(root_path) else root_path.name
        f_out.write(f"{indent}{dir_name}/\n")
        
        # 写入符合条件的文件名
        sub_indent = ' ' * 4 * (len(level) + 1)
        for f in sorted(files):
            if Path(f).suffix.lower() in extensions:
                f_out.write(f"{sub_indent}{f}\n")


def _read_file_safe(file_path: Path) -> Optional[str]:
    """
    安全地读取文件内容，尝试多种编码。
    
    Returns:
        文件内容字符串，如果读取失败则返回 None
    """
    encodings = ['utf-8', 'gbk', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception:
            return None
    
    print(f"⚠️  无法解码文件: {file_path} (尝试的编码: {', '.join(encodings)})")
    return None


def main():
    """主函数：配置并运行打包脚本"""
    # 配置参数
    PROJECT_PATH = Path(".")  # 当前目录
    OUTPUT_NAME = "full_project_context.txt"
    
    # 可选：自定义配置
    # ignore_dirs = DEFAULT_IGNORE_DIRS | {'logs', 'temp'}  # 添加更多忽略目录
    # extensions = DEFAULT_EXTENSIONS | {'.rs', '.rb'}  # 添加更多扩展名
    # max_file_size_mb = 5  # 限制单个文件最大 5MB
    
    try:
        generate_project_txt(
            root_dir=PROJECT_PATH,
            output_file=OUTPUT_NAME,
            # extensions=extensions,  # 可选
            # ignore_dirs=ignore_dirs,  # 可选
            # max_file_size_mb=max_file_size_mb,  # 可选
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        raise


if __name__ == "__main__":
    main()
