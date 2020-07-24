import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
# 模型对象序列化
# from flask.json import JSONEncoder as JSONEncoder_

# 初始化数据库
db = SQLAlchemy()


def create_app():
    # 初始化应用
    app = Flask(__name__)
    # 环境配置
    app_settings = os.getenv('APP_SETTINGS')
    # print(f'app_settings :{app_settings}')
    app.config.from_object(app_settings)
    # 安装扩展
    db.init_app(app)
    # 注册blueprint
    from project.api.views import users_blueprint
    app.register_blueprint(users_blueprint)
    return app
