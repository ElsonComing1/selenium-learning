@echo off
chcp 65001 >nul
title 自动化测试执行脚本

echo ========================================
echo   开始执行 Selenium 自动化测试
echo ========================================
echo.

:: 切换到脚本所在目录（day06）
cd /d "%~dp0"

:: 激活虚拟环境（从day06返回两级到根目录找venv）
echo [1/4] 正在激活 Python 虚拟环境...
call ..\..\venv\Scripts\activate.bat

:: 检查激活是否成功（注意：这里用 if 判断，注释放在外面）
if errorlevel 1 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)

:: 创建报告目录
echo [2/4] 检查报告目录...
if not exist "report" mkdir "report"

:: 执行测试（当前在day06，直接跑test_cases）
echo [3/4] 正在执行测试用例...
set "timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "timestamp=%timestamp: =0%"

pytest test_cases\ -v --html=report\test_report_%timestamp%.html --self-contained-html

echo.
echo [4/4] 测试执行完毕！

:: 打开报告目录
start "" "report"
echo.

:: 暂停查看结果
pause