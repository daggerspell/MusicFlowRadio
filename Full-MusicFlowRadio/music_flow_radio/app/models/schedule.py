from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dj_id = db.Column(db.Integer, db.ForeignKey("dj.id"), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Schedule for {self.dj.name} on {self.day_of_week}>"
