import os
import socket
import subprocess
import sys
import time
from pathlib import Path

CDP_PORT = 9222
# Thư mục lưu trữ profile riêng cho tool
BASE_PROFILE_DIR = Path(__file__).parent / "browser_profile"


def is_port_open(port: int = CDP_PORT, host: str = "127.0.0.1") -> bool:
    """Kiểm tra xem cổng CDP đã thực sự mở hay chưa."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0


def kill_chrome() -> None:
    """Tắt các tiến trình Chrome chạy ngầm."""
    try:
        subprocess.run(
            "taskkill /F /T /IM chrome.exe",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1.5)
        print("⚡ Đã dọn dẹp các tiến trình Chrome ngầm.")
    except Exception:
        pass


def get_available_profiles() -> list[dict]:
    """Danh sách các Profile tự động hóa trong thư mục browser_profile."""
    BASE_PROFILE_DIR.mkdir(exist_ok=True)
    
    # Danh sách profile cố định để bạn dễ chọn
    default_profiles = [
        {"folder": "Profile_1", "label": "Tài khoản FB 1 (Profile 1)"},
        {"folder": "Profile_2", "label": "Tài khoản FB 2 (Profile 2)"},
        {"folder": "Profile_3", "label": "Tài khoản FB 3 (Profile 3)"},
    ]
    return default_profiles


def launch_chrome(profile_folder: str, cdp_port: int = CDP_PORT) -> None:
    """Khởi chạy Chrome với User Data Dir riêng biệt để đảm bảo mở cổng CDP."""
    kill_chrome()

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

    # Tạo đường dẫn lưu profile riêng trong dự án
    target_profile_dir = BASE_PROFILE_DIR / profile_folder
    target_profile_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=> Đang bật Chrome tự động hóa: {profile_folder}")
    print(f"=> Lưu dữ liệu tại: {target_profile_dir}")

    cmd = [
        chrome_path,
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir={target_profile_dir.resolve()}",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.facebook.com/",
    ]

    try:
        subprocess.Popen(
            cmd,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )
    except Exception as e:
        print(f"❌ Lỗi bật Chrome: {e}")
        return

    print(f"=> Đang chờ cổng CDP {cdp_port} mở", end="")
    success = False
    for _ in range(10):
        if is_port_open(cdp_port):
            success = True
            break
        print(".", end="", flush=True)
        time.sleep(1)

    print()
    if success:
        print(f"✅ [THÀNH CÔNG]: Cổng kết nối CDP {cdp_port} đã sẵn sàng!")
        print("💡 LƯU Ý: Nếu đây là lần đầu mở, hãy đăng nhập Facebook trên cửa sổ Chrome vừa hiện ra. Lần sau sẽ tự động lưu đăng nhập.")
    else:
        print(f"❌ [CẢNH BÁO]: Cổng {cdp_port} chưa mở!")

    input("\n👉 Nhấn ENTER để tiếp tục...")


def main() -> None:
    while True:
        print("\n" + "=" * 50)
        print("      QUẢN LÝ TÀI KHOẢN & ĐĂNG NHẬP FB")
        print("=" * 50)
        print("[1] Chọn Profile tự động hóa (Lưu riêng trong tool)")
        print("[0] Quay lại menu trước")
        print("=" * 50)

        choice = input("Nhập lựa chọn của bạn: ").strip()

        if choice == "1":
            profiles = get_available_profiles()
            print("\n--- DANH SÁCH PROFILE TỰ ĐỘNG HÓA ---")
            for idx, p in enumerate(profiles, 1):
                print(f"[{idx}] {p['label']}")
            print("[0] Quay lại menu trước")
            print("-" * 39)

            p_choice = input("Chọn số thứ tự profile bạn muốn dùng: ").strip()
            if p_choice == "0":
                continue
            if p_choice.isdigit() and 1 <= int(p_choice) <= len(profiles):
                selected = profiles[int(p_choice) - 1]
                launch_chrome(selected["folder"])
            else:
                print("Lựa chọn không hợp lệ!")

        elif choice == "0":
            break
        else:
            print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()