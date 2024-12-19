from .patient import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending（待确认）, confirmed（已确认）, cancelled（已取消）, completed（已完成）
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    reports = db.relationship('Report', backref='appointment', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='appointment', lazy='dynamic', cascade='all, delete-orphan')
    evaluations = db.relationship('Evaluation', backref='appointment', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Appointment {self.id} - Patient {self.patient_id} - Doctor {self.doctor_id}>'

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    available_slots = db.Column(db.Integer, default=24)  # 上午12个号，下午12个号
    morning_slots = db.Column(db.Integer, default=12)    # 上午可用号数
    afternoon_slots = db.Column(db.Integer, default=12)  # 下午可用号数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Schedule {self.work_date} {self.start_time}-{self.end_time}>'
    
    # 检查指定时间是否有可用号源
    def is_time_available(self, time_str):
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        if time_obj < datetime.strptime('12:00', '%H:%M').time():
            return self.morning_slots > 0
        return self.afternoon_slots > 0
    
    # 预约成功后更新号源数量
    def book_slot(self, time_str):
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        if time_obj < datetime.strptime('12:00', '%H:%M').time():
            if self.morning_slots > 0:
                self.morning_slots -= 1
                self.available_slots -= 1
                return True
        else:
            if self.afternoon_slots > 0:
                self.afternoon_slots -= 1
                self.available_slots -= 1
                return True
        return False
    
    # 取消预约后恢复号源数量
    def restore_slot(self, time_str):
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        if time_obj < datetime.strptime('12:00', '%H:%M').time():
            self.morning_slots += 1
            self.available_slots += 1
        else:
            self.afternoon_slots += 1
            self.available_slots += 1