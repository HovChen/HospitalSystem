from .patient import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # super_admin, department_admin
    
    def get_id(self):
        return f'A{self.id}'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.id}>'

class Exception(db.Model):
    __tablename__ = 'exceptions'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    discovery_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    handler_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    handling_report = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, processing, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    handler = db.relationship('Admin', backref='handled_exceptions', lazy=True)
    
    def __repr__(self):
        return f'<Exception {self.id}>'