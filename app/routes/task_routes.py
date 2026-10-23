from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.models import Task, Group, Responsible
from app.services.task_service import TaskService
from app.services.analytics_service import AnalyticsService

bp = Blueprint('tasks', __name__)

@bp.route('/')
@login_required
def dashboard():
    is_admin = current_user.role == 'admin'
    stats = TaskService.get_dashboard_stats(current_user.id, is_admin)
    
    query = Task.query
    if not is_admin:
        query = query.filter_by(user_id=current_user.id)
    recent_tasks = query.order_by(Task.created_at.desc()).limit(5).all()
    
    status_chart = AnalyticsService.generate_status_chart(current_user.id, is_admin)
    priority_chart = AnalyticsService.generate_priority_chart(current_user.id, is_admin)
    
    return render_template('dashboard.html', stats=stats, recent_tasks=recent_tasks, 
                           status_chart=status_chart, priority_chart=priority_chart)

@bp.route('/tasks')
@login_required
def task_list():
    TaskService.update_overdue_tasks()
    is_admin = current_user.role == 'admin'
    
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    search = request.args.get('search', '')
    
    query = Task.query
    if not is_admin:
        query = query.filter_by(user_id=current_user.id)
        
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if search:
        query = query.filter(Task.title.ilike(f'%{search}%'))
        
    tasks = query.order_by(Task.due_date.asc()).all()
    groups = Group.query.all()
    responsibles = Responsible.query.all()
    
    return render_template('tasks.html', tasks=tasks, groups=groups, responsibles=responsibles, 
                           selected_status=status, selected_priority=priority, search_query=search)

@bp.route('/tasks/new', methods=['GET', 'POST'])
@login_required
def create_task():
    groups = Group.query.all()
    responsibles = Responsible.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        group_id = request.form.get('group_id')
        responsible_id = request.form.get('responsible_id')
        due_date_str = request.form.get('due_date')
        priority = request.form.get('priority')
        status = request.form.get('status', 'pendiente')
        
        if not title or not due_date_str or not group_id or not responsible_id:
            flash('Por favor complete todos los campos obligatorios.', 'danger')
            return render_template('task_form.html', groups=groups, responsibles=responsibles, task=None)
            
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            return render_template('task_form.html', groups=groups, responsibles=responsibles, task=None)
            
        task = Task(
            title=title,
            description=description,
            group_id=int(group_id),
            responsible_id=int(responsible_id),
            due_date=due_date,
            priority=priority,
            status=status,
            user_id=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        flash('Tarea creada exitosamente.', 'success')
        return redirect(url_for('tasks.task_list'))
        
    return render_template('task_form.html', groups=groups, responsibles=responsibles, task=None)

@bp.route('/tasks/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = db.session.get(Task, id)
    if not task or (task.user_id != current_user.id and current_user.role != 'admin'):
        flash('Tarea no encontrada o sin permisos.', 'danger')
        return redirect(url_for('tasks.task_list'))
        
    groups = Group.query.all()
    responsibles = Responsible.query.all()
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.group_id = int(request.form.get('group_id'))
        task.responsible_id = int(request.form.get('responsible_id'))
        task.priority = request.form.get('priority')
        task.status = request.form.get('status')
        
        due_date_str = request.form.get('due_date')
        try:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            return render_template('task_form.html', groups=groups, responsibles=responsibles, task=task)
            
        db.session.commit()
        flash('Tarea actualizada correctamente.', 'success')
        return redirect(url_for('tasks.task_list'))
        
    return render_template('task_form.html', groups=groups, responsibles=responsibles, task=task)

@bp.route('/tasks/delete/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    task = db.session.get(Task, id)
    if not task or (task.user_id != current_user.id and current_user.role != 'admin'):
        flash('Tarea no encontrada o sin permisos.', 'danger')
        return redirect(url_for('tasks.task_list'))
        
    db.session.delete(task)
    db.session.commit()
    flash('Tarea eliminada correctamente.', 'info')
    return redirect(url_for('tasks.task_list'))

@bp.route('/analytics')
@login_required
def analytics():
    is_admin = current_user.role == 'admin'
    status_chart = AnalyticsService.generate_status_chart(current_user.id, is_admin)
    priority_chart = AnalyticsService.generate_priority_chart(current_user.id, is_admin)
    return render_template('analytics.html', status_chart=status_chart, priority_chart=priority_chart)

@bp.route('/management', methods=['GET', 'POST'])
@login_required
def management():
    if current_user.role != 'admin':
        flash('Acceso restringido a administradores.', 'danger')
        return redirect(url_for('tasks.dashboard'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_group':
            name = request.form.get('group_name')
            desc = request.form.get('group_desc')
            if name:
                db.session.add(Group(name=name, description=desc))
                db.session.commit()
                flash('Grupo creado correctamente.', 'success')
        elif action == 'add_responsible':
            name = request.form.get('resp_name')
            email = request.form.get('resp_email')
            group_id = request.form.get('resp_group')
            if name and email and group_id:
                db.session.add(Responsible(name=name, email=email, group_id=int(group_id)))
                db.session.commit()
                flash('Responsable registrado correctamente.', 'success')
                
        return redirect(url_for('tasks.management'))
        
    groups = Group.query.all()
    responsibles = Responsible.query.all()
    return render_template('management.html', groups=groups, responsibles=responsibles)