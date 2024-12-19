from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.patient import db
from models.doctor import Doctor
from models.appointment import Appointment, Schedule
from models.report import Report, Evaluation, Payment
from datetime import datetime, timedelta

patient = Blueprint('patient', __name__)

@patient.route('/dashboard')
@login_required
def dashboard():
    # 获取患者的预约信息
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    # 添加today变量用于前端判断是否可以取消预约
    today = datetime.now().date()
    return render_template('patient/dashboard.html', 
                         appointments=appointments,
                         today=today)

@patient.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        
        # 检查是否在可预约时间范围内（0-7天）
        appointment_datetime = datetime.strptime(appointment_date, '%Y-%m-%d')
        days_diff = (appointment_datetime.date() - datetime.now().date()).days
        
        if days_diff < 0 or days_diff > 7:
            flash('预约时间必须在未来7天内')
            return redirect(url_for('patient.book_appointment'))
            
        # 检查医生是否有空余号源
        schedule = Schedule.query.filter_by(
            doctor_id=doctor_id,
            work_date=appointment_date
        ).first()
        
        if not schedule:
            flash('该医生在所选日期没有排班')
            return redirect(url_for('patient.book_appointment'))
            
        # 检查所选时间是否有号源
        if not schedule.is_time_available(appointment_time):
            flash('该时段已无可用号源')
            return redirect(url_for('patient.book_appointment'))
            
        # 创建预约
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=datetime.strptime(appointment_time, '%H:%M').time(),
            status='confirmed'
        )
        
        # 更新号源数量
        schedule.book_slot(appointment_time)
        
        db.session.add(appointment)
        db.session.commit()
        
        flash('预约成功')
        return redirect(url_for('patient.dashboard'))
    
    # 获取所有科室
    departments = db.session.query(Doctor.department).distinct().all()
    departments = [dept[0] for dept in departments]
    
    # 获取日期范围
    today = datetime.now().date()
    min_date = today.strftime('%Y-%m-%d')
    max_date = (today + timedelta(days=7)).strftime('%Y-%m-%d')
    
    return render_template('patient/book_appointment.html',
                         departments=departments,
                         min_date=min_date,
                         max_date=max_date)

@patient.route('/api/doctors', methods=['GET'])
@login_required
def get_doctors():
    department = request.args.get('department')
    if not department:
        return jsonify([])
    
    # 打印调试信息
    print(f"查询科室：{department}")
    doctors = Doctor.query.filter_by(department=department).all()
    print(f"找到医生数量：{len(doctors)}")
    for doc in doctors:
        print(f"医生ID：{doc.id}, 姓名：{doc.name}, 科室：{doc.department}, 专业：{doc.specialty}")
    
    return jsonify([{
        'id': doctor.id,
        'name': f"{doctor.name} - {doctor.specialty}",  # 修改名称格式
        'specialty': doctor.specialty,
        'department': doctor.department
    } for doctor in doctors])

@patient.route('/api/doctor/<int:doctor_id>', methods=['GET'])
@login_required
def get_doctor_info(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return jsonify({
        'name': doctor.name,
        'department': doctor.department,
        'specialty': doctor.specialty
    })

@patient.route('/api/available_times', methods=['GET'])
@login_required
def get_available_times():
    doctor_id = request.args.get('doctor_id')
    date = request.args.get('date')
    
    print(f"获取可用时间 - 医生ID：{doctor_id}, 日期：{date}")
    
    if not doctor_id or not date:
        print("缺少必要参数")
        return jsonify([])
    
    schedule = Schedule.query.filter_by(
        doctor_id=doctor_id,
        work_date=date
    ).first()
    
    if not schedule:
        print("未找到排班信息")
        return jsonify([])
    
    if schedule.available_slots <= 0:
        print("没有可用号源")
        return jsonify([])
    
    print(f"找到排班信息 - 可用号源：{schedule.available_slots}")
    
    # 生成可用时间段
    times = []
    
    # 上午时间段：8:30-11:30
    current_time = datetime.strptime('08:30', '%H:%M')
    end_time = datetime.strptime('11:30', '%H:%M')
    
    while current_time < end_time:
        times.append(current_time.strftime('%H:%M'))
        current_time += timedelta(minutes=15)
    
    # 下午时间段：14:00-17:00
    current_time = datetime.strptime('14:00', '%H:%M')
    end_time = datetime.strptime('17:00', '%H:%M')
    
    while current_time < end_time:
        times.append(current_time.strftime('%H:%M'))
        current_time += timedelta(minutes=15)
    
    print(f"生成的所有时间段：{times}")
    
    # 检查已预约的时间
    booked_appointments = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=datetime.strptime(date, '%Y-%m-%d').date()
    ).all()
    
    booked_times = []
    for appointment in booked_appointments:
        if isinstance(appointment.appointment_time, str):
            booked_times.append(appointment.appointment_time)
        else:
            booked_times.append(appointment.appointment_time.strftime('%H:%M'))
    
    print(f"已预约的时间段：{booked_times}")
    
    # 过滤掉已预约的时间
    available_times = [time for time in times if time not in booked_times]
    print(f"可用的时间段：{available_times}")
    
    return jsonify(available_times)

@patient.route('/view_reports')
@login_required
def view_reports():
    reports = Report.query.join(Appointment).filter(
        Appointment.patient_id == current_user.id
    ).all()
    return render_template('patient/reports.html', reports=reports)

@patient.route('/payments')
@login_required
def payments():
    payments = Payment.query.join(Appointment).filter(
        Appointment.patient_id == current_user.id
    ).all()
    return render_template('patient/payments.html', payments=payments)

@patient.route('/evaluate/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def evaluate(appointment_id):
    if request.method == 'POST':
        rating = request.form.get('rating')
        content = request.form.get('content')
        
        evaluation = Evaluation(
            appointment_id=appointment_id,
            patient_id=current_user.id,
            rating=rating,
            content=content
        )
        
        db.session.add(evaluation)
        db.session.commit()
        
        flash('评价提交成功')
        return redirect(url_for('patient.dashboard'))
        
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('patient/evaluate.html', appointment=appointment)

@patient.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # 检查是否是当前用户的预约
    if appointment.patient_id != current_user.id:
        flash('无权操作此预约')
        return redirect(url_for('patient.dashboard'))
    
    # 检查预约是否可以取消（只能取消未来的预约）
    if appointment.appointment_date < datetime.now().date():
        flash('无法取消过期的预约')
        return redirect(url_for('patient.dashboard'))
    
    # 恢复号源数量
    schedule = Schedule.query.filter_by(
        doctor_id=appointment.doctor_id,
        work_date=appointment.appointment_date
    ).first()
    
    if schedule:
        schedule.restore_slot(appointment.appointment_time.strftime('%H:%M'))
    
    # 更新预约状态
    appointment.status = 'cancelled'
    db.session.commit()
    
    flash('预约已取消')
    return redirect(url_for('patient.dashboard'))