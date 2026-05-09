from flask import Flask, render_template, request, redirect, session, flash, url_for
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

    # Already logged in
    if session.get('user_id'):
        return redirect('/dashboard')

    if request.method == 'POST':

        try:

            username = request.form.get('username').strip()

            password = request.form.get('password')

            role = request.form.get('role')

            # ================= VALIDATION =================

            if not username or not password or not role:

                flash("⚠️ All fields are required")

                return redirect('/register')

            # Username length
            if len(username) < 3:

                flash("⚠️ Username too short")

                return redirect('/register')

            # Password length
            if len(password) < 4:

                flash("⚠️ Password must be minimum 4 characters")

                return redirect('/register')

            # Role validation
            if role not in ['admin', 'electrician']:

                flash("⚠️ Invalid role selected")

                return redirect('/register')

            # ================= DUPLICATE USER =================

            existing_user = User.query.filter_by(
                username=username
            ).first()

            if existing_user:

                flash("⚠️ Username already exists")

                return redirect('/register')

            # ================= PROFILE IMAGE =================

            file = request.files.get('profile_pic')

            image_data = None

            if file and file.filename:

                allowed_extensions = [
                    '.png',
                    '.jpg',
                    '.jpeg'
                ]

                filename = file.filename.lower()

                if not any(
                    filename.endswith(ext)
                    for ext in allowed_extensions
                ):

                    flash("⚠️ Only PNG/JPG images allowed")

                    return redirect('/register')

                image_data = base64.b64encode(
                    file.read()
                ).decode('utf-8')

            # ================= CREATE USER =================

            user = User(

                username=username,

                password=generate_password_hash(password),

                role=role,

                profile_pic=image_data

            )

            db.session.add(user)

            db.session.commit()

            flash("✅ Registered Successfully")

            return redirect('/login')

        except Exception as e:

            db.session.rollback()

            print("REGISTER ERROR:", e)

            flash("❌ Registration Failed")

            return redirect('/register')

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

# ================= EDIT JOB =================
@app.route('/edit_job/<int:id>', methods=['GET', 'POST'])
def edit_job(id):

    if session.get('role') != 'admin':
        return redirect('/dashboard')

    job = db.session.get(Job, id)

    if request.method == 'POST':

        job.title = request.form.get('title')

        job.location = request.form.get('location')

        db.session.commit()

        flash("Job Updated")

        return redirect('/jobs')

    return render_template(
        'edit_job.html',
        job=job
    )

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

@app.route('/profile', methods=['GET', 'POST'])
def profile():

    if not session.get('user_id'):
        return redirect('/login')

    user = db.session.get(
        User,
        session['user_id']
    )

    if request.method == 'POST':

        user.username = request.form.get('username')

        password = request.form.get('password')

        if password:
            user.password = generate_password_hash(password)

        file = request.files.get('profile_pic')

        if file and file.filename:

            user.profile_pic = base64.b64encode(
                file.read()
            ).decode('utf-8')

        db.session.commit()

        session['username'] = user.username

        flash("✅ Profile Updated")

        return redirect('/profile')

    return render_template(
        'profile.html',
        user=user
    )

# ================= EDIT USER =================

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):

    if not session.get('user_id'):
        return redirect('/login')

    # ONLY ADMIN
    if session.get('role') != 'admin':
        flash("Access Denied")
        return redirect('/dashboard')

    user = db.session.get(User, user_id)

    if not user:
        flash("User Not Found")
        return redirect('/electricians')

    if request.method == 'POST':

        user.username = request.form.get('username')
        user.role = request.form.get('role')

        # PASSWORD UPDATE
        password = request.form.get('password')

        if password:
            user.password = generate_password_hash(password)

        # PROFILE IMAGE
        file = request.files.get('profile_pic')

        if file and file.filename:

            user.profile_pic = base64.b64encode(
                file.read()
            ).decode('utf-8')

        db.session.commit()

        flash("✅ User Updated Successfully")

        return redirect('/electricians')

    return render_template(
        'edit_user.html',
        edit_user=user
    )


# ================= DELETE USER =================

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):

    if not session.get('user_id'):
        return redirect('/login')

    if session.get('role') != 'admin':
        flash("Access Denied")
        return redirect('/dashboard')

    user = db.session.get(User, user_id)

    if not user:
        flash("User Not Found")
        return redirect('/electricians')

    # PREVENT ADMIN DELETE SELF
    if user.id == session.get('user_id'):
        flash("You Cannot Delete Yourself")
        return redirect('/electricians')

    try:

        db.session.delete(user)

        db.session.commit()

        flash("✅ User Deleted Successfully")

    except Exception as e:

        db.session.rollback()

        print(e)

        flash("Delete Failed")

    return redirect('/electricians')


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

# ================= DELETE TASK =================
@app.route('/delete_task/<int:id>')
def delete_task(id):

    if session.get('role') != 'admin':
        return redirect('/dashboard')

    task = db.session.get(Task, id)

    if task:

        db.session.delete(task)

        db.session.commit()

        flash("Task Deleted")

    return redirect('/dashboard')


# ================= PAYMENTS =================

@app.route('/payments', methods=['GET', 'POST'])
def payments():

    if not session.get('user_id'):
        return redirect('/login')

    if request.method == 'POST':

        amount = int(request.form.get('amount'))
        client_name = request.form.get('client_name')

        try:

            order_amount = amount * 100

            order = client.order.create({
                "amount": order_amount,
                "currency": "INR",
                "payment_capture": "1"
            })

            session['payment_amount'] = amount
            session['client_name'] = client_name

            return render_template(
                'payment_gateway.html',
                order=order,
                key=app.config['RAZORPAY_KEY_ID'],
                amount=amount
            )

        except Exception as e:

            print("PAYMENT ERROR:", e)

            flash("Payment Gateway Error")

            return redirect('/dashboard')

    return render_template('payments.html')

# ================= PAYMENT SUCCESS =================

@app.route('/payment_success')
def payment_success():

    try:

        payment = Payment(

            payer=session.get('client_name'),

            receiver="Admin",

            amount=session.get('payment_amount'),

            payment_type="ClientToAdmin",

            status="Success"
        )

        db.session.add(payment)

        db.session.commit()

        flash("✅ Payment Successful")

    except Exception as e:

        db.session.rollback()

        print("PAYMENT ERROR:", e)

        flash("Payment Failed")

    return redirect('/transactions')

# ================= PAY ELECTRICIAN =================

@app.route('/pay_electrician/<int:user_id>')
def pay_electrician(user_id):

    if session.get('role') != 'admin':
        return redirect('/dashboard')

    electrician = db.session.get(User, user_id)

    if not electrician:

        flash("Electrician not found")

        return redirect('/electricians')

    try:

        payment = Payment(

            payer="Admin",

            receiver=electrician.username,

            amount=2000,

            payment_type="Salary",

            payment_method="Bank Transfer",

            transaction_id=f"TXN{datetime.now().timestamp()}",

            status="Success"

        )

        db.session.add(payment)

        db.session.commit()

        flash(f"₹2000 paid to {electrician.username}")

    except Exception as e:

        db.session.rollback()

        print("PAY ERROR:", e)

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
    
    
    # ================= ELECTRICIAN PAYMENT HISTORY =================

@app.route('/electrician_payments')
def electrician_payments():

    if not session.get('user_id'):
        return redirect('/login')

    if session.get('role') != 'electrician':
        return redirect('/dashboard')

    try:

        payments = Payment.query.filter_by(
            receiver=session.get('username')
        ).order_by(
            Payment.id.desc()
        ).all()

        total = sum(p.amount for p in payments)

        return render_template(
            'electrician_payments.html',
            payments=payments,
            total=total
        )

    except Exception as e:

        print("ELECTRICIAN PAYMENT ERROR:", e)

        flash("Payment history error")

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


@app.route('/backup')
def backup():

    if session.get('role') != 'admin':
        return redirect('/dashboard')

    import shutil

    shutil.copy(
        'instance/electrician.db',
        'backup_electrician.db'
    )

    flash("Backup Created")

    return redirect('/dashboard')

#====global error handler=====
@app.errorhandler(404)
def not_found(e):

    return render_template(
        'error.html',
        msg="404 Page Not Found"
    ),404


@app.errorhandler(500)
def server_error(e):

    return render_template(
        'error.html',
        msg="500 Internal Server Error"
    ),500


# ================= LOGOUT =================
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)