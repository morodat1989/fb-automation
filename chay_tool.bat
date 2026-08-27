@echo off
chcp 65001 > nul

:: Ép đường dẫn làm việc về đúng thư mục chứa file .bat này
cd /d "%~dp0"

echo ============================================
echo           KHỞI CHẠY FB AUTOMATION
echo ============================================

:: 1. Chạy chương trình chính
python main.py

:: 2. Tự động Sync Git sau khi thoát menu
echo.
echo [!] Đang tự động đồng bộ code lên GitHub...
git add .
git commit -m "Auto update: %date% %time%"
git push origin main

echo.
echo [✓] Hoàn thành đồng bộ code!
pause