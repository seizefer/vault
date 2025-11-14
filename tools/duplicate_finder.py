#!/usr/bin/env python3
"""
文件去重工具
功能：
1. 查找重复文件（基于内容MD5，不只是文件名）
2. 智能保留策略（保留最新/最旧/最短路径）
3. 安全删除（可选移动到回收站）
4. 支持预览模式

使用方法：
python duplicate_finder.py /path/to/folder --preview
"""

import argparse
import hashlib
from pathlib import Path
from collections import defaultdict
import shutil
from datetime import datetime


def calculate_md5(file_path, chunk_size=8192):
    """计算文件MD5哈希值"""
    md5 = hashlib.md5()

    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        print(f"⚠️  无法读取文件: {file_path} - {e}")
        return None


def calculate_quick_hash(file_path, sample_size=1024*1024):
    """
    快速哈希（只读取文件开头和结尾）
    用于初步筛选，速度快但可能有误判
    """
    try:
        file_size = file_path.stat().st_size

        if file_size < sample_size * 2:
            # 小文件直接用完整MD5
            return calculate_md5(file_path)

        md5 = hashlib.md5()

        # 读取文件开头
        with open(file_path, 'rb') as f:
            md5.update(f.read(sample_size))

            # 读取文件结尾
            f.seek(-sample_size, 2)  # 从文件末尾往前
            md5.update(f.read(sample_size))

        # 加入文件大小作为哈希的一部分
        md5.update(str(file_size).encode())

        return 'quick_' + md5.hexdigest()
    except Exception as e:
        return None


def find_duplicates(
    directory,
    recursive=True,
    extensions=None,
    min_size=0,
    use_quick_hash=True
):
    """
    查找重复文件

    参数：
    - directory: 搜索目录
    - recursive: 是否递归
    - extensions: 文件扩展名过滤
    - min_size: 最小文件大小（字节），忽略太小的文件
    - use_quick_hash: 使用快速哈希（大文件推荐）
    """
    directory = Path(directory)

    if not directory.exists():
        print(f"❌ 目录不存在: {directory}")
        return {}

    print(f"🔍 扫描目录: {directory}")
    print(f"📁 递归: {'是' if recursive else '否'}")

    # 收集文件
    if recursive:
        files = [f for f in directory.rglob('*') if f.is_file()]
    else:
        files = [f for f in directory.glob('*') if f.is_file()]

    # 过滤扩展名
    if extensions:
        extensions = [ext.lower() for ext in extensions]
        files = [f for f in files if f.suffix.lower() in extensions]

    # 过滤文件大小
    files = [f for f in files if f.stat().st_size >= min_size]

    print(f"📄 找到 {len(files)} 个文件")
    print()

    # 第一步：按文件大小分组（相同大小才可能重复）
    print("📊 第1步：按文件大小分组...")
    size_groups = defaultdict(list)
    for f in files:
        size = f.stat().st_size
        size_groups[size].append(f)

    # 只保留有多个文件的组
    potential_duplicates = {size: files for size, files in size_groups.items()
                           if len(files) > 1}

    print(f"   发现 {len(potential_duplicates)} 组可能重复的文件")
    print()

    # 第二步：计算哈希值
    print("🔐 第2步：计算文件哈希值...")
    hash_groups = defaultdict(list)
    processed = 0
    total = sum(len(files) for files in potential_duplicates.values())

    for size, file_list in potential_duplicates.items():
        for file_path in file_list:
            if use_quick_hash and size > 10 * 1024 * 1024:  # 大于10MB用快速哈希
                file_hash = calculate_quick_hash(file_path)
            else:
                file_hash = calculate_md5(file_path)

            if file_hash:
                hash_groups[file_hash].append(file_path)

            processed += 1
            if processed % 100 == 0:
                print(f"   进度: {processed}/{total}")

    print(f"   完成: {processed}/{total}")
    print()

    # 只保留真正重复的（哈希值相同且文件数>1）
    duplicates = {h: files for h, files in hash_groups.items() if len(files) > 1}

    # 如果使用了快速哈希，对可疑的重复组进行完整MD5验证
    if use_quick_hash:
        print("🔍 第3步：验证快速哈希结果...")
        verified_duplicates = {}

        for file_hash, file_list in duplicates.items():
            if file_hash.startswith('quick_'):
                # 重新计算完整MD5
                md5_groups = defaultdict(list)
                for f in file_list:
                    full_md5 = calculate_md5(f)
                    if full_md5:
                        md5_groups[full_md5].append(f)

                # 加入验证后的结果
                for md5, files in md5_groups.items():
                    if len(files) > 1:
                        verified_duplicates[md5] = files
            else:
                verified_duplicates[file_hash] = file_list

        duplicates = verified_duplicates
        print("   验证完成")
        print()

    return duplicates


def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def select_files_to_keep(file_list, strategy='newest'):
    """
    选择要保留的文件

    策略：
    - newest: 保留最新的
    - oldest: 保留最旧的
    - shortest_path: 保留路径最短的
    - ask: 手动选择
    """
    if strategy == 'newest':
        # 按修改时间排序，保留最新的
        file_list.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return file_list[0], file_list[1:]

    elif strategy == 'oldest':
        # 保留最旧的
        file_list.sort(key=lambda f: f.stat().st_mtime)
        return file_list[0], file_list[1:]

    elif strategy == 'shortest_path':
        # 保留路径最短的（通常在更上层目录）
        file_list.sort(key=lambda f: len(str(f)))
        return file_list[0], file_list[1:]

    else:  # ask
        print("\n请选择要保留的文件：")
        for i, f in enumerate(file_list, 1):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            print(f"  {i}. {f}")
            print(f"     修改时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")

        while True:
            try:
                choice = int(input("输入序号 (1-{}): ".format(len(file_list))))
                if 1 <= choice <= len(file_list):
                    keep = file_list[choice - 1]
                    remove = [f for i, f in enumerate(file_list) if i != choice - 1]
                    return keep, remove
            except ValueError:
                pass
            print("❌ 无效输入，请重试")


def handle_duplicates(
    duplicates,
    strategy='newest',
    action='preview',
    trash_dir=None
):
    """
    处理重复文件

    action:
    - preview: 只预览
    - delete: 删除
    - move: 移动到指定文件夹
    """
    if not duplicates:
        print("✅ 没有发现重复文件")
        return

    print(f"🔍 发现 {len(duplicates)} 组重复文件")
    print()

    total_duplicates = sum(len(files) - 1 for files in duplicates.values())
    total_waste_size = sum(
        files[0].stat().st_size * (len(files) - 1)
        for files in duplicates.values()
    )

    print(f"📊 统计:")
    print(f"   重复文件数: {total_duplicates}")
    print(f"   浪费空间: {format_size(total_waste_size)}")
    print()

    # 处理每组重复
    files_to_remove = []

    for i, (file_hash, file_list) in enumerate(duplicates.items(), 1):
        print(f"📦 第 {i}/{len(duplicates)} 组重复:")
        print(f"   文件数: {len(file_list)}")
        print(f"   文件大小: {format_size(file_list[0].stat().st_size)}")
        print()

        for f in file_list:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            print(f"   - {f}")
            print(f"     修改时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")

        # 选择保留策略
        keep, remove = select_files_to_keep(file_list, strategy)

        print(f"\n   ✅ 保留: {keep.name}")
        print(f"   ❌ 删除: {len(remove)} 个文件")

        files_to_remove.extend(remove)
        print()
        print("-" * 80)
        print()

    # 执行操作
    if action == 'preview':
        print("💡 这是预览模式，没有删除任何文件")
        print(f"💡 将删除 {len(files_to_remove)} 个重复文件，释放 {format_size(total_waste_size)}")
        print("💡 使用 --delete 或 --move 参数来执行实际操作")

    elif action == 'delete':
        confirm = input(f"\n⚠️  确认删除 {len(files_to_remove)} 个文件? (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            success = 0
            failed = 0

            for f in files_to_remove:
                try:
                    f.unlink()
                    success += 1
                except Exception as e:
                    print(f"❌ 删除失败: {f} - {e}")
                    failed += 1

            print(f"\n✅ 成功删除 {success} 个文件")
            print(f"💾 释放空间: {format_size(total_waste_size)}")
            if failed > 0:
                print(f"❌ 失败 {failed} 个文件")
        else:
            print("❌ 已取消")

    elif action == 'move':
        if trash_dir is None:
            trash_dir = Path.cwd() / '_duplicates_trash'

        trash_dir = Path(trash_dir)
        trash_dir.mkdir(exist_ok=True)

        print(f"📁 移动到: {trash_dir}")

        confirm = input(f"\n⚠️  确认移动 {len(files_to_remove)} 个文件? (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            success = 0
            failed = 0

            for f in files_to_remove:
                try:
                    # 保持原有的目录结构
                    relative = f.relative_to(f.parent.parent)
                    target = trash_dir / relative
                    target.parent.mkdir(parents=True, exist_ok=True)

                    shutil.move(str(f), str(target))
                    success += 1
                except Exception as e:
                    print(f"❌ 移动失败: {f} - {e}")
                    failed += 1

            print(f"\n✅ 成功移动 {success} 个文件")
            if failed > 0:
                print(f"❌ 失败 {failed} 个文件")
        else:
            print("❌ 已取消")


def main():
    parser = argparse.ArgumentParser(
        description='文件去重工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览重复文件
  python duplicate_finder.py /path/to/folder

  # 只查找图片
  python duplicate_finder.py /path/to/folder --ext .jpg .png .gif

  # 保留最新的文件，删除其他
  python duplicate_finder.py /path/to/folder --strategy newest --delete

  # 移动重复文件到trash文件夹
  python duplicate_finder.py /path/to/folder --move --trash ./trash

  # 忽略小于1MB的文件
  python duplicate_finder.py /path/to/folder --min-size 1048576

策略说明:
  newest        - 保留最新修改的文件
  oldest        - 保留最旧的文件
  shortest_path - 保留路径最短的文件（通常在上层目录）
        """
    )

    parser.add_argument('directory', help='要扫描的目录')
    parser.add_argument('--recursive', '-r', action='store_true', default=True,
                       help='递归扫描子目录（默认启用）')
    parser.add_argument('--ext', nargs='+',
                       help='只处理指定扩展名的文件')
    parser.add_argument('--min-size', type=int, default=0,
                       help='最小文件大小（字节），忽略更小的文件')
    parser.add_argument('--strategy', choices=['newest', 'oldest', 'shortest_path'],
                       default='newest',
                       help='保留策略（默认: newest）')
    parser.add_argument('--delete', action='store_true',
                       help='删除重复文件')
    parser.add_argument('--move', action='store_true',
                       help='移动重复文件到trash目录')
    parser.add_argument('--trash',
                       help='trash目录路径（配合--move使用）')
    parser.add_argument('--no-quick-hash', action='store_true',
                       help='禁用快速哈希（更慢但更准确）')

    args = parser.parse_args()

    # 查找重复
    duplicates = find_duplicates(
        directory=args.directory,
        recursive=args.recursive,
        extensions=args.ext,
        min_size=args.min_size,
        use_quick_hash=not args.no_quick_hash
    )

    # 确定操作模式
    if args.delete:
        action = 'delete'
    elif args.move:
        action = 'move'
    else:
        action = 'preview'

    # 处理重复
    handle_duplicates(
        duplicates=duplicates,
        strategy=args.strategy,
        action=action,
        trash_dir=args.trash
    )


if __name__ == '__main__':
    main()
