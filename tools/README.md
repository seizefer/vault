# 个人信息管理辅助工具包

本工具包包含多个Python脚本，用于辅助个人信息系统的搭建和维护。

## 🛠️ 工具列表

### 1. bookmark_analyzer.py - 浏览器书签分析工具

**功能：**
- 解析Edge/Chrome导出的HTML书签文件
- 统计书签数量、分类、域名分布
- 自动分类书签（技术/视频/社交/学习等）
- 导出为CSV/JSON，方便导入Notion
- 检测重复书签

**使用方法：**

```bash
# 1. 导出浏览器书签
# Edge: 设置 → 收藏夹 → 导出收藏夹 → 保存为 bookmarks.html
# Chrome: 书签管理器 → ··· → 导出书签 → 保存为 bookmarks.html

# 2. 分析书签（预览）
python bookmark_analyzer.py bookmarks.html

# 3. 导出为CSV（可导入Excel/Notion）
python bookmark_analyzer.py bookmarks.html --csv output.csv

# 4. 导出为JSON
python bookmark_analyzer.py bookmarks.html --json output.json
```

**输出示例：**
```
📊 书签统计分析
================================================================
总书签数: 1234

📁 按文件夹分布:
  技术/前端: 156
  学习资料: 89
  工具: 45
  ...

🏷️  按类别分布:
  技术: 456
  视频: 234
  社交: 123
  ...
```

---

### 2. file_renamer.py - 批量文件重命名工具

**功能：**
- 根据EXIF信息（拍摄日期）重命名照片/视频
- 支持自定义命名模板
- 自动检测文件来源（手机/相机/截图/下载）
- 预览模式（先查看效果，再执行）
- 支持递归处理子文件夹

**使用方法：**

```bash
# 1. 预览重命名（不实际修改文件）
python file_renamer.py /path/to/photos

# 2. 使用默认模板执行重命名
python file_renamer.py /path/to/photos --execute

# 3. 自定义命名模板
python file_renamer.py /path/to/photos \
  --pattern "{year}-{month}-{day}_手机_照片_{counter}" \
  --execute

# 4. 自动检测来源（手机/相机/截图）
python file_renamer.py /path/to/photos \
  --pattern "{year}-{month}-{day}_{source}_照片_{counter}" \
  --auto-source \
  --execute

# 5. 只处理特定类型文件
python file_renamer.py /path/to/photos \
  --ext .jpg .jpeg \
  --execute

# 6. 递归处理子文件夹
python file_renamer.py /path/to/photos \
  --recursive \
  --execute
```

**命名模板占位符：**
- `{year}` - 年份 (2025)
- `{month}` - 月份 (01-12)
- `{day}` - 日期 (01-31)
- `{hour}` - 小时
- `{minute}` - 分钟
- `{second}` - 秒
- `{counter}` - 序号 (001, 002, ...)
- `{source}` - 来源（手机/相机/截图/下载）
- `{original}` - 原始文件名
- `{ext}` - 扩展名

**重命名前后对比：**
```
重命名前:
  IMG_1234.jpg
  IMG_1235.jpg
  Screenshot_20250115.png

重命名后:
  2025-01-15_手机_照片_001.jpg
  2025-01-15_手机_照片_002.jpg
  2025-01-15_截图_图片_003.png
```

---

### 3. duplicate_finder.py - 文件去重工具

**功能：**
- 基于文件内容（MD5哈希）查找重复文件
- 支持多种保留策略（最新/最旧/最短路径）
- 安全操作：预览、删除、移动到trash
- 大文件优化（快速哈希）
- 统计重复文件占用空间

**使用方法：**

```bash
# 1. 预览重复文件
python duplicate_finder.py /path/to/folder

# 2. 查找并删除重复文件（保留最新的）
python duplicate_finder.py /path/to/folder \
  --strategy newest \
  --delete

# 3. 移动重复文件到trash文件夹（更安全）
python duplicate_finder.py /path/to/folder \
  --move \
  --trash ./duplicates_trash

# 4. 只查找图片文件的重复
python duplicate_finder.py /path/to/folder \
  --ext .jpg .png .gif

# 5. 忽略小文件（如小于1MB）
python duplicate_finder.py /path/to/folder \
  --min-size 1048576 \
  --delete

# 6. 使用最短路径策略（保留在更上层目录的文件）
python duplicate_finder.py /path/to/folder \
  --strategy shortest_path \
  --move
```

**保留策略说明：**
- `newest` - 保留最新修改的文件
- `oldest` - 保留最旧的文件
- `shortest_path` - 保留路径最短的文件（通常在上层目录）

**输出示例：**
```
📊 统计:
   重复文件数: 156
   浪费空间: 2.34 GB

📦 第 1/23 组重复:
   文件数: 3
   文件大小: 5.67 MB

   - /path/to/folder1/photo.jpg
     修改时间: 2025-01-15 10:30:45
   - /path/to/folder2/photo_copy.jpg
     修改时间: 2025-01-10 08:20:15
   - /path/to/backup/photo.jpg
     修改时间: 2025-01-05 14:15:30

   ✅ 保留: photo.jpg (最新)
   ❌ 删除: 2 个文件
```

---

## 📦 安装依赖

```bash
# 安装Python（如果还没有）
# Windows: 下载 https://www.python.org/downloads/
# macOS: brew install python3
# Linux: sudo apt install python3 python3-pip

# 安装依赖包
pip install Pillow
```

---

## 🚀 快速开始

### 场景1：清理浏览器书签并导入Notion

```bash
# 1. 导出Edge书签为bookmarks.html
# 2. 分析并导出CSV
python bookmark_analyzer.py bookmarks.html --csv bookmarks.csv

# 3. 在Notion中导入CSV
#    - 打开Notion
#    - 在Topics/Resources页面
#    - 点击"···" → Import → CSV/TSV
#    - 选择bookmarks.csv
#    - 映射字段：title → Name, url → URL, category → Tags
```

### 场景2：整理手机照片

```bash
# 1. 把手机照片导出到电脑（如 /Users/你的名字/照片整理）

# 2. 预览重命名效果
python file_renamer.py /Users/你的名字/照片整理

# 3. 确认后执行重命名
python file_renamer.py /Users/你的名字/照片整理 \
  --pattern "{year}-{month}-{day}_手机_照片_{counter}" \
  --execute

# 4. 查找并删除重复照片
python duplicate_finder.py /Users/你的名字/照片整理 \
  --strategy newest \
  --delete
```

### 场景3：清理下载文件夹

```bash
# 1. 查找重复文件
python duplicate_finder.py ~/Downloads

# 2. 移动重复文件到trash（安全，可恢复）
python duplicate_finder.py ~/Downloads \
  --move \
  --trash ~/Downloads/_trash

# 3. 检查trash文件夹，确认后手动删除
```

---

## ⚠️ 安全建议

1. **总是先预览**
   - 所有工具默认都是预览模式
   - 先运行一次看效果，再用 `--execute` 或 `--delete` 执行

2. **备份重要文件**
   - 在执行批量操作前，先备份重要文件到云盘或移动硬盘
   - 特别是使用 `--delete` 参数时

3. **使用移动代替删除**
   - 优先使用 `--move` 而不是 `--delete`
   - 移动到trash文件夹，确认无误后再手动删除

4. **分批处理**
   - 不要一次性处理太多文件
   - 建议每次处理<1000个文件，分多次执行

5. **检查结果**
   - 执行后检查文件是否正确
   - 如有问题，从备份恢复

---

## 🐛 故障排除

### 问题1：运行脚本提示"找不到模块"

```bash
# 解决：安装缺失的依赖
pip install Pillow
```

### 问题2：中文文件名显示乱码

```bash
# Windows用户：在命令提示符中执行
chcp 65001

# 或使用PowerShell（推荐）
```

### 问题3：没有权限访问某些文件

```bash
# Windows: 以管理员身份运行命令提示符
# macOS/Linux: 使用 sudo（谨慎使用）
sudo python script.py ...
```

### 问题4：EXIF信息读取失败

- 部分照片可能没有EXIF信息（如截图、编辑过的照片）
- 工具会自动使用文件修改时间作为备选

---

## 📝 使用建议

1. **循序渐进**
   - 先用一个小文件夹测试
   - 熟悉后再处理大量文件

2. **结合手动整理**
   - 工具可以处理90%的机械工作
   - 剩余10%需要人工判断

3. **定期维护**
   - 每月运行一次去重工具
   - 每季度整理一次文件命名

4. **自定义模板**
   - 根据自己的习惯调整命名模板
   - 记录常用的命令，创建脚本快捷方式

---

## 💡 进阶用法

### 创建批处理脚本（Windows）

创建 `organize_photos.bat`:
```batch
@echo off
echo 正在整理照片...
python file_renamer.py "C:\Users\你的名字\照片" --execute
python duplicate_finder.py "C:\Users\你的名字\照片" --move --trash "C:\Users\你的名字\照片\_trash"
echo 完成！
pause
```

### 创建Shell脚本（macOS/Linux）

创建 `organize_photos.sh`:
```bash
#!/bin/bash
echo "正在整理照片..."
python3 file_renamer.py ~/照片 --execute
python3 duplicate_finder.py ~/照片 --move --trash ~/照片/_trash
echo "完成！"
```

---

## 📞 获取帮助

所有工具都支持 `--help` 参数查看详细说明：

```bash
python bookmark_analyzer.py --help
python file_renamer.py --help
python duplicate_finder.py --help
```

---

## 📄 许可证

这些工具为个人信息管理系统的配套工具，仅供学习和个人使用。
