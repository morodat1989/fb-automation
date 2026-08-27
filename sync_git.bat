@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================
echo         ĐỒNG BỘ CODE LÊN GITHUB
echo ============================================

echo [!] Đang thêm toàn bộ file thay đổi...
git add .

echo [!] Đang đóng gói commit...
git commit -m "Auto update: %date% %time%"

echo [!] Đang đẩy code lên GitHub (origin main)...
git push origin main

echo.
echo [✓] Đã hoàn thành đồng bộ code lên GitHub!
pause