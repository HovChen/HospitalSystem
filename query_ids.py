#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
医院预约系统 - ID查询脚本
此脚本用于查询系统中的患者ID和医生ID
使用方法：python query_ids.py [患者/医生]
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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
    id_card = db.Column(db.String(18), unique=True, nullable=False)

# 医生模型
class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    department = db.Column(db.String(64), nullable=False)
    specialty = db.Column(db.String(128), nullable=False)

def query_patients():
    """查询所有患者信息"""
    try:
        with app.app_context():
            patients = Patient.query.all()
            if not patients:
                print("\n当前系统中没有患者记录")
                return

            print("\n=== 患者信息列表 ===")
            print("ID  姓名     性别   身份证号")
            print("-" * 50)
            for patient in patients:
                print(f"{patient.id:<4}{patient.name:<8}{patient.gender:<6}{patient.id_card}")
            print("-" * 50)
            print(f"共找到 {len(patients)} 条记录\n")
    except Exception as e:
        print(f"查询患者信息时出错: {str(e)}")
        sys.exit(1)

def query_doctors():
    """查询所有医生信息"""
    try:
        with app.app_context():
            doctors = Doctor.query.all()
            if not doctors:
                print("\n当前系统中没有医生记录")
                return

            print("\n=== 医生信息列表 ===")
            print("ID  姓名     科室     专业")
            print("-" * 50)
            for doctor in doctors:
                print(f"{doctor.id:<4}{doctor.name:<8}{doctor.department:<8}{doctor.specialty}")
            print("-" * 50)
            print(f"共找到 {len(doctors)} 条记录\n")
    except Exception as e:
        print(f"查询医生信息时出错: {str(e)}")
        sys.exit(1)

def print_usage():
    """打印使用说明"""
    print("\n=== ID查询脚本使用说明 ===")
    print("用法: python query_ids.py [参数]")
    print("参数说明:")
    print("  患者  - 查询所有患者的ID信息")
    print("  医生  - 查询所有医生的ID信息")
    print("  全部  - 同时查询患者和医生的ID信息")
    print("\n示例:")
    print("  python query_ids.py 患者")
    print("  python query_ids.py 医生")
    print("  python query_ids.py 全部")
    print("=====================\n")

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['患者', '医生', '全部']:
        print_usage()
        sys.exit(1)

    query_type = sys.argv[1]
    
    try:
        if query_type == '患者' or query_type == '全部':
            query_patients()
        
        if query_type == '医生' or query_type == '全部':
            query_doctors()
            
    except Exception as e:
        print(f"执行查询时出错: {str(e)}")
        print("请确保数据库连接正确且可访问")
        sys.exit(1)
