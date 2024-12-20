from app import create_app
from models.admin import Admin, db

app = create_app()

with app.app_context():
    admins = Admin.query.all()
    if not admins:
        print("数据库中没有管理员账号，正在创建超级管理员账号...")
        admin = Admin(
            username="admin",
            role="super_admin"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("超级管理员账号创建成功！")
        print("用户名: admin")
        print("密码: admin123")
    else:
        print("现有管理员账号：")
        for admin in admins:
            print(f"ID: {admin.id}, 用户名: {admin.username}, 角色: {admin.role}") 