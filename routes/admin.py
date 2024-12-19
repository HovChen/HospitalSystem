from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.patient import db, Patient
from models.doctor import Doctor
from models.admin import Admin, Exception
from models.appointment import Appointment
from models.report import Evaluation
from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy import func

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
def dashboard():
    # 获取统计数据
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    total_appointments = Appointment.query.count()
    pending_exceptions = Exception.query.filter_by(status='pending').count()
    
    # 获取最近的异常记录
    recent_exceptions = Exception.query.order_by(Exception.discovery_date.desc()).limit(5).all()
    
    # 获取科室预约统计
    department_stats = db.session.query(
        Doctor.department,
        func.count(Appointment.id).label('count')
    ).join(Appointment).group_by(Doctor.department).all()
    
    department_labels = [stat[0] for stat in department_stats]
    department_data = [stat[1] for stat in department_stats]
    
    # 获取医生评分统计
    doctor_ratings = db.session.query(
        Doctor.name,
        func.avg(Evaluation.rating).label('avg_rating')
    ).join(Appointment).join(Evaluation).group_by(Doctor.id, Doctor.name).all()
    
    doctor_names = [rating[0] for rating in doctor_ratings]
    doctor_rating_values = [float(rating[1]) if rating[1] else 0 for rating in doctor_ratings]
    
    return render_template('admin/dashboard.html',
                         total_patients=total_patients,
                         total_doctors=total_doctors,
                         total_appointments=total_appointments,
                         pending_exceptions=pending_exceptions,
                         recent_exceptions=recent_exceptions,
                         department_labels=department_labels,
                         department_data=department_data,
                         doctor_names=doctor_names,
                         doctor_ratings=doctor_rating_values)

@admin.route('/doctors', methods=['GET', 'POST'])
@login_required
def manage_doctors():
    if request.method == 'POST':
        name = request.form.get('name')
        department = request.form.get('department')
        specialty = request.form.get('specialty')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        doctor = Doctor(
            name=name,
            department=department,
            specialty=specialty,
            phone=phone
        )
        doctor.set_password(password)
        
        db.session.add(doctor)
        db.session.commit()
        
        flash('医生信息添加成功')
        return redirect(url_for('admin.manage_doctors'))
        
    doctors = Doctor.query.all()
    return render_template('admin/doctors.html', doctors=doctors)

@admin.route('/exceptions')
@login_required
def view_exceptions():
    exceptions = Exception.query.all()
    return render_template('admin/exceptions.html', exceptions=exceptions)

@admin.route('/handle_exception/<int:exception_id>', methods=['POST'])
@login_required
def handle_exception(exception_id):
    exception = Exception.query.get_or_404(exception_id)
    handling_report = request.form.get('handling_report')
    
    exception.handler_id = current_user.id
    exception.handling_report = handling_report
    exception.status = 'resolved'
    
    db.session.commit()
    
    flash('异常处理成功')
    return redirect(url_for('admin.view_exceptions'))

@admin.route('/statistics')
@login_required
def statistics():
    # 获取各科室预约统计
    department_stats = db.session.query(
        Doctor.department,
        func.count(Appointment.id).label('appointment_count')
    ).join(Appointment).group_by(Doctor.department).all()
    
    # 获取医生评分统计
    doctor_ratings = db.session.query(
        Doctor.name,
        func.avg(Evaluation.rating).label('avg_rating')
    ).join(Appointment).join(Evaluation).group_by(Doctor.id).all()
    
    return render_template('admin/statistics.html',
                         department_stats=department_stats,
                         doctor_ratings=doctor_ratings)

@admin.route('/create_admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    if current_user.role != 'super_admin':
        flash('无权操作')
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if Admin.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('admin.create_admin'))
            
        admin = Admin(
            username=username,
            role=role
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        flash('管理员创建成功')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/create_admin.html') 