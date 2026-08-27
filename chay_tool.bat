@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================
echo           KHỞI CHẠY FB AUTOMATION
echo ============================================

:: Kiểm tra xem Chrome CDP 9222 đã hoạt động chưa
netstat -ano | findstr /C:":9222 " > nul
if not errorlevel 1 (
    echo [✓] Đã phát hiện Chrome CDP Port 9222 đang chạy sẵn.
    goto RUN_MAIN
)

:: Nếu chưa chạy, chạy login_setup.py ngay tại cửa sổ này để chọn Profile
echo [!] Chưa mở Chrome CDP Port 9222.
echo [!] Đang khởi động trình chọn Profile...
echo --------------------------------------------
python login_setup.py
echo --------------------------------------------

:RUN_MAIN
echo.
echo [!] Đang kết nối Chrome và mở Menu chính...
python main.py

echo.
echo [!] Đang tự động đồng bộ code lên GitHub...
git add .
git commit -m "Auto update: %date% %time%"
git push origin main

echo.
echo [✓] Đã hoàn thành đồng bộ code lên GitHub!
pause