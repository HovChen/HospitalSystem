from app import create_app
from models.appointment import Schedule, db
from datetime import datetime, time

app = create_app()

with app.app_context():
    # 检查是否已有排班
    today = datetime.now().date()
    existing_schedule = Schedule.query.filter_by(
        doctor_id=18,
        work_date=today
    ).first()
    
    if existing_schedule:
        print('今日已有排班')
    else:
        # 添加今日排班
        schedule = Schedule(
            doctor_id=18,
            work_date=today,
            start_time=time(8, 30),
            end_time=time(17, 0),
            available_slots=24,
            morning_slots=12,
            afternoon_slots=12
        )
        db.session.add(schedule)
        db.session.commit()
        print('排班添加成功') 