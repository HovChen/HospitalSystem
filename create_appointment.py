#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
医院预约系统 - 预约创建脚本
此脚本用于直接创建医生预约记录，跳过Web界面直接操作数据库
作用：可以快速为指定患者创建一个预约记录
使用方法：python create_appointment.py 患者ID 医生ID 日期 时间
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time
import sys

# 初始化Flask应用
app = Flask(__name__)

# MySQL数据库配置
MYSQL_HOST = '124.222.16.229'
MYSQL_USER = 'hospital'
MYSQL_PASSWORD = 'hospital'
MYSQL_DB = 'hospital'

# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 患者模型
class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    id_card = db.Column(db.String(18), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

# 医生模型
class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    department = db.Column(db.String(64), nullable=False)
    specialty = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(128), nullable=False)

class Appointment(db.Model):
    """
    预约模型类
    用于映射数据库中的appointments表
    包含预约的所有必要字段
    """
    __tablename__ = 'appointments'
    
    # 数据库字段定义
    id = db.Column(db.Integer, primary_key=True)  # 预约ID，主键
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)  # 患者ID，外键
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)  # 医生ID，外键
    appointment_date = db.Column(db.Date, nullable=False)  # 预约日期
    appointment_time = db.Column(db.Time, nullable=False)  # 预约时间
    status = db.Column(db.String(20), default='confirmed')  # 预约状态，默认为已确认
    notes = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

def check_and_create_tables():
    """检查并创建必要的数据库表"""
    try:
        with app.app_context():
            # 检查表是否存在
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # 打印现有表
            print("\n当前数据库中的表：")
            for table in existing_tables:
                print(f"- {table}")
            
            # 创建表（如果不存在）
            print("\n正在检查并创建必要的表...")
            db.create_all()
            print("表检查和创建完成！\n")
            
    except Exception as e:
        print(f"检查和创建表时出错: {str(e)}")
        sys.exit(1)

def verify_ids(patient_id, doctor_id):
    """验证患者ID和医生ID是否存在"""
    try:
        with app.app_context():
            patient = Patient.query.get(patient_id)
            if not patient:
                print(f"错误：患者ID {patient_id} 不存在")
                return False
                
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                print(f"错误：医生ID {doctor_id} 不存在")
                return False
                
            print(f"\n验证通过：")
            print(f"患者: {patient.name} (ID: {patient.id})")
            print(f"医生: {doctor.name} - {doctor.department} (ID: {doctor.id})")
            return True
            
    except Exception as e:
        print(f"验证ID时出错: {str(e)}")
        return False

def create_appointment(patient_id, doctor_id, date_str, time_str):
    """
    创建新的预约记录
    
    参数:
        patient_id (int): 患者ID
        doctor_id (int): 医生ID
        date_str (str): 预约日期，格式：YYYY-MM-DD（如：2024-01-20）
        time_str (str): 预约时间，格式：HH:MM（如：09:30）
    """
    try:
        # 验证ID是否存在
        if not verify_ids(patient_id, doctor_id):
            sys.exit(1)

        # 将输入的日期字符串转换为datetime.date对象
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        # 将输入的时间字符串转换为datetime.time对象
        appointment_time = datetime.strptime(time_str, '%H:%M').time()

        # 创建新的预约记录对象
        appointment = Appointment(
            patient_id=patient_id,  # 设置患者ID
            doctor_id=doctor_id,    # 设置医生ID
            appointment_date=appointment_date,  # 设置预约日期
            appointment_time=appointment_time,  # 设置预约时间
            status='confirmed'      # 设置预约状态为已确认
        )

        # 使用Flask应用上下文将预约记录保存到数据库
        with app.app_context():
            # 添加到数据库会话
            db.session.add(appointment)
            # 提交事务
            db.session.commit()
            
            # 打印成功信息
            print("\n=== 预约创建成功 ===")
            print(f"预约ID: {appointment.id}")
            print(f"预约日期: {date_str}")
            print(f"预约时间: {time_str}")
            print("==================\n")

    except ValueError as ve:
        # 处理日期时间格式错误
        print(f"日期或时间格式错误: {str(ve)}")
        print("正确的格式应该是：YYYY-MM-DD HH:MM")
        print("例如：2024-01-20 09:30")
        sys.exit(1)
    except Exception as e:
        # 处理其他所有错误
        print(f"创建预约时发生错误: {str(e)}")
        print("请检查：")
        print("1. 数据库连接是否正确")
        print("2. 患者ID是否存在")
        print("3. 医生ID是否存在")
        sys.exit(1)

def print_usage():
    """打印脚本的使用说明"""
    print("\n=== 预约创建脚本使用说明 ===")
    print("用法: python create_appointment.py 患者ID 医生ID 日期 时间")
    print("参数说明:")
    print("  患者ID: 数字，必须是存在的患者ID")
    print("  医生ID: 数字，必须是存在的医生ID")
    print("  日期: YYYY-MM-DD格式，如：2024-01-20")
    print("  时间: HH:MM格式，如：09:30")
    print("\n示例:")
    print("  python create_appointment.py 1 2 2024-01-20 09:30")
    print("========================\n")

if __name__ == "__main__":
    # 首先检查并创建必要的表
    check_and_create_tables()

    # 检查命令行参数数量是否正确
    if len(sys.argv) != 5:
        print_usage()
        sys.exit(1)

    try:
        # 获取并转换命令行参数
        patient_id = int(sys.argv[1])  # 转换患者ID为整数
        doctor_id = int(sys.argv[2])   # 转换医生ID为整数
        date_str = sys.argv[3]         # 预约日期字符串
        time_str = sys.argv[4]         # 预约时间字符串

        # 创建预约
        create_appointment(patient_id, doctor_id, date_str, time_str)
        
    except ValueError:
        print("错误：患者ID和医生ID必须是数字！")
        print_usage()
        sys.exit(1)
