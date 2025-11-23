from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

# 创建 Flask 应用，指定静态文件目录
app = Flask(__name__, 
            static_folder='../frontend/dist',
            static_url_path='')
CORS(app)

# 注册TZ游戏路由
from tz_routes import register_tz_routes
register_tz_routes(app)

# 服务前端静态文件
@app.route('/')
def serve_frontend():
    """服务前端 index.html"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """服务其他静态文件"""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # 如果文件不存在，返回 index.html（支持前端路由）
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 TZ War Robot Communication System")
    print("=" * 50)
    print("Application running on: http://localhost:5001")
    print("Serving frontend from: ../frontend/dist")
    print("=" * 50)
    print("\nAvailable API endpoints:")
    print("  POST /api/tz/start    - 开始游戏")
    print("  POST /api/tz/message  - 发送消息")
    print("  GET  /api/tz/state    - 获取状态")
    print("  POST /api/tz/reset    - 重置游戏")
    print("  GET  /health          - 健康检查")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001)
