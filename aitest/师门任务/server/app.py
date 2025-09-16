from flask import Flask, send_from_directory  # 补充导入 send_from_directory
from main.config.config import DATABASE
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# 注册蓝图
from main.router import Routers

# 创建Flask应用程序实例
app = Flask(__name__)
# 设置静态文件夹路径和静态URL路径
app.static_folder = 'public'
app.static_url_path = '/public/'

# 访问图片的静态资源路径
@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(app.static_folder + '/uploads', filename)

# 配置Flask应用程序
app.config['SQLALCHEMY_DATABASE_URI'] = f"{DATABASE['ENGINE']}://{DATABASE['URI']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 跨域配置
CORS(app, resources=r'/*')

# 创建SQLAlchemy对象，用于数据交互
db = SQLAlchemy(app)

# 将 页面的路由 注册到应用程序中
app.register_blueprint(Routers)

# 启动flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3112, threaded=False, debug=True)
    db.engine.dispose()  # 修正：SQLAlchemy 实例没有 close 方法
    print("Good bye!")