from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class Patient(UserMixin, db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    id_card = db.Column(db.String(18), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # 关联关系
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic')
    evaluations = db.relationship('Evaluation', backref='patient', lazy='dynamic')
    
    def get_id(self):
        return f'P{self.id}'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<Patient {self.name}>' 