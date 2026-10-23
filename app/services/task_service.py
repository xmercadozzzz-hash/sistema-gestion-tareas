from datetime import datetime
from app import db
from app.models.models import Task, Responsible, Group

class TaskService:
    @staticmethod
    def update_overdue_tasks():
        now = datetime.utcnow()
        tasks = Task.query.filter(Task.status != 'completada').all()
        updated = False
        for task in tasks:
            if task.due_date < now and task.status != 'vencida':
                task.status = 'vencida'
                updated = True
        if updated:
            db.session.commit()

    @staticmethod
    def get_dashboard_stats(user_id=None, is_admin=False):
        TaskService.update_overdue_tasks()
        query = Task.query
        if not is_admin:
            query = query.filter_by(user_id=user_id)
            
        total = query.count()
        pending = query.filter_by(status='pendiente').count()
        in_process = query.filter_by(status='en proceso').count()
        completed = query.filter_by(status='completada').count()
        overdue = query.filter_by(status='vencida').count()
        
        progress = round((completed / total * 100), 1) if total > 0 else 0.0

        return {
            'total': total,
            'pending': pending,
            'in_process': in_process,
            'completed': completed,
            'overdue': overdue,
            'progress': progress
        }