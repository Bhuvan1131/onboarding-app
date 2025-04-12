from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class OnboardingEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    joining_date = db.Column(db.String(20))

    employee_info = db.Column(db.JSON)  # Stores all fields in one column
    hr_info = db.Column(db.JSON)
    status = db.Column(db.String(20))
