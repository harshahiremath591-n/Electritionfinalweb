from flask import Flask, render_template, request, redirect, session, flash, send_file
from config import Config
from models import db, User, Task, Job, Material, Payment, MaterialUsage, Attendance, Location
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask_socketio import SocketIO
from fpdf import FPDF

import os
import base64
import razorpay
import shutil

app = Flask(__name__)

app.secret_key = "harsha_secret"

app.config.from_object(Config)

app.permanent_session_lifetime = timedelta(minutes=10)

socketio = SocketIO(app)

# ================= RAZORPAY =================

client = razorpay.Client(
    auth=(
        app.config['RAZORPAY_KEY_ID'],
        app.config['RAZORPAY_KEY_SECRET']
    )
)

# ================= DATABASE =================

db.init_app(app)

with app.app_context():
    db.create_all()

# ================= LOGIN REQUIRED =================

def login_required(f):

    @wraps(f)

    def wrapper(*args, **kwargs):

        if not session.get('user_id'):
            return redirect('/login')

        return f(*args, **kwargs)

    return wrapper

# ================= HOME =================

@app.route('/')
def home():

    return render_template('home.html')

# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')

        password = request.form.get('password')

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session.clear()

            session.permanent = True

            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username

            flash("✅ Login Successful")

            return redirect('/dashboard')

        flash("❌ Invalid Login")

    return render_template('login.html')

# ================= REGISTER =================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if session.get('user_id'):
        return redirect('/dashboard')

    if request.method == 'POST':

        try:

            username = request.form.get('username').strip()

            password = request.form.get('password')

            role = request.form.get('role')

            # ================= VALIDATION =================

            if not username or not password or not role:

                flash("⚠️ All fields required")

                return redirect('/register')

            if len(username) < 3:

                flash("⚠️ Username too short")

                return redirect('/register')

            if len(password) < 4:

                flash("⚠️ Password minimum 4 characters")

                return redirect('/register')

            if role not in ['admin', 'electrician']:

                flash("⚠️ Invalid role")

                return redirect('/register')

            existing = User.query.filter_by(
                username=username
            ).first()

            if existing:

                flash("⚠️ Username already exists")

                return redirect('/register')

            # ================= IMAGE =================

            image_data = None

            file = request.files.get('profile_pic')

            if file and file.filename:

                allowed = ['.png', '.jpg', '.jpeg']

                filename = file.filename.lower()

                if not any(
                    filename.endswith(ext)
                    for ext in allowed
                ):

                    flash("⚠️ Only PNG/JPG allowed")

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

            flash("✅ Registration Successful")

            return redirect('/login')

        except Exception as e:

            db.session.rollback()

            print("REGISTER ERROR:", e)

            flash("❌ Registration Failed")

            return redirect('/register')

    return render_template('register.html')

# ================= ATTENDANCE =================

from datetime import datetime

@app.route('/attendance')
@login_required
def attendance():

    data = Attendance.query.order_by(
        Attendance.id.desc()
    ).all()

    return render_template(
        'attendance.html',
        data=data
    )


# ================= CHECK IN =================

@app.route('/checkin')
@login_required
def checkin():

    attend = Attendance(

        user_id=session['user_id'],

        checkin=datetime.now()

    )

    db.session.add(attend)

    db.session.commit()

    flash("✅ Checked In")

    return redirect('/attendance')


# ================= CHECK OUT =================

@app.route('/checkout/<int:id>')
@login_required
def checkout(id):

    attend = Attendance.query.get(id)

    attend.checkout = datetime.now()

    total = attend.checkout - attend.checkin

    attend.working_hours = str(total)

    db.session.commit()

    flash("✅ Checked Out")

    return redirect('/attendance')

# ================= DASHBOARD =================

@app.route('/dashboard')
@login_required
def dashboard():

    filter_type = request.args.get('filter', 'daily')

    now = datetime.now(timezone.utc)

    # ================= FILTER =================

    if filter_type == 'daily':

        start_date = now - timedelta(days=1)

    elif filter_type == 'weekly':

        start_date = now - timedelta(days=7)

    else:

        start_date = now - timedelta(days=30)

    # ================= TASKS =================

    if session.get('role') == 'electrician':

        tasks = Task.query.filter_by(
            assigned_to=session.get('user_id')
        ).all()

    else:

        tasks = Task.query.all()

    # ================= COUNTS =================

    completed = Task.query.filter(
        Task.status == "Completed"
    ).count()

    pending = Task.query.filter(
        Task.status == "Pending"
    ).count()

    processing = Task.query.filter(
        Task.status == "Processing"
    ).count()

    total_users = User.query.filter_by(
        role='electrician'
    ).count()

    return render_template(

        'dashboard.html',

        tasks=tasks,

        completed=completed,

        pending=pending,

        processing=processing,

        total_users=total_users,

        filter_type=filter_type
    )

# ================= JOBS =================

@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def jobs():

    if request.method == 'POST':

        job = Job(

            title=request.form.get('title'),

            location=request.form.get('location')
        )

        db.session.add(job)

        db.session.commit()

        flash("✅ Job Added")

    jobs = Job.query.all()

    return render_template(
        'jobs.html',
        jobs=jobs
    )

# ================= EDIT JOB =================

@app.route('/edit_job/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):

    if session.get('role') != 'admin':

        return redirect('/dashboard')

    job = db.session.get(Job, id)

    if request.method == 'POST':

        job.title = request.form.get('title')

        job.location = request.form.get('location')

        db.session.commit()

        flash("✅ Job Updated")

        return redirect('/jobs')

    return render_template(
        'edit_job.html',
        job=job
    )

# ================= MATERIALS =================

@app.route('/materials', methods=['GET', 'POST'])
@login_required
def materials():

    # ================= ADD MATERIAL =================

    if request.method == 'POST':

        if session.get('role') != 'admin':

            flash("Only Admin Can Add Materials")

            return redirect('/materials')

        try:

            material = Material(

                name=request.form.get('name'),

                quantity=int(request.form.get('quantity')),

                cost=float(request.form.get('cost'))

            )

            db.session.add(material)

            db.session.commit()

            flash("✅ Material Added Successfully")

        except Exception as e:

            db.session.rollback()

            print("MATERIAL ERROR:", e)

            flash("❌ Material Add Failed")

    # ================= GET MATERIALS =================

    materials = Material.query.order_by(
        Material.id.desc()
    ).all()

    total_materials = len(materials)

    total_cost = sum(m.cost for m in materials)

    low_stock = Material.query.filter(
        Material.quantity < 5
    ).count()

    return render_template(

        'materials.html',

        materials=materials,

        total_materials=total_materials,

        total_cost=total_cost,

        low_stock=low_stock

    )

# ================= ELECTRICIANS =================

@app.route('/electricians')
@login_required
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
@login_required
def reports():

    tasks = Task.query.order_by(
        Task.id.desc()
    ).all()

    return render_template(
        'reports.html',
        tasks=tasks,
        filter_type="All"
    )


# ================= DAILY =================

@app.route('/daily')
@login_required
def daily():

    tasks = Task.query.all()

    return render_template(
        'reports.html',
        tasks=tasks,
        filter_type="Daily"
    )


# ================= WEEKLY =================

@app.route('/weekly')
@login_required
def weekly():

    tasks = Task.query.all()

    return render_template(
        'reports.html',
        tasks=tasks,
        filter_type="Weekly"
    )


# ================= MONTHLY =================

@app.route('/monthly')
@login_required
def monthly():

    tasks = Task.query.all()

    return render_template(
        'reports.html',
        tasks=tasks,
        filter_type="Monthly"
    )

# ================= PROFILE =================

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

    user = db.session.get(
        User,
        session.get('user_id')
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
@login_required
def edit_user(user_id):

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

        password = request.form.get('password')

        if password:

            user.password = generate_password_hash(password)

        file = request.files.get('profile_pic')

        if file and file.filename:

            user.profile_pic = base64.b64encode(
                file.read()
            ).decode('utf-8')

        db.session.commit()

        flash("✅ User Updated")

        return redirect('/electricians')

    return render_template(
        'edit_user.html',
        edit_user=user
    )

# ================= DELETE USER =================

@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):

    if session.get('role') != 'admin':

        return redirect('/dashboard')

    user = db.session.get(User, user_id)

    if not user:

        flash("User Not Found")

        return redirect('/electricians')

    if user.id == session.get('user_id'):

        flash("⚠️ Cannot delete yourself")

        return redirect('/electricians')

    try:

        db.session.delete(user)

        db.session.commit()

        flash("✅ User Deleted")

    except Exception as e:

        db.session.rollback()

        print(e)

        flash("❌ Delete Failed")

    return redirect('/electricians')

# ================= ADD TASK =================

@app.route('/add_task', methods=['GET', 'POST'])
@login_required
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

        flash("✅ Task Assigned")

        return redirect('/dashboard')

    return render_template(

        'add_task.html',

        electricians=electricians,

        jobs=jobs
    )

# ================= UPDATE TASK =================

@app.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):

    task = db.session.get(Task, id)

    if not task:

        flash("Task Not Found")

        return redirect('/dashboard')

    if session.get('role') != 'electrician':

        return redirect('/dashboard')

    if task.assigned_to != session.get('user_id'):

        flash("Unauthorized")

        return redirect('/dashboard')

    try:

        status = request.form.get('status')

        if status in [
            "Pending",
            "Processing",
            "Completed"
        ]:

            task.status = status

            if status == "Completed":

                task.completed_at = datetime.now(
                    timezone.utc
                )

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

        flash("✅ Task Updated")

    except Exception as e:

        db.session.rollback()

        print(e)

        flash("❌ Update Failed")

    return redirect('/dashboard')

# ================= DELETE TASK =================

@app.route('/delete_task/<int:id>')
@login_required
def delete_task(id):

    if session.get('role') != 'admin':

        return redirect('/dashboard')

    task = db.session.get(Task, id)

    if task:

        db.session.delete(task)

        db.session.commit()

        flash("✅ Task Deleted")

    return redirect('/dashboard')

# ================= PAYMENTS =================

@app.route('/payments', methods=['GET', 'POST'])
@login_required
def payments():

    if request.method == 'POST':

        amount = int(
            request.form.get('amount')
        )

        client_name = request.form.get('client_name')

        try:

            order = client.order.create({

                "amount": amount * 100,

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

            print(e)

            flash("❌ Payment Gateway Error")

            return redirect('/dashboard')

    return render_template('payments.html')

# ================= PAYMENT SUCCESS =================

@app.route('/payment_success')
@login_required
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

        print(e)

        flash("❌ Payment Failed")

    return redirect('/transactions')

# ================= PAY ELECTRICIAN =================

@app.route('/pay_electrician/<int:user_id>')
@login_required
def pay_electrician(user_id):

    if session.get('role') != 'admin':

        return redirect('/dashboard')

    electrician = db.session.get(User, user_id)

    if not electrician:

        flash("Electrician Not Found")

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

        flash(f"₹2000 Paid to {electrician.username}")

    except Exception as e:

        db.session.rollback()

        print(e)

        flash("❌ Payment Failed")

    return redirect('/electricians')

# ================= TRANSACTIONS =================

@app.route('/transactions')
@login_required
def transactions():

    try:

        data = Payment.query.order_by(
            Payment.id.desc()
        ).all()

        return render_template(
            'transaction_history.html',
            data=data
        )

    except Exception as e:

        print(e)

        flash("❌ Transaction Error")

        return redirect('/dashboard')

# ================= ELECTRICIAN PAYMENTS =================

@app.route('/electrician_payments')
@login_required
def electrician_payments():

    if session.get('role') != 'electrician':

        return redirect('/dashboard')

    try:

        payments = Payment.query.filter_by(
            receiver=session.get('username')
        ).order_by(
            Payment.id.desc()
        ).all()

        total = sum(
            p.amount for p in payments
        )

        return render_template(

            'electrician_payments.html',

            payments=payments,

            total=total
        )

    except Exception as e:

        print(e)

        flash("❌ Payment History Error")

        return redirect('/dashboard')

# ================= USER CONTEXT =================

@app.context_processor
def inject_user():

    if session.get('user_id'):

        user = db.session.get(
            User,
            session.get('user_id')
        )

        return dict(user=user)

    return dict(user=None)

# ================= BACKUP =================

@app.route('/backup')
@login_required
def backup():

    if session.get('role') != 'admin':

        return redirect('/dashboard')

    shutil.copy(

        'instance/electrician.db',

        'backup_electrician.db'
    )

    flash("✅ Backup Created")

    return redirect('/dashboard')

# ================= ERROR HANDLERS =================

@app.errorhandler(404)
def not_found(e):

    return render_template(

        'error.html',

        msg="404 Page Not Found"
    ), 404

@app.errorhandler(500)
def server_error(e):

    return render_template(

        'error.html',

        msg="500 Internal Server Error"
    ), 500
    
    

    
    #=====location======
@app.route('/location', methods=['GET', 'POST'])
@login_required
def location():

    if request.method == 'POST':

        lat = request.form.get('latitude')

        lon = request.form.get('longitude')

        loc = Location(

            user_id=session['user_id'],

            latitude=lat,

            longitude=lon,

            updated_at=datetime.now()

        )

        db.session.add(loc)

        db.session.commit()

        flash("📍 Location Updated")

    data = Location.query.order_by(
        Location.id.desc()
    ).all()

    return render_template(
        'location.html',
        data=data
    )
    
    #====pdf======
@app.route('/invoice/<int:id>')
@login_required
def invoice(id):

    job = db.session.get(Job, id)

    if not job:

        flash("Invoice Not Found")

        return redirect('/jobs')

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", size=18)

    pdf.cell(200, 10, txt="Electrician Invoice", ln=True)

    pdf.ln(10)

    pdf.set_font("Arial", size=14)

    pdf.cell(200, 10, txt=f"Job : {job.title}", ln=True)

    pdf.cell(200, 10, txt=f"Location : {job.location}", ln=True)

    pdf.cell(200, 10, txt=f"Generated : {datetime.now()}", ln=True)

    file_name = f"invoice_{id}.pdf"

    pdf.output(file_name)

    return send_file(file_name, as_attachment=True)

# ================= MATERIAL USAGE =================

@app.route('/material_usage', methods=['GET', 'POST'])
@login_required
def material_usage():

    if session.get('role') != 'admin':

        flash("Only Admin Allowed")

        return redirect('/dashboard')

    electricians = User.query.filter_by(
        role='electrician'
    ).all()

    materials = Material.query.all()

    if request.method == 'POST':

        electrician_id = request.form.get(
            'electrician_id'
        )

        material_id = request.form.get(
            'material_id'
        )

        used_quantity = int(
            request.form.get('used_quantity')
        )

        material = db.session.get(
            Material,
            material_id
        )

        # CHECK STOCK

        if used_quantity > material.quantity:

            flash("❌ Not Enough Stock")

            return redirect('/material_usage')

        # SAVE USAGE

        usage = MaterialUsage(

            electrician_id=electrician_id,

            material_id=material_id,

            used_quantity=used_quantity

        )

        # AUTO REDUCE STOCK

        material.quantity -= used_quantity

        db.session.add(usage)

        db.session.commit()

        flash("✅ Material Usage Saved")

        return redirect('/material_usage')

    usages = MaterialUsage.query.order_by(
        MaterialUsage.id.desc()
    ).all()

    return render_template(

        'material_usage.html',

        electricians=electricians,

        materials=materials,

        usages=usages

    )
    

# ================= LOGOUT =================

@app.route('/logout')
def logout():

    session.clear()

    flash("✅ Logged Out")

    return redirect('/login')

# ================= RUN =================

if __name__ == "__main__":
    socketio.run(app, debug=True)