from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.patient import Patient, db
from models.doctor import Doctor
from models.admin import Admin
from werkzeug.security import generate_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if user_type == 'patient':
            user = Patient.query.filter_by(id_card=username).first()
        elif user_type == 'doctor':
            user = Doctor.query.filter_by(username=username).first()
        elif user_type == 'admin':
            user = Admin.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for(f'{user_type}.dashboard'))
        flash('用户名或密码错误')
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        id_card = request.form.get('id_card')
        password = request.form.get('password')
        gender = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        phone = request.form.get('phone')
        
        if Patient.query.filter_by(id_card=id_card).first():
            flash('该身份证号已被注册')
            return redirect(url_for('auth.register'))
            
        patient = Patient(
            name=name,
            id_card=id_card,
            gender=gender,
            birth_date=birth_date,
            phone=phone
        )
        patient.set_password(password)
        
        db.session.add(patient)
        db.session.commit()
        
        flash('注册成功，请登录')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index')) 