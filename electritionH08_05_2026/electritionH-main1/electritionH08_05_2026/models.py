from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ================= USERS =================
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(db.String(200))

    role = db.Column(db.String(20))

    profile_pic = db.Column(db.Text)

# ================= JOBS =================
class Job(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))

    location = db.Column(db.String(200))

# ================= TASKS =================
class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    completed_at = db.Column(db.DateTime)

    assigned_to = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey('job.id')
    )

    report = db.Column(db.String(200))
    
    
    

# ================= MATERIALS =================
class Material(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    quantity = db.Column(db.Integer)

    cost = db.Column(db.Float)

#================== TASK MATERIALS =================
    class TaskMaterial(db.Model):

        id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(
        db.Integer,
        db.ForeignKey('task.id')
    )    
    material_id = db.Column(
        db.Integer,
        db.ForeignKey('material.id')
    )

    quantity_used = db.Column(db.Integer)
    
    
# ================= PAYMENTS =================
class Payment(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    payer = db.Column(db.String(100))

    receiver = db.Column(db.String(100))

    amount = db.Column(db.Float)

    payment_type = db.Column(db.String(100))

    status = db.Column(db.String(50))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )