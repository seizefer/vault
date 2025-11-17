#!/bin/bash
# 个人信息系统 - 一键快速设置脚本
# 适用于 macOS/Linux

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo -e "${BLUE}=================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# 检查Python环境
check_python() {
    print_header "检查Python环境"

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python已安装: $PYTHON_VERSION"
        return 0
    else
        print_error "未找到Python3"
        print_info "请先安装Python3: https://www.python.org/downloads/"
        return 1
    fi
}

# 安装Python依赖
install_dependencies() {
    print_header "安装Python依赖"

    print_info "安装Pillow（用于图片处理）..."
    pip3 install Pillow --quiet

    print_success "依赖安装完成"
}

# 创建目录结构
create_directories() {
    print_header "创建目录结构"

    # 主目录
    HOME_DIR="$HOME"
    INFO_SYSTEM_DIR="$HOME/PersonalInfoSystem"

    # 创建主要文件夹
    mkdir -p "$INFO_SYSTEM_DIR/照片整理"
    mkdir -p "$INFO_SYSTEM_DIR/文档整理"
    mkdir -p "$INFO_SYSTEM_DIR/下载归档"
    mkdir -p "$INFO_SYSTEM_DIR/备份"
    mkdir -p "$INFO_SYSTEM_DIR/_工具"

    print_success "目录结构已创建: $INFO_SYSTEM_DIR"
}

# 复制工具脚本
copy_tools() {
    print_header "复制工具脚本"

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    INFO_SYSTEM_DIR="$HOME/PersonalInfoSystem"
    TOOL_DIR="$INFO_SYSTEM_DIR/_工具"

    # 复制Python脚本
    if [ -f "$SCRIPT_DIR/bookmark_analyzer.py" ]; then
        cp "$SCRIPT_DIR/bookmark_analyzer.py" "$TOOL_DIR/"
        print_success "已复制: bookmark_analyzer.py"
    fi

    if [ -f "$SCRIPT_DIR/file_renamer.py" ]; then
        cp "$SCRIPT_DIR/file_renamer.py" "$TOOL_DIR/"
        print_success "已复制: file_renamer.py"
    fi

    if [ -f "$SCRIPT_DIR/duplicate_finder.py" ]; then
        cp "$SCRIPT_DIR/duplicate_finder.py" "$TOOL_DIR/"
        print_success "已复制: duplicate_finder.py"
    fi

    if [ -f "$SCRIPT_DIR/system_health_check.py" ]; then
        cp "$SCRIPT_DIR/system_health_check.py" "$TOOL_DIR/"
        print_success "已复制: system_health_check.py"
    fi

    if [ -f "$SCRIPT_DIR/automation_scripts.py" ]; then
        cp "$SCRIPT_DIR/automation_scripts.py" "$TOOL_DIR/"
        print_success "已复制: automation_scripts.py"
    fi

    # 设置可执行权限
    chmod +x "$TOOL_DIR"/*.py

    print_success "工具脚本已准备就绪"
}

# 创建快捷命令
create_aliases() {
    print_header "创建快捷命令"

    TOOL_DIR="$HOME/PersonalInfoSystem/_工具"
    SHELL_RC=""

    # 检测shell类型
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    fi

    if [ -z "$SHELL_RC" ]; then
        print_warning "无法检测shell类型，跳过创建快捷命令"
        return 0
    fi

    # 添加快捷命令
    echo "" >> "$SHELL_RC"
    echo "# 个人信息系统快捷命令" >> "$SHELL_RC"
    echo "alias pis-health='python3 $TOOL_DIR/system_health_check.py'" >> "$SHELL_RC"
    echo "alias pis-rename='python3 $TOOL_DIR/file_renamer.py'" >> "$SHELL_RC"
    echo "alias pis-dedup='python3 $TOOL_DIR/duplicate_finder.py'" >> "$SHELL_RC"
    echo "alias pis-bookmark='python3 $TOOL_DIR/bookmark_analyzer.py'" >> "$SHELL_RC"
    echo "alias pis-auto='python3 $TOOL_DIR/automation_scripts.py'" >> "$SHELL_RC"

    print_success "快捷命令已添加到 $SHELL_RC"
    print_info "重新加载shell后可使用: source $SHELL_RC"
}

# 生成使用指南
create_quick_guide() {
    print_header "生成使用指南"

    INFO_SYSTEM_DIR="$HOME/PersonalInfoSystem"
    GUIDE_FILE="$INFO_SYSTEM_DIR/快速开始.txt"

    cat > "$GUIDE_FILE" << 'EOF'
========================================
个人信息系统 - 快速开始指南
========================================

🎯 第1天任务清单（2小时）

1. 访问 Notion.so 注册账号
   → https://www.notion.so

2. 创建4个顶级页面：
   ✅ 📥 INBOX（统一入口）
   ✅ 📅 DAILY（日常记录）
   ✅ 🏷️ TOPICS（知识库）
   ✅ 🎯 LIFE HUB（执行中心）

3. 清理浏览器标签页
   → 目标：关闭70%的标签页
   → 有用的存到Notion Inbox

4. 填写第一个Daily Page
   → 记录今天做了什么

5. 设置手机提醒
   → 早9:00: 查看Notion
   → 晚10:00: 填写Daily

========================================
🛠️ 可用工具
========================================

系统健康检查：
  pis-health

批量重命名文件：
  pis-rename /path/to/photos --execute

查找重复文件：
  pis-dedup /path/to/folder --delete

分析浏览器书签：
  pis-bookmark bookmarks.html --csv output.csv

自动化维护：
  pis-auto clean-downloads --execute

详细使用说明：
  添加 --help 参数查看

========================================
📚 文档位置
========================================

完整指南：
  ~/PersonalInfoSystem/个人信息系统完整指南.md

流程图：
  ~/PersonalInfoSystem/docs/流程图与架构.md

模板：
  ~/PersonalInfoSystem/templates/

案例研究：
  ~/PersonalInfoSystem/docs/案例研究.md

========================================
💡 提示
========================================

1. 不追求完美，够用就好
2. 每天20分钟维护系统
3. 从小处开始，积少成多
4. 使用工具自动化
5. 坚持30天形成习惯

现在就开始吧！Good luck! 🚀
EOF

    print_success "使用指南已生成: $GUIDE_FILE"
}

# 运行健康检查
run_health_check() {
    print_header "运行系统健康检查"

    TOOL_DIR="$HOME/PersonalInfoSystem/_工具"

    if [ -f "$TOOL_DIR/system_health_check.py" ]; then
        python3 "$TOOL_DIR/system_health_check.py"
    else
        print_warning "健康检查脚本未找到"
    fi
}

# 主函数
main() {
    clear

    cat << "EOF"
 _____ _____ _____                  _____      __
|  _  |     |   __|___ ___ ___ ___ |     |___ |  |_ ___
|   __|-   -|__   | . |  _|_ -|_ -| |-   | .'|   | -_|
|__|  |_____|_____|_  |_| |___|___| |_|_|_|__,|_|_|___|
                  |___|

个人信息系统 - 一键快速设置
EOF

    echo ""
    print_info "开始设置..."
    echo ""

    # 执行设置步骤
    if ! check_python; then
        exit 1
    fi

    echo ""
    install_dependencies

    echo ""
    create_directories

    echo ""
    copy_tools

    echo ""
    create_aliases

    echo ""
    create_quick_guide

    echo ""
    run_health_check

    # 完成
    echo ""
    print_header "设置完成！"
    echo ""
    print_success "个人信息系统已准备就绪"
    echo ""
    print_info "下一步："
    echo "  1. 打开 ~/PersonalInfoSystem/快速开始.txt 查看指南"
    echo "  2. 访问 Notion.so 创建账号"
    echo "  3. 执行第1天任务清单"
    echo ""
    print_info "重新加载shell后可使用快捷命令:"

    if [ -n "$ZSH_VERSION" ]; then
        echo "  source ~/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        echo "  source ~/.bashrc"
    fi

    echo ""
    print_info "祝你成功！🎉"
    echo ""
}

# 运行主函数
main
