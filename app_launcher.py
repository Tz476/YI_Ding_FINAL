#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TZ War Robot - Mac Application Launcher with PyWebView
用于打包成独立应用的启动器（使用原生窗口）
"""

import os
import sys
import time
import threading
from pathlib import Path

def get_resource_path(relative_path):
    """获取资源文件的绝对路径（支持打包后的应用）"""
    try:
        # PyInstaller创建临时文件夹，路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def start_backend():
    """启动后端 Flask 服务器"""
    print("🚀 Starting TZ War Robot Backend...")
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'production'
    
    # 导入并运行 Flask app
    backend_path = get_resource_path('backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    try:
        from backend.app import app
        
        # 在后台线程中运行 Flask
        def run_flask():
            app.run(
                host='127.0.0.1',
                port=5001,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        print("✅ Backend server started on http://127.0.0.1:5001")
        return True
    
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        import traceback
        traceback.print_exc()
        return False


def wait_for_server():
    """等待服务器启动"""
    import urllib.request
    
    # 等待服务器启动（最多等待10秒）
    max_wait = 10
    for i in range(max_wait):
        try:
            urllib.request.urlopen('http://127.0.0.1:5001/health', timeout=1)
            print("✅ Server is ready!")
            return True
        except Exception:
            if i < max_wait - 1:
                print(f"⏳ Waiting for server... ({i+1}/{max_wait})")
                time.sleep(1)
            else:
                print("❌ Server did not start in time")
                return False
    return False


def main():
    """主函数"""
    print("=" * 50)
    print("🤖 TZ: The Lost War Robot")
    print("=" * 50)
    print()
    
    # 启动后端服务器
    if not start_backend():
        print("❌ Failed to start backend server")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # 等待服务器就绪
    if not wait_for_server():
        print("❌ Server did not start properly")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # 使用 pywebview 创建原生窗口
    try:
        import webview
        
        print("🖥️  Creating native window...")
        print()
        print("=" * 50)
        print("✅ Application is running!")
        print("=" * 50)
        print()
        print("📝 Instructions:")
        print("  - The game is now in a native window")
        print("  - Close the window to quit the game")
        print()
        
        # 创建窗口 - 手机屏幕尺寸（iPhone）
        window = webview.create_window(
            title='TZ: The Lost War Robot',
            url='http://127.0.0.1:5001',
            width=375,   # iPhone 标准宽度
            height=812,  # iPhone 标准高度（包含刘海屏）
            resizable=False,  # 固定尺寸，不可调整
            fullscreen=False,
            background_color='#0a0e1a',  # 匹配前端背景色
            text_select=True
        )
        
        # 启动 webview（这会阻塞直到窗口关闭）
        webview.start(debug=False)
        
        print("\n\n👋 Window closed. Shutting down...")
        
    except ImportError:
        print("❌ PyWebView not found. Please install it:")
        print("   pip install pywebview")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to create window: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == '__main__':
    main()
