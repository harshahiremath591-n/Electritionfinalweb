from flask import Flask, render_template, request, redirect, session, flash
from config import Config
from models import db, User, Task, Job, Material, Payment
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone

import os
import base64
import razorpay

app = Flask(__name__)
app.secret_key = "harsha_secret"
app.config.from_object(Config)

# ================= RAZORPAY =================
client = razorpay.Client(
    auth=(
        app.config['RAZORPAY_KEY_ID'],
        app.config['RAZORPAY_KEY_SECRET']
    )
)

db.init_app(app)

with app.app_context():
    db.create_all()
    


# ================= HOME =================
@app.route('/')
def home():
    return render_template('home.html')

# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        user = User.query.filter_by(
            username=request.form.get('username')
        ).first()

        if user and check_password_hash(
            user.password,
            request.form.get('password')
        ):

            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username

            return redirect('/dashboard')

        flash("Invalid Login")

    return render_template('login.html')

# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        # ✅ DUPLICATE CHECK
        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            flash("Username already exists")

            return redirect('/register')

        file = request.files.get('profile_pic')

        image_data = None

        if file and file.filename:

         image_data = base64.b64encode(
           file.read()
         ).decode('utf-8')

        user = User(
            username=username,
            password=generate_password_hash(password),
            role=role,
            profile_pic=image_data
        )

        db.session.add(user)
        db.session.commit()

        flash("Registered Successfully")

        return redirect('/login')

    return render_template('register.html')

# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():

    if not session.get('user_id'):
        return redirect('/login')

    if session['role'] == 'electrician':
        tasks = Task.query.filter_by(
            assigned_to=session['user_id']
        ).all()
    else:
        tasks = Task.query.all()

    completed = Task.query.filter_by(status="Completed").count()
    pending = Task.query.filter_by(status="Pending").count()
    processing = Task.query.filter_by(status="Processing").count()

    return render_template(
        'dashboard.html',
        tasks=tasks,
        completed=completed,
        pending=pending,
        processing=processing
    )

# ================= JOBS =================
@app.route('/jobs', methods=['GET', 'POST'])
def jobs():

    if request.method == 'POST':

        job = Job(
            title=request.form.get('title'),
            location=request.form.get('location')
        )

        db.session.add(job)
        db.session.commit()

    jobs = Job.query.all()

    return render_template('jobs.html', jobs=jobs)

# ================= MATERIALS =================
@app.route('/materials', methods=['GET', 'POST'])
def materials():

    if not session.get('user_id'):
        return redirect('/login')

    if request.method == 'POST':

        try:

            material = Material(
                name=request.form.get('name'),
                quantity=int(request.form.get('quantity')),
                cost=float(request.form.get('cost'))
            )

            db.session.add(material)
            db.session.commit()

            flash("Material Added")

        except Exception as e:

            db.session.rollback()

            print("MATERIAL ERROR:", e)

            flash("Material Error")

    materials = Material.query.all()

    return render_template(
        'materials.html',
        materials=materials
    )

# ================= ELECTRICIANS =================
@app.route('/electricians')
def electricians():

    users = User.query.filter_by(
        role='electrician'
    ).all()

    return render_template(
        'electricians.html',
        users=users
    )

# ================= REPORTS =================
@app.route('/reports')
def reports():

    tasks = Task.query.all()

    return render_template(
        'reports.html',
        tasks=tasks
    )

# ================= PROFILE =================
@app.route('/profile')
def profile():

    user = db.session.get(
        User,
        session['user_id']
    )

    return render_template(
        'profile.html',
        user=user
    )

# ================= ADD TASK =================
@app.route('/add_task', methods=['GET', 'POST'])
def add_task():

    electricians = User.query.filter_by(
        role='electrician'
    ).all()

    jobs = Job.query.all()

    if request.method == 'POST':

        task = Task(
            title=request.form.get('title'),
            assigned_to=request.form.get('user_id'),
            job_id=request.form.get('job_id'),
            status="Pending"
        )

        db.session.add(task)
        db.session.commit()

        flash("Task Assigned")

        return redirect('/dashboard')

    return render_template(
        'add_task.html',
        electricians=electricians,
        jobs=jobs
    )

# ================= UPDATE TASK =================
@app.route('/update/<int:id>', methods=['POST'])
def update(id):

    if not session.get('user_id'):
        return redirect('/login')

    task = db.session.get(Task, id)

    if not task:
        flash("Task not found")
        return redirect('/dashboard')

    # Only electrician can update
    if session.get('role') != 'electrician':
        return redirect('/dashboard')

    # Only assigned electrician
    if task.assigned_to != session.get('user_id'):
        flash("Unauthorized")
        return redirect('/dashboard')

    try:

        status = request.form.get('status')

        # ✅ UPDATE STATUS
        if status in ["Pending", "Processing", "Completed"]:

            task.status = status

            if status == "Completed":
                task.completed_at = datetime.now(timezone.utc)

        # ✅ REPORT UPLOAD
        file = request.files.get('report')

        if file and file.filename:

            filename = f"{task.id}_{file.filename}"

            path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )

            file.save(path)

            task.report = filename

        db.session.commit()

        flash("Task Updated Successfully")

    except Exception as e:

        db.session.rollback()

        print("UPDATE ERROR:", e)

        flash("Task Update Failed")

    return redirect('/dashboard')


# ================= CLIENT PAYMENT =================
@app.route('/payments')
def payments():

    if not session.get('user_id'):
        return redirect('/login')

    try:

        amount = 500 * 100

        order = client.order.create({

            "amount": amount,

            "currency": "INR",

            "payment_capture": "1"

        })

        return render_template(
            'payments.html',
            order=order,
            key=app.config['RAZORPAY_KEY_ID']
        )

    except Exception as e:

        print("PAYMENT ERROR:", e)

        flash("Payment Gateway Error")

        return redirect('/dashboard')

# ================= PAYMENT SUCCESS =================
@app.route('/payment_success')
def payment_success():

    try:

        payment = Payment(

            payer="Client",

            receiver="Admin",

            amount=500,

            payment_type="ClientToAdmin",

            status="Success"

        )

        db.session.add(payment)

        db.session.commit()

        flash("Client Payment Successful")

    except Exception as e:

        db.session.rollback()

        print("PAYMENT SAVE ERROR:", e)

    return redirect('/dashboard')

# ================= PAY ELECTRICIAN =================
@app.route('/pay_electrician/<int:user_id>')
def pay_electrician(user_id):

    if session.get('role') != 'admin':
        return redirect('/dashboard')

    electrician = db.session.get(User, user_id)

    if not electrician:
        flash("Electrician Not Found")
        return redirect('/dashboard')

    try:

        payment = Payment(

            payer="Admin",

            receiver=electrician.username,

            amount=2000,

            payment_type="AdminToElectrician",

            status="Success"

        )

        db.session.add(payment)

        db.session.commit()

        flash("Salary Paid Successfully")

    except Exception as e:

        db.session.rollback()

        print("SALARY ERROR:", e)

        flash("Payment Failed")

    return redirect('/electricians')


# ================= TRANSACTIONS =================
@app.route('/transactions')
def transactions():

    if not session.get('user_id'):
        return redirect('/login')

    try:

        data = Payment.query.order_by(
            Payment.id.desc()
        ).all()

        return render_template(
            'transaction_history.html',
            data=data
        )

    except Exception as e:

        print("TRANSACTION ERROR:", e)

        flash("Transaction Error")

        return redirect('/dashboard')
    
        #=====--====

@app.context_processor
def inject_user():

    if session.get('user_id'):

        user = db.session.get(
            User,
            session['user_id']
        )

        return dict(user=user)

    return dict(user=None)


# ================= LOGOUT =================
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)