from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.models import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('¡Bienvenido de nuevo!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('tasks.dashboard'))
        else:
            flash('Usuario o contraseña inválidos.', 'danger')
            
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'warning')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado.', 'warning')
            return redirect(url_for('auth.register'))
            
        new_user = User(username=username, email=email, role='miembro')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registro exitoso. Por favor inicie sesión.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))