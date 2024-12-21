from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from config import Config
from models.patient import db, Patient
from models.doctor import Doctor
from models.appointment import Appointment, Schedule
from models.report import Report, Evaluation, Payment
from models.admin import Admin, Exception

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # 注册蓝图
    from routes.auth import auth as auth_blueprint
    from routes.patient import patient as patient_blueprint
    from routes.doctor import doctor as doctor_blueprint
    from routes.admin import admin as admin_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(patient_blueprint)
    app.register_blueprint(doctor_blueprint, url_prefix='/doctor')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    @login_manager.user_loader
    def load_user(user_id):
        # 尝试从不同的用户模型中加载用户
        if user_id.startswith('P'):
            return Patient.query.get(int(user_id[1:]))
        elif user_id.startswith('D'):
            return Doctor.query.get(int(user_id[1:]))
        elif user_id.startswith('A'):
            return Admin.query.get(int(user_id[1:]))
        return None
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 