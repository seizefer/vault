#!/usr/bin/env python3
"""
个人信息系统自动化工具集合

功能：
1. 自动清理临时文件
2. 生成每日/每周报告
3. 自动备份重要文件
4. 批量处理常见任务

使用方法：
python automation_scripts.py <command> [options]
"""

import argparse
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json
import subprocess
import sys


class AutomationToolkit:
    def __init__(self):
        self.home_dir = Path.home()
        self.config_file = Path(__file__).parent / 'automation_config.json'
        self.load_config()

    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            # 默认配置
            self.config = {
                'download_dir': str(self.home_dir / 'Downloads'),
                'desktop_dir': str(self.home_dir / 'Desktop'),
                'backup_dir': str(self.home_dir / 'Backups'),
                'photo_dirs': [
                    str(self.home_dir / 'Pictures'),
                    str(self.home_dir / '图片')
                ],
                'clean_days': 30,  # 清理超过N天的文件
                'backup_retention_days': 90
            }
            self.save_config()

    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def auto_clean_downloads(self, dry_run=True):
        """
        自动清理下载文件夹
        - 删除超过N天的文件
        - 保留最近使用的
        """
        download_dir = Path(self.config['download_dir'])

        if not download_dir.exists():
            print(f"❌ 下载文件夹不存在: {download_dir}")
            return

        print(f"🔍 扫描下载文件夹: {download_dir}")

        cutoff_date = datetime.now() - timedelta(days=self.config['clean_days'])
        files_to_delete = []
        total_size = 0

        for file_path in download_dir.iterdir():
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

                if mtime < cutoff_date:
                    size = file_path.stat().st_size
                    files_to_delete.append((file_path, size, mtime))
                    total_size += size

        print(f"\n📊 统计:")
        print(f"  找到 {len(files_to_delete)} 个超过 {self.config['clean_days']} 天的文件")
        print(f"  可释放空间: {total_size / (1024**3):.2f} GB")
        print()

        if not files_to_delete:
            print("✅ 下载文件夹已经很整洁了！")
            return

        if dry_run:
            print("📋 将删除以下文件（预览模式）:")
            for file_path, size, mtime in sorted(files_to_delete, key=lambda x: x[2]):
                print(f"  - {file_path.name}")
                print(f"    大小: {size / (1024**2):.2f} MB")
                print(f"    修改时间: {mtime.strftime('%Y-%m-%d %H:%M')}")
            print("\n💡 使用 --execute 参数来实际执行删除")
        else:
            confirm = input(f"\n⚠️  确认删除 {len(files_to_delete)} 个文件? (yes/no): ")
            if confirm.lower() in ['yes', 'y']:
                deleted = 0
                for file_path, _, _ in files_to_delete:
                    try:
                        file_path.unlink()
                        deleted += 1
                    except Exception as e:
                        print(f"❌ 删除失败: {file_path.name} - {e}")

                print(f"\n✅ 成功删除 {deleted} 个文件")
                print(f"💾 释放空间: {total_size / (1024**3):.2f} GB")
            else:
                print("❌ 已取消")

    def auto_clean_desktop(self, dry_run=True):
        """
        自动整理桌面
        - 将文件移动到对应文件夹
        """
        desktop_dir = Path(self.config['desktop_dir'])

        if not desktop_dir.exists():
            print(f"❌ 桌面文件夹不存在: {desktop_dir}")
            return

        print(f"🔍 扫描桌面: {desktop_dir}")

        # 创建分类文件夹
        organize_dirs = {
            'documents': desktop_dir / '_整理_文档',
            'images': desktop_dir / '_整理_图片',
            'archives': desktop_dir / '_整理_压缩包',
            'others': desktop_dir / '_整理_其他'
        }

        file_categories = {
            'documents': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
        }

        files_to_move = []

        for file_path in desktop_dir.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()

                # 确定分类
                category = 'others'
                for cat, extensions in file_categories.items():
                    if ext in extensions:
                        category = cat
                        break

                # 跳过快捷方式
                if ext in ['.lnk', '.url']:
                    continue

                files_to_move.append((file_path, category))

        if not files_to_move:
            print("✅ 桌面已经很整洁了！")
            return

        print(f"\n📊 统计:")
        for category in set(c for _, c in files_to_move):
            count = sum(1 for _, c in files_to_move if c == category)
            print(f"  {category}: {count} 个文件")

        if dry_run:
            print("\n📋 将移动以下文件（预览模式）:")
            for file_path, category in files_to_move:
                print(f"  {file_path.name} → {organize_dirs[category].name}")
            print("\n💡 使用 --execute 参数来实际执行移动")
        else:
            # 创建目标文件夹
            for dir_path in organize_dirs.values():
                dir_path.mkdir(exist_ok=True)

            confirm = input(f"\n⚠️  确认移动 {len(files_to_move)} 个文件? (yes/no): ")
            if confirm.lower() in ['yes', 'y']:
                moved = 0
                for file_path, category in files_to_move:
                    try:
                        target_dir = organize_dirs[category]
                        target_path = target_dir / file_path.name

                        # 如果文件已存在，添加序号
                        if target_path.exists():
                            base = target_path.stem
                            ext = target_path.suffix
                            i = 1
                            while target_path.exists():
                                target_path = target_dir / f"{base}_{i}{ext}"
                                i += 1

                        shutil.move(str(file_path), str(target_path))
                        moved += 1
                    except Exception as e:
                        print(f"❌ 移动失败: {file_path.name} - {e}")

                print(f"\n✅ 成功移动 {moved} 个文件")
                print(f"📁 文件已整理到桌面的「_整理_XXX」文件夹中")
            else:
                print("❌ 已取消")

    def generate_daily_summary(self):
        """
        生成每日总结报告
        - 今天创建/修改的文件
        - 文件操作统计
        """
        print("📊 生成每日总结...")

        today = datetime.now().date()
        summary = {
            'date': today.isoformat(),
            'files_created': [],
            'files_modified': [],
            'total_files_created': 0,
            'total_files_modified': 0
        }

        # 扫描主要目录
        scan_dirs = [
            self.home_dir / 'Documents',
            self.home_dir / 'Downloads',
            self.home_dir / 'Desktop'
        ]

        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue

            for file_path in scan_dir.rglob('*'):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        ctime = datetime.fromtimestamp(stat.st_ctime).date()
                        mtime = datetime.fromtimestamp(stat.st_mtime).date()

                        if ctime == today:
                            summary['files_created'].append(str(file_path))
                            summary['total_files_created'] += 1

                        if mtime == today and ctime != today:
                            summary['files_modified'].append(str(file_path))
                            summary['total_files_modified'] += 1

                    except (PermissionError, OSError):
                        pass

        # 打印总结
        print("\n" + "=" * 60)
        print(f"📅 每日总结 - {today}")
        print("=" * 60)
        print(f"新建文件: {summary['total_files_created']} 个")
        print(f"修改文件: {summary['total_files_modified']} 个")

        if summary['files_created']:
            print("\n📄 新建的文件（最多显示10个）:")
            for file_path in summary['files_created'][:10]:
                print(f"  - {Path(file_path).name}")

        if summary['files_modified']:
            print("\n✏️  修改的文件（最多显示10个）:")
            for file_path in summary['files_modified'][:10]:
                print(f"  - {Path(file_path).name}")

        print("\n" + "=" * 60)

        return summary

    def auto_backup(self, dry_run=True):
        """
        自动备份重要文件
        - 备份到指定目录
        - 保留最近N天的备份
        """
        backup_dir = Path(self.config['backup_dir'])
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        today_backup_dir = backup_dir / f"backup_{timestamp}"

        print(f"💾 准备备份到: {today_backup_dir}")

        # 要备份的目录
        backup_sources = [
            self.home_dir / 'Documents' / 'Important',  # 重要文档
            self.home_dir / 'Desktop',  # 桌面
            # 可以添加更多
        ]

        total_size = 0
        files_to_backup = []

        for source_dir in backup_sources:
            if source_dir.exists():
                for file_path in source_dir.rglob('*'):
                    if file_path.is_file():
                        size = file_path.stat().st_size
                        files_to_backup.append((file_path, source_dir))
                        total_size += size

        print(f"\n📊 备份统计:")
        print(f"  文件数量: {len(files_to_backup)}")
        print(f"  总大小: {total_size / (1024**3):.2f} GB")

        if dry_run:
            print("\n💡 使用 --execute 参数来实际执行备份")
            return

        confirm = input(f"\n⚠️  确认备份 {len(files_to_backup)} 个文件? (yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            print("❌ 已取消")
            return

        # 执行备份
        today_backup_dir.mkdir(exist_ok=True)
        backed_up = 0

        for file_path, source_dir in files_to_backup:
            try:
                # 保持目录结构
                relative_path = file_path.relative_to(source_dir)
                target_path = today_backup_dir / source_dir.name / relative_path

                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, target_path)
                backed_up += 1

            except Exception as e:
                print(f"❌ 备份失败: {file_path.name} - {e}")

        print(f"\n✅ 成功备份 {backed_up} 个文件")
        print(f"📁 备份位置: {today_backup_dir}")

        # 清理旧备份
        self.cleanup_old_backups()

    def cleanup_old_backups(self):
        """清理旧备份"""
        backup_dir = Path(self.config['backup_dir'])
        if not backup_dir.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=self.config['backup_retention_days'])
        deleted = 0

        for backup_subdir in backup_dir.iterdir():
            if backup_subdir.is_dir() and backup_subdir.name.startswith('backup_'):
                try:
                    # 从文件夹名提取日期
                    date_str = backup_subdir.name.split('_')[1]
                    backup_date = datetime.strptime(date_str, '%Y%m%d')

                    if backup_date < cutoff_date:
                        shutil.rmtree(backup_subdir)
                        deleted += 1
                        print(f"🗑️  删除旧备份: {backup_subdir.name}")

                except (ValueError, IndexError):
                    pass

        if deleted > 0:
            print(f"✅ 清理了 {deleted} 个旧备份")


def main():
    parser = argparse.ArgumentParser(
        description='个人信息系统自动化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
命令列表:
  clean-downloads   清理下载文件夹（删除超过30天的文件）
  clean-desktop     整理桌面文件
  daily-summary     生成每日文件操作总结
  backup            备份重要文件
  config            显示/修改配置

示例:
  # 预览下载文件夹清理（不实际删除）
  python automation_scripts.py clean-downloads

  # 实际执行清理
  python automation_scripts.py clean-downloads --execute

  # 整理桌面
  python automation_scripts.py clean-desktop --execute

  # 生成每日总结
  python automation_scripts.py daily-summary

  # 备份重要文件
  python automation_scripts.py backup --execute

建议将此脚本加入定时任务:
  Windows: 任务计划程序
  macOS/Linux: cron
        """
    )

    parser.add_argument('command',
                       choices=['clean-downloads', 'clean-desktop', 'daily-summary', 'backup', 'config'],
                       help='要执行的命令')
    parser.add_argument('--execute', action='store_true',
                       help='实际执行操作（默认只预览）')
    parser.add_argument('--config-key', help='配置键（用于config命令）')
    parser.add_argument('--config-value', help='配置值（用于config命令）')

    args = parser.parse_args()

    toolkit = AutomationToolkit()

    if args.command == 'clean-downloads':
        toolkit.auto_clean_downloads(dry_run=not args.execute)

    elif args.command == 'clean-desktop':
        toolkit.auto_clean_desktop(dry_run=not args.execute)

    elif args.command == 'daily-summary':
        toolkit.generate_daily_summary()

    elif args.command == 'backup':
        toolkit.auto_backup(dry_run=not args.execute)

    elif args.command == 'config':
        if args.config_key and args.config_value:
            toolkit.config[args.config_key] = args.config_value
            toolkit.save_config()
            print(f"✅ 配置已更新: {args.config_key} = {args.config_value}")
        else:
            print("当前配置:")
            print(json.dumps(toolkit.config, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
