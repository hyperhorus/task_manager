from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Task
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MySQL Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# MySQL Database URI
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

app.config[
    'SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Optional: Connection pool settings for better performance
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db.init_app(app)


# Rest of your routes remain the same...
@app.route('/')
def index():
    filter_status = request.args.get('filter', 'all')
    sort_by = request.args.get('sort', 'creation_date')

    query = Task.query

    if filter_status == 'completed':
        query = query.filter_by(completed=True)
    elif filter_status == 'pending':
        query = query.filter_by(completed=False)

    if sort_by == 'priority':
        # Custom order: High, Medium, Low
        priority_order = db.case(
            (Task.priority == 'High', 1),
            (Task.priority == 'Medium', 2),
            (Task.priority == 'Low', 3),
            else_=4
        )
        tasks = query.order_by(priority_order).all()
    elif sort_by == 'title':
        tasks = query.order_by(Task.title).all()
    else:  # creation_date
        tasks = query.order_by(Task.creation_date.desc()).all()

    return render_template('index.html', tasks=tasks, filter_status=filter_status, sort_by=sort_by)


@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task = Task(
            title=request.form['title'],
            description=request.form['description'],
            priority=request.form['priority'],
            email_contact=request.form['email_contact'] or None,
            phone_contact=request.form['phone_contact'] or None
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_task.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.priority = request.form['priority']
        task.email_contact = request.form['email_contact'] or None
        task.phone_contact = request.form['phone_contact'] or None

        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_task.html', task=task)


@app.route('/toggle/<int:id>')
def toggle_task(id):
    task = Task.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    flash(f'Task marked as {"completed" if task.completed else "pending"}!', 'success')
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('index'))


# API endpoints for JSON responses
@app.route('/api/tasks')
def api_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])


@app.route('/api/tasks/<int:id>')
def api_task(id):
    task = Task.query.get_or_404(id)
    return jsonify(task.to_dict())


if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    app.run(debug=True)