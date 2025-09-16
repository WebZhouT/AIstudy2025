# main/controller/shimen_controller.py
from flask import Blueprint, jsonify, request
from main.service.shimen import ShimenService

shimen_bp = Blueprint('shimen', __name__)
shimen_service = ShimenService()

@shimen_bp.route('/start', methods=['POST'])
def start_shimen():
    """开始师门任务"""
    try: 
        data = request.json
        # 只接收门派和等级，其他忽略
        sect = data.get('sect', '五庄观')
        level = data.get('level', 69)
        
        # 启动任务（在新线程中）
        import threading
        thread = threading.Thread(target=shimen_service.start_shimen_tasks, args=(data,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success", 
            "message": "师门任务已开始",
            "data": {"sect": sect, "level": level}
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@shimen_bp.route('/stop', methods=['POST'])
def stop_shimen():
    """停止师门任务"""
    shimen_service.stop()
    return jsonify({"status": "success", "message": "已停止师门任务"})