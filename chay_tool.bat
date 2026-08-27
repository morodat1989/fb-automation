@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================
echo           KHỞI CHẠY FB AUTOMATION
echo ============================================

:: Kiểm tra cổng 9222
netstat -ano | findstr /C:":9222 " > nul
if errorlevel 1 goto LAUNCH_CHROME

echo [+] Đã phát hiện Chrome CDP Port 9222 đang hoạt động!
goto RUN_MAIN

:LAUNCH_CHROME
echo [!] Chưa mở Chrome CDP Port 9222.
echo [!] Đang tự động mở cửa sổ Chrome mới qua login_setup.py...
start cmd /k "python login_setup.py"
echo [!] Đang chờ Chrome sẵn sàng trong 5 giây...
timeout /t 5 /nobreak > nul

:RUN_MAIN
echo.
echo [!] Đang kết nối và khởi tạo Menu chính...
python main.py

echo.
echo [!] Đang tự động đồng bộ code lên GitHub...
git add .
git commit -m "Auto update: %date% %time%"
git push origin main

echo.
echo [✓] Đã hoàn thành đồng bộ code lên GitHub!
pause