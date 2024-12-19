from .patient import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Doctor(UserMixin, db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    department = db.Column(db.String(64), nullable=False)
    specialty = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(128), nullable=False)
    
    # 关联关系
    schedules = db.relationship('Schedule', backref='doctor', lazy='dynamic', cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_id(self):
        return f'D{self.id}'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Doctor {self.name}>' 