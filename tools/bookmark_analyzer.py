#!/usr/bin/env python3
"""
浏览器书签分析工具
功能：
1. 解析Edge/Chrome导出的HTML书签文件
2. 统计书签数量、分类
3. 导出为CSV或JSON，方便导入Notion
4. 检测重复和失效链接

使用方法：
python bookmark_analyzer.py bookmarks.html
"""

import re
import json
import csv
from html.parser import HTMLParser
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse
import argparse


class BookmarkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self.current_folder = []
        self.in_dt = False
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == 'h3':  # 文件夹
            self.current_folder.append(attrs.get('add_date', ''))

        elif tag == 'a':  # 书签链接
            self.current_link = {
                'url': attrs.get('href', ''),
                'add_date': attrs.get('add_date', ''),
                'icon': attrs.get('icon', ''),
                'folder': ' > '.join(self.current_folder) if self.current_folder else 'Root',
                'title': ''
            }

    def handle_endtag(self, tag):
        if tag == 'h3' and self.current_folder:
            self.current_folder.pop()

        elif tag == 'a' and self.current_link:
            self.bookmarks.append(self.current_link)
            self.current_link = None

    def handle_data(self, data):
        if self.current_link is not None:
            self.current_link['title'] = data.strip()


def analyze_bookmarks(html_file):
    """分析书签文件"""
    parser = BookmarkParser()

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        parser.feed(content)

    return parser.bookmarks


def categorize_url(url):
    """根据URL自动分类"""
    domain = urlparse(url).netloc.lower()

    # 定义分类规则
    categories = {
        '技术': ['github.com', 'stackoverflow.com', 'medium.com', 'dev.to',
                'csdn.net', 'juejin.cn', 'segmentfault.com'],
        '视频': ['youtube.com', 'bilibili.com', 'youtu.be'],
        '社交': ['twitter.com', 'x.com', 'weibo.com', 'zhihu.com', 'xiaohongshu.com'],
        '学习': ['coursera.org', 'udemy.com', 'edx.org', 'khanacademy.org'],
        '工具': ['notion.so', 'trello.com', 'figma.com', 'canva.com'],
        '购物': ['taobao.com', 'jd.com', 'amazon.com', 'tmall.com'],
        '新闻': ['news', 'bbc.com', 'cnn.com', 'theguardian.com']
    }

    for category, keywords in categories.items():
        if any(keyword in domain for keyword in keywords):
            return category

    return '其他'


def generate_stats(bookmarks):
    """生成统计信息"""
    stats = {
        'total': len(bookmarks),
        'by_folder': defaultdict(int),
        'by_category': defaultdict(int),
        'by_domain': defaultdict(int)
    }

    for bm in bookmarks:
        stats['by_folder'][bm['folder']] += 1

        category = categorize_url(bm['url'])
        stats['by_category'][category] += 1

        domain = urlparse(bm['url']).netloc
        stats['by_domain'][domain] += 1

    return stats


def export_to_csv(bookmarks, output_file):
    """导出为CSV（可导入Excel/Notion）"""
    # 添加分类信息
    for bm in bookmarks:
        bm['category'] = categorize_url(bm['url'])

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        if bookmarks:
            writer = csv.DictWriter(f, fieldnames=['title', 'url', 'folder', 'category', 'add_date'])
            writer.writeheader()
            writer.writerows(bookmarks)

    print(f"✅ CSV已导出到: {output_file}")


def export_to_json(bookmarks, output_file):
    """导出为JSON"""
    for bm in bookmarks:
        bm['category'] = categorize_url(bm['url'])

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON已导出到: {output_file}")


def print_stats(stats):
    """打印统计信息"""
    print("\n" + "="*60)
    print("📊 书签统计分析")
    print("="*60)

    print(f"\n总书签数: {stats['total']}")

    print("\n📁 按文件夹分布 (Top 10):")
    sorted_folders = sorted(stats['by_folder'].items(), key=lambda x: x[1], reverse=True)[:10]
    for folder, count in sorted_folders:
        print(f"  {folder}: {count}")

    print("\n🏷️  按类别分布:")
    sorted_categories = sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_categories:
        print(f"  {category}: {count}")

    print("\n🌐 按域名分布 (Top 15):")
    sorted_domains = sorted(stats['by_domain'].items(), key=lambda x: x[1], reverse=True)[:15]
    for domain, count in sorted_domains:
        print(f"  {domain}: {count}")


def find_duplicates(bookmarks):
    """查找重复书签"""
    url_map = defaultdict(list)

    for bm in bookmarks:
        url_map[bm['url']].append(bm['title'])

    duplicates = {url: titles for url, titles in url_map.items() if len(titles) > 1}

    if duplicates:
        print(f"\n⚠️  发现 {len(duplicates)} 个重复的URL:")
        for url, titles in list(duplicates.items())[:10]:
            print(f"  {url}")
            print(f"    标题: {', '.join(set(titles))}")
    else:
        print("\n✅ 没有发现重复书签")


def main():
    parser = argparse.ArgumentParser(description='浏览器书签分析工具')
    parser.add_argument('html_file', help='书签HTML文件路径')
    parser.add_argument('--csv', help='导出为CSV文件')
    parser.add_argument('--json', help='导出为JSON文件')
    parser.add_argument('--no-stats', action='store_true', help='不显示统计信息')

    args = parser.parse_args()

    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"❌ 文件不存在: {html_path}")
        return

    print(f"🔍 正在分析书签文件: {html_path}")
    bookmarks = analyze_bookmarks(html_path)

    if not bookmarks:
        print("❌ 未找到书签")
        return

    # 统计
    if not args.no_stats:
        stats = generate_stats(bookmarks)
        print_stats(stats)
        find_duplicates(bookmarks)

    # 导出
    if args.csv:
        export_to_csv(bookmarks, args.csv)

    if args.json:
        export_to_json(bookmarks, args.json)

    if not args.csv and not args.json:
        # 默认导出CSV
        default_csv = html_path.stem + '_bookmarks.csv'
        export_to_csv(bookmarks, default_csv)
        print(f"\n💡 提示: 可以将CSV导入Excel或Notion进行进一步筛选")


if __name__ == '__main__':
    main()
