from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class OnboardingEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    joining_date = db.Column(db.String(20), nullable=False)
    
    employee_info = db.Column(db.JSON)  # stores entire employee section
    hr_info = db.Column(db.JSON)        # stores entire HR section
    status = db.Column(db.String(20), default='invited')
