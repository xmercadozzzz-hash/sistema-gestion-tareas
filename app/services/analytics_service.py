import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from app.models.models import Task

class AnalyticsService:
    @staticmethod
    def get_tasks_dataframe(user_id=None, is_admin=False):
        query = Task.query
        if not is_admin:
            query = query.filter_by(user_id=user_id)
        tasks = query.all()
        
        data = []
        for t in tasks:
            data.append({
                'id': t.id,
                'title': t.title,
                'priority': t.priority,
                'status': t.status,
                'group': t.group_rel.name if t.group_rel else 'Sin Grupo',
                'responsible': t.responsible_rel.name if t.responsible_rel else 'Sin Asignar',
                'due_date': t.due_date
            })
        return pd.DataFrame(data)

    @staticmethod
    def generate_status_chart(user_id=None, is_admin=False):
        df = AnalyticsService.get_tasks_dataframe(user_id, is_admin)
        plt.figure(figsize=(6, 4))
        if df.empty:
            plt.text(0.5, 0.5, 'Sin datos disponibles', horizontalalignment='center', verticalalignment='center')
            plt.axis('off')
        else:
            counts = df['status'].value_counts()
            colors = {'pendiente': '#f39c12', 'en proceso': '#3498db', 'completada': '#2ecc71', 'vencida': '#e74c3c'}
            bar_colors = [colors.get(x, '#95a5a6') for x in counts.index]
            counts.plot(kind='bar', color=bar_colors)
            plt.title('Tareas por Estado')
            plt.xlabel('Estado')
            plt.ylabel('Cantidad')
            plt.xticks(rotation=0)
            plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        return plot_url

    @staticmethod
    def generate_priority_chart(user_id=None, is_admin=False):
        df = AnalyticsService.get_tasks_dataframe(user_id, is_admin)
        plt.figure(figsize=(6, 4))
        if df.empty:
            plt.text(0.5, 0.5, 'Sin datos disponibles', horizontalalignment='center', verticalalignment='center')
            plt.axis('off')
        else:
            counts = df['priority'].value_counts()
            counts.plot(kind='pie', autopct='%1.1f%%', colors=['#27ae60', '#f1c40f', '#c0392b'])
            plt.title('Tareas por Prioridad')
            plt.ylabel('')
            plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        return plot_url