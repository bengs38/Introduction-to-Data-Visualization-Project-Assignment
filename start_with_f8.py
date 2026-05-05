from __future__ import annotations

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

import keyboard
import psutil


ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173


def is_port_in_use(port: int) -> bool:
    for connection in psutil.net_connections(kind="inet"):
        if connection.laddr and connection.laddr.port == port and connection.status == psutil.CONN_LISTEN:
            return True
    return False


def start_backend() -> None:
    if is_port_in_use(BACKEND_PORT):
        print("Backend zaten çalışıyor")
        return

    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload"],
        cwd=str(BACKEND_DIR),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    print("Backend başlatıldı")


def start_frontend() -> None:
    if is_port_in_use(FRONTEND_PORT):
        print("Frontend zaten çalışıyor")
        return

    subprocess.Popen(
        ["cmd", "/c", "npm.cmd", "run", "dev"],
        cwd=str(FRONTEND_DIR),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    print("Frontend başlatıldı")


def start_application() -> None:
    start_backend()
    start_frontend()
    time.sleep(5)
    print("Tarayıcı açılıyor")
    webbrowser.open(f"http://localhost:{FRONTEND_PORT}")


def main() -> None:
    print("Akıllı Veri Analiz Asistanı hazır.")
    print("Uygulamayı başlatmak için F8 tuşuna basın. Çıkmak için CTRL+C.")
    keyboard.add_hotkey("f8", start_application)
    keyboard.wait()


if __name__ == "__main__":
    main()
