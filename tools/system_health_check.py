#!/usr/bin/env python3
"""
个人信息系统健康检查工具

功能：
1. 检测本地文件系统状态
2. 生成健康报告
3. 给出优化建议

使用方法：
python system_health_check.py
"""

import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json


class SystemHealthChecker:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.home()
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'score': 0,
            'checks': {},
            'warnings': [],
            'recommendations': []
        }

    def check_downloads_folder(self):
        """检查下载文件夹"""
        downloads = self.base_dir / 'Downloads'
        if not downloads.exists():
            return

        files = list(downloads.glob('*'))
        file_count = len([f for f in files if f.is_file()])

        # 检查最近修改时间
        recent_files = sum(1 for f in files
                          if f.is_file() and
                          (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days < 7)

        old_files = sum(1 for f in files
                       if f.is_file() and
                       (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days > 30)

        self.report['checks']['downloads'] = {
            'total_files': file_count,
            'recent_files': recent_files,
            'old_files': old_files,
            'status': 'good' if file_count < 50 else 'warning' if file_count < 100 else 'critical'
        }

        if file_count > 100:
            self.report['warnings'].append(
                f"⚠️  下载文件夹有{file_count}个文件，建议清理（目标<50个）"
            )
            self.report['recommendations'].append(
                "清理下载文件夹：删除超过30天未使用的文件"
            )

        if old_files > 20:
            self.report['warnings'].append(
                f"⚠️  有{old_files}个文件超过30天未使用"
            )

    def check_desktop(self):
        """检查桌面"""
        desktop = self.base_dir / 'Desktop'
        if not desktop.exists():
            return

        files = list(desktop.glob('*'))
        file_count = len(files)

        self.report['checks']['desktop'] = {
            'total_items': file_count,
            'status': 'good' if file_count < 10 else 'warning' if file_count < 30 else 'critical'
        }

        if file_count > 30:
            self.report['warnings'].append(
                f"⚠️  桌面有{file_count}个项目，建议清理（目标<10个）"
            )
            self.report['recommendations'].append(
                "清理桌面：只保留常用的快捷方式，其他文件归档"
            )
        elif file_count == 0:
            self.report['checks']['desktop']['status'] = 'excellent'
            print("✨ 完美！桌面保持整洁")

    def analyze_file_structure(self, target_dir):
        """分析文件结构"""
        if not target_dir.exists():
            return None

        analysis = {
            'total_files': 0,
            'total_size': 0,
            'file_types': Counter(),
            'duplicates_possibility': 0,
            'unnamed_files': 0,
            'large_files': []
        }

        size_map = defaultdict(list)  # 用于检测可能的重复

        for file_path in target_dir.rglob('*'):
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    analysis['total_files'] += 1
                    analysis['total_size'] += stat.st_size

                    # 文件类型
                    ext = file_path.suffix.lower()
                    analysis['file_types'][ext if ext else 'no_extension'] += 1

                    # 检测未命名文件（如IMG_1234.jpg）
                    if file_path.stem.startswith(('IMG_', 'DSC_', 'Screenshot', '屏幕截图', '未命名')):
                        analysis['unnamed_files'] += 1

                    # 记录文件大小（用于检测重复）
                    size_map[stat.st_size].append(file_path)

                    # 大文件
                    if stat.st_size > 100 * 1024 * 1024:  # >100MB
                        analysis['large_files'].append({
                            'path': str(file_path),
                            'size': stat.st_size
                        })

                except (PermissionError, OSError):
                    pass

        # 估算可能的重复文件
        analysis['duplicates_possibility'] = sum(
            len(files) - 1 for files in size_map.values() if len(files) > 1
        )

        return analysis

    def check_photo_organization(self):
        """检查照片组织情况"""
        photo_dirs = [
            self.base_dir / 'Pictures',
            self.base_dir / '图片',
            self.base_dir / 'Photos',
            self.base_dir / '照片'
        ]

        for photo_dir in photo_dirs:
            if photo_dir.exists():
                analysis = self.analyze_file_structure(photo_dir)
                if analysis:
                    self.report['checks']['photos'] = {
                        'directory': str(photo_dir),
                        'total_files': analysis['total_files'],
                        'total_size_mb': analysis['total_size'] / (1024 * 1024),
                        'unnamed_files': analysis['unnamed_files'],
                        'possible_duplicates': analysis['duplicates_possibility'],
                        'file_types': dict(analysis['file_types'].most_common(5))
                    }

                    # 评估状态
                    if analysis['unnamed_files'] > analysis['total_files'] * 0.5:
                        self.report['warnings'].append(
                            f"⚠️  {analysis['unnamed_files']}个照片未重命名（占{analysis['unnamed_files']/analysis['total_files']*100:.1f}%）"
                        )
                        self.report['recommendations'].append(
                            "使用file_renamer.py批量重命名照片"
                        )

                    if analysis['duplicates_possibility'] > 100:
                        self.report['warnings'].append(
                            f"⚠️  可能有{analysis['duplicates_possibility']}个重复文件"
                        )
                        self.report['recommendations'].append(
                            "使用duplicate_finder.py查找并删除重复照片"
                        )

                break

    def check_file_naming_compliance(self, target_dir):
        """检查文件命名是否符合规范"""
        if not target_dir.exists():
            return None

        # 规范格式：YYYY-MM-DD_来源_类型_主题_编号
        pattern_compliant = 0
        total_files = 0

        for file_path in target_dir.rglob('*'):
            if file_path.is_file():
                total_files += 1
                name = file_path.stem

                # 简单检测：是否以日期开头（YYYY-MM-DD或YYYY-MMDD）
                if len(name) > 10 and name[0:4].isdigit():
                    if name[4] == '-' and name[7] == '-':
                        pattern_compliant += 1

        compliance_rate = (pattern_compliant / total_files * 100) if total_files > 0 else 0

        return {
            'total_files': total_files,
            'compliant_files': pattern_compliant,
            'compliance_rate': compliance_rate
        }

    def check_notion_readiness(self):
        """检查Notion准备情况（基于本地标记文件）"""
        # 这个需要用户自己创建标记文件
        markers = {
            'inbox_created': self.base_dir / '.notion_inbox_ready',
            'daily_created': self.base_dir / '.notion_daily_ready',
            'topics_created': self.base_dir / '.notion_topics_ready',
            'lifehub_created': self.base_dir / '.notion_lifehub_ready'
        }

        readiness = {key: path.exists() for key, path in markers.items()}
        ready_count = sum(readiness.values())

        self.report['checks']['notion_readiness'] = {
            'modules_ready': ready_count,
            'total_modules': len(markers),
            'details': readiness
        }

        if ready_count < len(markers):
            self.report['recommendations'].append(
                f"完成Notion设置：{len(markers) - ready_count}个模块未创建"
            )

    def calculate_health_score(self):
        """计算健康分数（0-100）"""
        score = 100

        # 下载文件夹扣分
        if 'downloads' in self.report['checks']:
            downloads_status = self.report['checks']['downloads']['status']
            if downloads_status == 'critical':
                score -= 20
            elif downloads_status == 'warning':
                score -= 10

        # 桌面扣分
        if 'desktop' in self.report['checks']:
            desktop_status = self.report['checks']['desktop']['status']
            if desktop_status == 'critical':
                score -= 15
            elif desktop_status == 'warning':
                score -= 8
            elif desktop_status == 'excellent':
                score += 5  # 加分奖励

        # 照片组织扣分
        if 'photos' in self.report['checks']:
            photos = self.report['checks']['photos']
            if photos['unnamed_files'] > 1000:
                score -= 15
            elif photos['unnamed_files'] > 500:
                score -= 10

            if photos['possible_duplicates'] > 200:
                score -= 10
            elif photos['possible_duplicates'] > 100:
                score -= 5

        # Notion准备度加分
        if 'notion_readiness' in self.report['checks']:
            ready_modules = self.report['checks']['notion_readiness']['modules_ready']
            score += ready_modules * 5

        self.report['score'] = max(0, min(100, score))

        # 确定整体状态
        if score >= 80:
            self.report['status'] = 'excellent'
        elif score >= 60:
            self.report['status'] = 'good'
        elif score >= 40:
            self.report['status'] = 'warning'
        else:
            self.report['status'] = 'critical'

    def run_all_checks(self):
        """运行所有检查"""
        print("🔍 开始健康检查...\n")

        print("📁 检查下载文件夹...")
        self.check_downloads_folder()

        print("🖥️  检查桌面...")
        self.check_desktop()

        print("📸 检查照片组织...")
        self.check_photo_organization()

        print("📊 计算健康分数...")
        self.calculate_health_score()

        print("\n✅ 检查完成！\n")

    def print_report(self):
        """打印报告"""
        print("=" * 60)
        print("🏥 个人信息系统健康报告")
        print("=" * 60)
        print(f"检查时间: {self.report['timestamp']}")
        print()

        # 健康分数
        score = self.report['score']
        status = self.report['status']

        status_emoji = {
            'excellent': '🌟',
            'good': '✅',
            'warning': '⚠️',
            'critical': '🔴'
        }

        status_text = {
            'excellent': '优秀',
            'good': '良好',
            'warning': '需要改进',
            'critical': '严重问题'
        }

        print(f"总体评分: {score}/100 {status_emoji.get(status, '❓')}")
        print(f"系统状态: {status_text.get(status, '未知')}")
        print()

        # 详细检查结果
        if self.report['checks']:
            print("📋 详细检查结果:")
            print("-" * 60)

            for check_name, check_data in self.report['checks'].items():
                print(f"\n{check_name.upper()}:")
                for key, value in check_data.items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for k, v in value.items():
                            print(f"    {k}: {v}")
                    elif isinstance(value, (int, float)):
                        if isinstance(value, float):
                            print(f"  {key}: {value:.2f}")
                        else:
                            print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")

        # 警告
        if self.report['warnings']:
            print("\n" + "=" * 60)
            print("⚠️  警告:")
            print("-" * 60)
            for i, warning in enumerate(self.report['warnings'], 1):
                print(f"{i}. {warning}")

        # 建议
        if self.report['recommendations']:
            print("\n" + "=" * 60)
            print("💡 建议:")
            print("-" * 60)
            for i, rec in enumerate(self.report['recommendations'], 1):
                print(f"{i}. {rec}")

        print("\n" + "=" * 60)

        # 根据分数给出总体建议
        if score < 40:
            print("\n🚨 紧急行动建议:")
            print("  1. 立即清理下载文件夹和桌面")
            print("  2. 运行文件去重工具")
            print("  3. 批量重命名文件")
            print("  4. 建立Notion基础结构")
        elif score < 60:
            print("\n📌 重点改进建议:")
            print("  1. 完成当前警告项的处理")
            print("  2. 建立每日维护习惯")
            print("  3. 逐步优化文件组织")
        elif score < 80:
            print("\n👍 继续保持，小幅优化:")
            print("  1. 保持当前良好习惯")
            print("  2. 处理剩余警告项")
            print("  3. 探索自动化工具")
        else:
            print("\n🎉 系统运行优秀！")
            print("  1. 继续保持当前习惯")
            print("  2. 可以尝试优化工作流")
            print("  3. 分享经验帮助他人")

        print()

    def export_report(self, output_file):
        """导出报告为JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)
        print(f"📄 报告已导出到: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='个人信息系统健康检查工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础检查
  python system_health_check.py

  # 指定检查目录
  python system_health_check.py --dir /path/to/your/home

  # 导出报告
  python system_health_check.py --export report.json

评分标准:
  80-100: 优秀 🌟
  60-79:  良好 ✅
  40-59:  需要改进 ⚠️
  0-39:   严重问题 🔴

检查项目:
  - 下载文件夹状态
  - 桌面整洁度
  - 照片组织情况
  - 文件命名规范
  - 可能的重复文件
        """
    )

    parser.add_argument('--dir', help='要检查的主目录（默认为用户主目录）')
    parser.add_argument('--export', help='导出报告为JSON文件')

    args = parser.parse_args()

    # 运行检查
    checker = SystemHealthChecker(base_dir=args.dir)
    checker.run_all_checks()
    checker.print_report()

    # 导出报告
    if args.export:
        checker.export_report(args.export)

    # 返回状态码（可用于自动化脚本）
    return 0 if checker.report['score'] >= 60 else 1


if __name__ == '__main__':
    exit(main())
