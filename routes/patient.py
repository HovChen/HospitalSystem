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
    date_str = request.args.get('date')
    
    if not doctor_id or not date_str:
        return jsonify([])
    
    selected_date = datetime.strptime(date_str, '%Y-%m-%d')
    now = datetime.now().time()
    is_today = selected_date.date() == datetime.now().date()
    
    # 获取医生排班信息
    schedule = Schedule.query.filter_by(
        doctor_id=doctor_id,
        work_date=selected_date.date()
    ).first()
    
    if not schedule:
        return jsonify([])
    
    times = []
    morning_start = datetime.strptime('08:00', '%H:%M').time()
    morning_end = datetime.strptime('12:00', '%H:%M').time()
    afternoon_start = datetime.strptime('14:00', '%H:%M').time()
    afternoon_end = datetime.strptime('17:00', '%H:%M').time()
    
    # 如果停诊状态，检查停诊时间段
    if schedule.status == 'off' and schedule.off_start_time and schedule.off_end_time:
        off_start = schedule.off_start_time
        off_end = schedule.off_end_time
    else:
        off_start = None
        off_end = None
    
    # 生成上午时间段
    if not is_today or (is_today and now < morning_end):
        current = morning_start
        while current < morning_end:
            # 如果是当天且当前时间已过，跳过这个时间段
            if is_today and current <= now:
                current = (datetime.combine(datetime.today(), current) + timedelta(minutes=15)).time()
                continue
            # 如果在停诊时间段内，跳过
            if off_start and off_end and off_start <= current <= off_end:
                current = (datetime.combine(datetime.today(), current) + timedelta(minutes=15)).time()
                continue
            if schedule.morning_slots > 0:
                times.append(current.strftime('%H:%M'))
            current = (datetime.combine(datetime.today(), current) + timedelta(minutes=15)).time()
    
    # 生成下午时间段
    if not is_today or (is_today and now < afternoon_end):
        current = afternoon_start
        while current < afternoon_end:
            # 如果是当天且当前时间已过，跳过这个时间段
            if is_today and current <= now:
                current = (datetime.combine(datetime.today(), current) + timedelta(minutes=15)).time()
                continue
            # 如果在停诊时间段内，跳过
            if off_start and off_end and off_start <= current <= off_end:
                current = (datetime.combine(datetime.today(), current) + timedelta(minutes=15)).time()
                continue
            if schedule.afternoon_slots > 0:
                times.append(current.strftime('%H:%M'))
            current = (datetime.combine(datetime.today(), current) + timedelta(minutes=15)).time()
    
    # 如果是加班状态，添加加班时间段
    if schedule.status == 'extra' and schedule.extra_start_time and schedule.extra_end_time and schedule.extra_slots > 0:
        extra_start = schedule.extra_start_time
        extra_end = schedule.extra_end_time
        current = extra_start
        
        while current < extra_end:
            # 如果是当天且当前时间已过，跳过这个时间段
            if is_today and current <= now:
                current = (datetime.combine(datetime.today(), current) + timedelta(minutes=15)).time()
                continue
            times.append(current.strftime('%H:%M'))
            current = (datetime.combine(datetime.today(), current) + timedelta(minutes=15)).time()
    
    # 检查已预约的时间
    booked_appointments = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=selected_date.date()
    ).all()
    
    booked_times = []
    for appointment in booked_appointments:
        if isinstance(appointment.appointment_time, str):
            booked_times.append(appointment.appointment_time)
        else:
            booked_times.append(appointment.appointment_time.strftime('%H:%M'))
    
    # 过滤掉已预约的时间
    available_times = [time for time in times if time not in booked_times]
    available_times.sort()
    
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
    # 获取预约信息
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # 检查是否是当前用户的预约
    if appointment.patient_id != current_user.id:
        flash('无权评价此预约')
        return redirect(url_for('patient.dashboard'))
    
    # 检查预约状态是否为已完成
    if appointment.status != 'completed':
        flash('只能评价已完成的预约')
        return redirect(url_for('patient.dashboard'))
    
    # 检查是否已经评价过
    existing_evaluation = Evaluation.query.filter_by(appointment_id=appointment_id).first()
    if existing_evaluation:
        flash('已经评价过此预约')
        return redirect(url_for('patient.dashboard'))
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        content = request.form.get('content')
        
        # 验证评分
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (TypeError, ValueError):
            flash('评分必须是1-5的整数')
            return redirect(url_for('patient.evaluate', appointment_id=appointment_id))
        
        # 验证评价内容
        if not content or len(content.strip()) < 10:
            flash('评价内容不能少于10个字符')
            return redirect(url_for('patient.evaluate', appointment_id=appointment_id))
        
        # 创建评价
        evaluation = Evaluation(
            appointment_id=appointment_id,
            patient_id=current_user.id,
            rating=rating,
            content=content.strip()
        )
        
        db.session.add(evaluation)
        db.session.commit()
        
        flash('评价提交成功')
        return redirect(url_for('patient.dashboard'))
    
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

@patient.route('/payment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def make_payment(appointment_id):
    # 获取预约信息
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # 检查是否是当前用户的预约
    if appointment.patient_id != current_user.id:
        flash('无权操作此预约')
        return redirect(url_for('patient.dashboard'))
    
    # 检查预约状态是否为已完成
    if appointment.status != 'completed':
        flash('只能对已完成的预约进行缴费')
        return redirect(url_for('patient.dashboard'))
    
    # 检查是否已经支付
    existing_payment = Payment.query.filter_by(appointment_id=appointment_id).first()
    if existing_payment:
        flash('该预约已完成支付')
        return redirect(url_for('patient.dashboard'))
    
    # 根据科室设置不同的金额（模拟）
    amount_map = {
        '内科': 50,
        '外科': 60,
        '儿科': 40,
        '妇科': 55,
        '眼科': 45,
        '口腔科': 65,
        '皮肤科': 50,
        '精神科': 80,
        '中医科': 45
    }
    amount = amount_map.get(appointment.doctor.department, 50)
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if not payment_method:
            flash('请选择支付方式')
            return redirect(url_for('patient.make_payment', appointment_id=appointment_id))
        
        # 创建支付记录
        payment = Payment(
            appointment_id=appointment_id,
            amount=amount,
            payment_method=payment_method,
            payment_date=datetime.now(),
            status='paid'  # 直接设置为已支付（模拟支付）
        )
        
        db.session.add(payment)
        db.session.commit()
        
        flash('支付成功')
        return redirect(url_for('patient.dashboard'))
    
    return render_template('patient/payment.html', 
                         appointment=appointment,
                         amount=amount)