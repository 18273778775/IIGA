import webbrowser
import threading
import time
from app import run_flask_app

# 后端服务的 URL
BACKEND_URL = "http://127.0.0.1:5000"

def start_backend():
    """
    在新的线程中启动 Flask 后端服务。
    """
    print("正在启动后端服务...")
    # 使用 threading 在后台运行 Flask 应用
    # run_flask_app() 是阻塞的，所以需要在线程中运行
    thread = threading.Thread(target=run_flask_app, daemon=True)
    thread.start()
    print(f"后端服务应该已经在 {BACKEND_URL} 上运行。")

def open_frontend():
    """
    在默认浏览器中打开前端页面。
    """
    print(f"尝试在浏览器中打开 {BACKEND_URL}...")
    try:
        webbrowser.open(BACKEND_URL)
        print("浏览器已打开或尝试打开页面。")
    except Exception as e:
        print(f"无法自动打开浏览器: {e}")
        print(f"请手动在浏览器中访问 {BACKEND_URL}")

if __name__ == "__main__":
    start_backend()
    # 等待一段时间确保后端服务有足够的时间启动
    # 这个时间可能需要根据实际情况调整
    print("等待后端服务启动...")
    time.sleep(3)  # 等待3秒
    open_frontend()

    # 让主线程保持运行，否则 daemon 线程可能会在 Flask 应用完全启动前退出
    # 这在某些情况下是必要的，特别是如果 Flask 应用启动较慢
    # 或者，如果 run_flask_app 本身是阻塞的，并且不是 daemon 线程，则不需要这个循环
    print("一键启动完成。后端服务正在运行。按 Ctrl+C 关闭。")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭应用...")
        # 这里可以添加任何必要的清理代码
        print("应用已关闭。")
