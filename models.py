from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), nullable=False, default='Medium')  # Low, Medium, High
    completed = db.Column(db.Boolean, nullable=False, default=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    email_contact = db.Column(db.String(120), nullable=True)
    phone_contact = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<Task {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'completed': self.completed,
            'creation_date': self.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
            'email_contact': self.email_contact,
            'phone_contact': self.phone_contact
        }