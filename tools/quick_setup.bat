@echo off
REM 个人信息系统 - 一键快速设置脚本 (Windows)
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo =============================================
echo 个人信息系统 - 一键快速设置
echo =============================================
echo.

REM 检查Python
echo [1/6] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python
    echo.
    echo 请先安装Python3: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

python --version
echo ✅ Python已安装
echo.

REM 安装依赖
echo [2/6] 安装Python依赖...
python -m pip install Pillow --quiet
echo ✅ 依赖安装完成
echo.

REM 创建目录结构
echo [3/6] 创建目录结构...
set "INFO_DIR=%USERPROFILE%\PersonalInfoSystem"
set "TOOL_DIR=%INFO_DIR%\_工具"

if not exist "%INFO_DIR%" mkdir "%INFO_DIR%"
if not exist "%INFO_DIR%\照片整理" mkdir "%INFO_DIR%\照片整理"
if not exist "%INFO_DIR%\文档整理" mkdir "%INFO_DIR%\文档整理"
if not exist "%INFO_DIR%\下载归档" mkdir "%INFO_DIR%\下载归档"
if not exist "%INFO_DIR%\备份" mkdir "%INFO_DIR%\备份"
if not exist "%TOOL_DIR%" mkdir "%TOOL_DIR%"

echo ✅ 目录已创建: %INFO_DIR%
echo.

REM 复制工具脚本
echo [4/6] 复制工具脚本...
set "SCRIPT_DIR=%~dp0"

if exist "%SCRIPT_DIR%bookmark_analyzer.py" (
    copy /Y "%SCRIPT_DIR%bookmark_analyzer.py" "%TOOL_DIR%\" >nul
    echo ✅ 已复制: bookmark_analyzer.py
)

if exist "%SCRIPT_DIR%file_renamer.py" (
    copy /Y "%SCRIPT_DIR%file_renamer.py" "%TOOL_DIR%\" >nul
    echo ✅ 已复制: file_renamer.py
)

if exist "%SCRIPT_DIR%duplicate_finder.py" (
    copy /Y "%SCRIPT_DIR%duplicate_finder.py" "%TOOL_DIR%\" >nul
    echo ✅ 已复制: duplicate_finder.py
)

if exist "%SCRIPT_DIR%system_health_check.py" (
    copy /Y "%SCRIPT_DIR%system_health_check.py" "%TOOL_DIR%\" >nul
    echo ✅ 已复制: system_health_check.py
)

if exist "%SCRIPT_DIR%automation_scripts.py" (
    copy /Y "%SCRIPT_DIR%automation_scripts.py" "%TOOL_DIR%\" >nul
    echo ✅ 已复制: automation_scripts.py
)

echo.

REM 创建快捷批处理文件
echo [5/6] 创建快捷命令...

echo @echo off > "%TOOL_DIR%\pis-health.bat"
echo python "%TOOL_DIR%\system_health_check.py" %%* >> "%TOOL_DIR%\pis-health.bat"

echo @echo off > "%TOOL_DIR%\pis-rename.bat"
echo python "%TOOL_DIR%\file_renamer.py" %%* >> "%TOOL_DIR%\pis-rename.bat"

echo @echo off > "%TOOL_DIR%\pis-dedup.bat"
echo python "%TOOL_DIR%\duplicate_finder.py" %%* >> "%TOOL_DIR%\pis-dedup.bat"

echo @echo off > "%TOOL_DIR%\pis-bookmark.bat"
echo python "%TOOL_DIR%\bookmark_analyzer.py" %%* >> "%TOOL_DIR%\pis-bookmark.bat"

echo @echo off > "%TOOL_DIR%\pis-auto.bat"
echo python "%TOOL_DIR%\automation_scripts.py" %%* >> "%TOOL_DIR%\pis-auto.bat"

REM 添加到PATH（需要用户手动确认）
echo ✅ 快捷命令已创建
echo.
echo 💡 要在任何位置使用命令，请手动添加到PATH:
echo    %TOOL_DIR%
echo.

REM 生成使用指南
echo [6/6] 生成使用指南...

set "GUIDE_FILE=%INFO_DIR%\快速开始.txt"

(
echo ========================================
echo 个人信息系统 - 快速开始指南
echo ========================================
echo.
echo 🎯 第1天任务清单（2小时）
echo.
echo 1. 访问 Notion.so 注册账号
echo    → https://www.notion.so
echo.
echo 2. 创建4个顶级页面：
echo    ✅ 📥 INBOX（统一入口）
echo    ✅ 📅 DAILY（日常记录）
echo    ✅ 🏷️ TOPICS（知识库）
echo    ✅ 🎯 LIFE HUB（执行中心）
echo.
echo 3. 清理浏览器标签页
echo    → 目标：关闭70%%的标签页
echo    → 有用的存到Notion Inbox
echo.
echo 4. 填写第一个Daily Page
echo    → 记录今天做了什么
echo.
echo 5. 设置手机提醒
echo    → 早9:00: 查看Notion
echo    → 晚10:00: 填写Daily
echo.
echo ========================================
echo 🛠️ 可用工具
echo ========================================
echo.
echo 系统健康检查：
echo   %TOOL_DIR%\pis-health.bat
echo.
echo 批量重命名文件：
echo   %TOOL_DIR%\pis-rename.bat C:\path\to\photos --execute
echo.
echo 查找重复文件：
echo   %TOOL_DIR%\pis-dedup.bat C:\path\to\folder --delete
echo.
echo 分析浏览器书签：
echo   %TOOL_DIR%\pis-bookmark.bat bookmarks.html --csv output.csv
echo.
echo 自动化维护：
echo   %TOOL_DIR%\pis-auto.bat clean-downloads --execute
echo.
echo 详细使用说明：
echo   添加 --help 参数查看
echo.
echo ========================================
echo 📚 文档位置
echo ========================================
echo.
echo 完整指南：
echo   %INFO_DIR%\个人信息系统完整指南.md
echo.
echo 快速参考：
echo   %INFO_DIR%\docs\快速参考手册.md
echo.
echo 案例研究：
echo   %INFO_DIR%\docs\案例研究.md
echo.
echo ========================================
echo 💡 提示
echo ========================================
echo.
echo 1. 不追求完美，够用就好
echo 2. 每天20分钟维护系统
echo 3. 从小处开始，积少成多
echo 4. 使用工具自动化
echo 5. 坚持30天形成习惯
echo.
echo 现在就开始吧！Good luck! 🚀
) > "%GUIDE_FILE%"

echo ✅ 使用指南已生成
echo.

REM 运行健康检查
echo.
echo ========================================
echo 运行系统健康检查
echo ========================================
echo.

python "%TOOL_DIR%\system_health_check.py"

REM 完成
echo.
echo ========================================
echo 设置完成！
echo ========================================
echo.
echo ✅ 个人信息系统已准备就绪
echo.
echo 📍 安装位置: %INFO_DIR%
echo.
echo 下一步：
echo   1. 打开 快速开始.txt 查看指南
echo   2. 访问 Notion.so 创建账号
echo   3. 执行第1天任务清单
echo.
echo 💡 提示: 可以将工具目录添加到PATH环境变量
echo    %TOOL_DIR%
echo.
echo 祝你成功！🎉
echo.

pause
