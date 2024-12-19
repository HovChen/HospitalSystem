from app import create_app
from models.patient import db
from models.doctor import Doctor
from models.admin import Admin
from models.appointment import Schedule
from datetime import datetime, timedelta, time

def init_db():
    app = create_app()
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已经有管理员账号
        if not Admin.query.filter_by(id=1).first():
            # 创建超级管理员
            admin = Admin(
                id=1,
                username='admin',
                role='super_admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # 添加示例医生
        departments = {
            '内科': 'IM',
            '外科': 'SU',
            '儿科': 'PE',
            '妇科': 'GY',
            '眼科': 'OP',
            '骨科': 'OR'
        }
        specialties = {
            '内科': ['心内科', '消化内科', '呼吸内科'],
            '外科': ['普外科', '神经外科', '心胸外科'],
            '儿科': ['儿童内科', '儿童外科', '新生儿科'],
            '妇科': ['妇科', '产科', '计划生育科'],
            '眼科': ['眼底病', '白内障', '青光眼'],
            '骨科': ['脊柱外科', '关节外科', '运动医学科']
        }
        
        # 清除所有现有医生和排班
        Doctor.query.delete()
        Schedule.query.delete()
        
        doctor_id = 1
        for dept, dept_code in departments.items():
            for i, specialty in enumerate(specialties[dept], 1):
                username = f'{dept_code}{i}'  # 例如：IM1, IM2, IM3
                doctor = Doctor(
                    id=doctor_id,
                    username=username,
                    name=f'{dept}{i}号医生',
                    department=dept,
                    specialty=specialty,
                    phone='1234567890'
                )
                doctor.set_password('doctor123')
                db.session.add(doctor)
                
                # 为每个医生添加未来7天的排班
                today = datetime.now().date()
                for day in range(1, 8):
                    schedule_date = today + timedelta(days=day)
                    schedule = Schedule(
                        doctor_id=doctor_id,
                        work_date=schedule_date,
                        start_time=time(8, 30),  # 8:30
                        end_time=time(17, 0),    # 17:00
                        available_slots=24,       # 上午12个号，下午12个号，共24个号
                        morning_slots=12,         # 上午可用号数
                        afternoon_slots=12        # 下午可用号数
                    )
                    db.session.add(schedule)
                
                doctor_id += 1
        
        db.session.commit()
        print("数据库初始化完成！")
        print("\n默认账号：")
        print("超级管理员 - 工号：1，密码：admin123")
        print("\n医生账号：")
        for dept, dept_code in departments.items():
            print(f"\n{dept}：")
            for i, specialty in enumerate(specialties[dept], 1):
                print(f"  {dept}{i}号医生 - {specialty}")
                print(f"    工号：{dept_code}{i}，密码：doctor123")

if __name__ == '__main__':
    init_db() 