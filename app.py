
from app import create_app, db
from app.models.models import User, Group, Responsible

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Group': Group,
        'Responsible': Responsible
    }


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
