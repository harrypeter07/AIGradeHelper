from datetime import datetime
from app import db

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
