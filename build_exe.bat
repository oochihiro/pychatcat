@echo off
chcp 65001 >nul
echo ========================================
echo 正在打包 Python 学习助手为 EXE...
echo ========================================
echo.

REM 清理旧的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo 开始打包...
python -m PyInstaller ^
    --name=pychatcat ^
    --onefile ^
    --noconsole ^
    --hidden-import=main ^
    --hidden-import=config.backend_config ^
    --hidden-import=integrations.cloud_integration ^
    --hidden-import=integrations.sqlite_integration ^
    --hidden-import=core.user_identity ^
    --hidden-import=core.sqlite_analytics ^
    --hidden-import=ui.pixel_code_editor ^
    --hidden-import=ui.pixel_console ^
    --hidden-import=ui.pixel_ai_assistant ^
    --hidden-import=ui.debugger_panel ^
    --hidden-import=core.file_manager ^
    --hidden-import=core.code_executor ^
    --hidden-import=core.deepseek_client ^
    --hidden-import=cat_icon ^
    --add-data="config;config" ^
    run_app.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ 打包成功！
    echo ========================================
    echo EXE 文件位置: dist\pychatcat.exe
    echo.
    echo 请测试运行 dist\pychatcat.exe
) else (
    echo.
    echo ========================================
    echo ❌ 打包失败！
    echo ========================================
    echo 请检查错误信息
)

pause




