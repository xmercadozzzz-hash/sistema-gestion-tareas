import pytest
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.models import User, Group, Responsible, Task

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })

    with app.app_context():
        db.create_all()
        
        user = User(username='testuser', email='test@test.com', role='admin')
        user.set_password('password123')
        db.session.add(user)
        
        group = Group(name='Grupo TCC', description='Equipo de prueba')
        db.session.add(group)
        db.session.commit()
        
        resp = Responsible(name='Juan Pérez', email='juan@test.com', group_id=group.id)
        db.session.add(resp)
        db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_auth_register_and_login(client):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Panel Principal de Control' in response.data

def test_create_and_edit_task(client):
    client.post('/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
    
    response = client.post('/tasks/new', data={
        'title': 'Investigación Arquitectura Hexagonal',
        'description': 'Redactar informe final',
        'group_id': 1,
        'responsible_id': 1,
        'due_date': (datetime.utcnow() + timedelta(days=5)).strftime('%Y-%m-%d'),
        'priority': 'alta',
        'status': 'pendiente'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Investigaci\xc3\xb3n Arquitectura Hexagonal' in response.data
    
    task = Task.query.first()
    response = client.post(f'/tasks/edit/{task.id}', data={
        'title': 'Investigación Actualizada',
        'description': 'Informe actualizado',
        'group_id': 1,
        'responsible_id': 1,
        'due_date': (datetime.utcnow() + timedelta(days=5)).strftime('%Y-%m-%d'),
        'priority': 'media',
        'status': 'en proceso'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Investigaci\xc3\xb3n Actualizada' in response.data

def test_delete_task(client):
    client.post('/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
    
    task = Task(
        title='Tarea para borrar',
        group_id=1,
        responsible_id=1,
        due_date=datetime.utcnow() + timedelta(days=1),
        user_id=1
    )
    db.session.add(task)
    db.session.commit()
    
    task_id = task.id
    response = client.post(f'/tasks/delete/{task_id}', follow_redirects=True)
    assert response.status_code == 200
    assert db.session.get(Task, task_id) is None