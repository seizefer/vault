#!/usr/bin/env python3
"""
批量文件重命名工具
功能：
1. 根据EXIF信息重命名照片/视频
2. 支持自定义命名模板
3. 预览模式（不实际重命名）
4. 支持递归处理子文件夹

使用方法：
python file_renamer.py /path/to/photos --pattern "{year}-{month}-{day}_手机_照片_{counter}" --preview
"""

import argparse
from pathlib import Path
from datetime import datetime
import re
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
import hashlib


def get_exif_date(image_path):
    """从图片EXIF获取拍摄日期"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()

        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'DateTimeOriginal' or tag == 'DateTime':
                    # 格式: '2025:01:15 10:30:45'
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        pass

    # 如果无法从EXIF获取，使用文件修改时间
    return datetime.fromtimestamp(image_path.stat().st_mtime)


def get_file_date(file_path):
    """获取文件日期（优先EXIF，其次文件时间）"""
    if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff']:
        return get_exif_date(file_path)
    else:
        return datetime.fromtimestamp(file_path.stat().st_mtime)


def generate_new_name(file_path, pattern, counter, file_date=None):
    """
    根据模板生成新文件名

    支持的占位符：
    {year} - 年份 (2025)
    {month} - 月份 (01-12)
    {day} - 日期 (01-31)
    {hour} - 小时
    {minute} - 分钟
    {second} - 秒
    {counter} - 序号 (001, 002, ...)
    {original} - 原始文件名（不含扩展名）
    {ext} - 扩展名
    """
    if file_date is None:
        file_date = get_file_date(file_path)

    replacements = {
        'year': file_date.strftime('%Y'),
        'month': file_date.strftime('%m'),
        'day': file_date.strftime('%d'),
        'hour': file_date.strftime('%H'),
        'minute': file_date.strftime('%M'),
        'second': file_date.strftime('%S'),
        'counter': f'{counter:03d}',
        'original': file_path.stem,
        'ext': file_path.suffix[1:]  # 去掉点号
    }

    new_name = pattern
    for key, value in replacements.items():
        new_name = new_name.replace(f'{{{key}}}', value)

    return new_name + file_path.suffix


def detect_source(file_path):
    """检测文件来源（手机/相机/截图/下载）"""
    name = file_path.name.lower()

    if 'screenshot' in name or 'scr_' in name or '截图' in name:
        return '截图'
    elif name.startswith('img_') or name.startswith('photo'):
        return '手机'
    elif name.startswith('dsc_') or name.startswith('_dsc'):
        return '相机'
    elif name.startswith('download') or '下载' in name:
        return '下载'
    else:
        return '未知'


def batch_rename(
    directory,
    pattern=None,
    extensions=None,
    recursive=False,
    preview=True,
    auto_detect_source=False
):
    """
    批量重命名文件

    参数：
    - directory: 目标文件夹
    - pattern: 命名模板
    - extensions: 文件扩展名列表（如 ['.jpg', '.png']）
    - recursive: 是否递归处理子文件夹
    - preview: 预览模式（不实际重命名）
    - auto_detect_source: 自动检测来源
    """
    directory = Path(directory)

    if not directory.exists():
        print(f"❌ 目录不存在: {directory}")
        return

    # 默认模板
    if pattern is None:
        pattern = "{year}-{month}-{day}_{source}_照片_{counter}"

    # 默认扩展名（图片）
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                     '.mp4', '.mov', '.avi', '.mkv']

    # 收集文件
    if recursive:
        files = [f for f in directory.rglob('*') if f.suffix.lower() in extensions]
    else:
        files = [f for f in directory.glob('*') if f.suffix.lower() in extensions]

    if not files:
        print(f"❌ 未找到匹配的文件")
        return

    print(f"📁 目录: {directory}")
    print(f"🔍 找到 {len(files)} 个文件")
    print(f"📝 命名模板: {pattern}")
    print()

    # 按日期排序
    files_with_date = [(f, get_file_date(f)) for f in files]
    files_with_date.sort(key=lambda x: x[1])

    # 重命名
    rename_map = []
    counter = 1

    for file_path, file_date in files_with_date:
        # 如果启用自动检测来源
        current_pattern = pattern
        if auto_detect_source and '{source}' in pattern:
            source = detect_source(file_path)
            current_pattern = pattern.replace('{source}', source)

        new_name = generate_new_name(file_path, current_pattern, counter, file_date)
        new_path = file_path.parent / new_name

        # 如果文件名已存在，增加后缀
        if new_path.exists() and new_path != file_path:
            base = new_path.stem
            ext = new_path.suffix
            i = 1
            while new_path.exists():
                new_path = file_path.parent / f"{base}__{i}{ext}"
                i += 1

        rename_map.append((file_path, new_path, file_date))
        counter += 1

    # 显示预览
    print("📋 重命名预览:")
    print("-" * 80)
    for old_path, new_path, file_date in rename_map[:20]:  # 只显示前20个
        print(f"  {old_path.name}")
        print(f"  → {new_path.name}")
        print(f"    日期: {file_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    if len(rename_map) > 20:
        print(f"  ... 还有 {len(rename_map) - 20} 个文件")
        print()

    # 执行重命名
    if not preview:
        confirm = input(f"⚠️  确认重命名 {len(rename_map)} 个文件? (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            success = 0
            failed = 0

            for old_path, new_path, _ in rename_map:
                try:
                    old_path.rename(new_path)
                    success += 1
                except Exception as e:
                    print(f"❌ 重命名失败: {old_path.name} - {e}")
                    failed += 1

            print(f"\n✅ 成功重命名 {success} 个文件")
            if failed > 0:
                print(f"❌ 失败 {failed} 个文件")
        else:
            print("❌ 已取消")
    else:
        print("💡 这是预览模式，没有实际重命名文件")
        print("💡 使用 --execute 参数来执行实际重命名")


def main():
    parser = argparse.ArgumentParser(
        description='批量文件重命名工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览重命名
  python file_renamer.py /path/to/photos

  # 自定义模板并执行
  python file_renamer.py /path/to/photos --pattern "{year}-{month}-{day}_照片_{counter}" --execute

  # 只处理JPG文件
  python file_renamer.py /path/to/photos --ext .jpg .jpeg --execute

  # 递归处理子文件夹
  python file_renamer.py /path/to/photos --recursive --execute

  # 自动检测来源（手机/相机/截图）
  python file_renamer.py /path/to/photos --auto-source --execute

支持的占位符:
  {year}     - 年份 (2025)
  {month}    - 月份 (01-12)
  {day}      - 日期 (01-31)
  {hour}     - 小时
  {minute}   - 分钟
  {second}   - 秒
  {counter}  - 序号 (001, 002, ...)
  {source}   - 来源（需配合--auto-source）
  {original} - 原始文件名
  {ext}      - 扩展名
        """
    )

    parser.add_argument('directory', help='目标文件夹路径')
    parser.add_argument('--pattern', '-p',
                       default="{year}-{month}-{day}_照片_{counter}",
                       help='命名模板')
    parser.add_argument('--ext', nargs='+',
                       help='要处理的文件扩展名（如 .jpg .png）')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='递归处理子文件夹')
    parser.add_argument('--execute', action='store_true',
                       help='执行实际重命名（默认只预览）')
    parser.add_argument('--auto-source', action='store_true',
                       help='自动检测文件来源（手机/相机/截图）')

    args = parser.parse_args()

    batch_rename(
        directory=args.directory,
        pattern=args.pattern,
        extensions=[ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
                   for ext in args.ext] if args.ext else None,
        recursive=args.recursive,
        preview=not args.execute,
        auto_detect_source=args.auto_source
    )


if __name__ == '__main__':
    main()
