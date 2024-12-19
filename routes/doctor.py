from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.patient import db
from models.appointment import Appointment, Schedule
from models.report import Report
from datetime import datetime, timedelta

doctor = Blueprint('doctor', __name__)

@doctor.route('/dashboard')
@login_required
def dashboard():
    # 获取今日预约信息
    today = datetime.now().date()
    today_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id,
        appointment_date=today
    ).order_by(Appointment.appointment_time).all()
    
    # 获取本周排班信息
    schedules = Schedule.query.filter_by(
        doctor_id=current_user.id
    ).filter(
        Schedule.work_date >= today,
        Schedule.work_date <= today + timedelta(days=7)
    ).order_by(Schedule.work_date).all()
    
    # 获取待处理的预约（状态为pending的预约）
    pending_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id,
        status='pending'
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    
    return render_template('doctor/dashboard.html',
                         today_appointments=today_appointments,
                         schedules=schedules,
                         pending_appointments=pending_appointments)

@doctor.route('/schedule', methods=['GET', 'POST'])
@login_required
def manage_schedule():
    if request.method == 'POST':
        work_date = request.form.get('work_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        available_slots = request.form.get('available_slots', 20)
        
        # 检查是否已有排班
        existing_schedule = Schedule.query.filter_by(
            doctor_id=current_user.id,
            work_date=work_date
        ).first()
        
        if existing_schedule:
            flash('该日期已有排班')
            return redirect(url_for('doctor.manage_schedule'))
            
        schedule = Schedule(
            doctor_id=current_user.id,
            work_date=work_date,
            start_time=start_time,
            end_time=end_time,
            available_slots=available_slots
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        flash('排班设置成功')
        return redirect(url_for('doctor.dashboard'))
        
    schedules = Schedule.query.filter_by(doctor_id=current_user.id).all()
    return render_template('doctor/schedule.html', schedules=schedules)

@doctor.route('/patients')
@login_required
def view_patients():
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    return render_template('doctor/patients.html', appointments=appointments)

@doctor.route('/create_report/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def create_report(appointment_id):
    if request.method == 'POST':
        report_type = request.form.get('report_type')
        content = request.form.get('content')
        
        report = Report(
            appointment_id=appointment_id,
            report_type=report_type,
            content=content
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('检查报告创建成功')
        return redirect(url_for('doctor.view_patients'))
        
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('doctor/create_report.html', appointment=appointment)

@doctor.route('/cancel_schedule/<int:schedule_id>')
@login_required
def cancel_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    
    if schedule.doctor_id != current_user.id:
        flash('无权操作')
        return redirect(url_for('doctor.manage_schedule'))
        
    # 检查是否有预约
    appointments = Appointment.query.filter_by(
        doctor_id=current_user.id,
        appointment_date=schedule.work_date
    ).all()
    
    if appointments:
        flash('该时段已有预约，无法取消')
        return redirect(url_for('doctor.manage_schedule'))
        
    db.session.delete(schedule)
    db.session.commit()
    
    flash('排班取消成功')
    return redirect(url_for('doctor.manage_schedule')) 