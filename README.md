# ⚡ Electrician Management System

An advanced Flask-based Electrician Management System with Admin and Electrician panels, task management, attendance, GPS location tracking, PDF invoice generation, analytics dashboard, payment system, and material inventory management.

---

# 🚀 FEATURES

| Module                     | Status      |
| -------------------------- | ----------- |
| 🔐 Login/Register          | ✅ Completed |
| 👤 Profile Management      | ✅ Completed |
| 📋 Task Assignment         | ✅ Completed |
| 👷 Electrician Panel       | ✅ Completed |
| 📦 Materials Management    | ✅ Completed |
| 📦 Material Usage Tracking | ✅ Completed |
| 💳 Payment System          | ✅ Completed |
| 📊 Reports Dashboard       | ✅ Completed |
| 📍 GPS Location Tracking   | ✅ Completed |
| 🧾 PDF Invoice Generator   | ✅ Completed |
| 👷 Attendance System       | ✅ Completed |
| 🔔 Live Dashboard Refresh  | ✅ Completed |
| 📈 Analytics Charts        | ✅ Completed |

---

# 🛠 TECHNOLOGIES USED

* Python
* Flask
* SQLite
* HTML5
* CSS3
* JavaScript
* Chart.js
* Razorpay
* Flask-SocketIO
* FPDF

---

# 📂 PROJECT STRUCTURE

```bash
project/
│
├── app.py
├── models.py
├── config.py
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── jobs.html
│   ├── materials.html
│   ├── material_usage.html
│   ├── attendance.html
│   ├── location.html
│   ├── reports.html
│   ├── invoice.html
│   └── ...
│
├── static/
│   ├── style.css
│   └── uploads/
│
└── instance/
    └── electrician.db
```

---

# 👨‍💼 ADMIN WORKFLOW

## 🔐 STEP 1 — ADMIN REGISTER

Open:

```bash
/register
```

Fill:

| Field    | Example  |
| -------- | -------- |
| Username | admin    |  #Any name
| Password | admin123 |  #Any password
| Role     | admin    |

Click Register.

---

## 🔑 STEP 2 — ADMIN LOGIN

Open:

```bash
/login
```

Enter:

| Field    | Example  |
| -------- | -------- |
| Username | admin    |
| Password | admin123 |

---

## 📊 STEP 3 — ADMIN DASHBOARD

Admin Dashboard includes:

| Panel              | Work                  |
| ------------------ | --------------------- |
| ✅ Completed        | Total completed tasks |
| ⏳ Pending          | Pending tasks         |
| 🔄 Processing      | Processing tasks      |
| 👷 Electricians    | Total workers         |
| 📊 Analytics Chart | Task statistics       |
| 📍 Live Location   | GPS coordinates       |
| 📋 Task History    | All task reports      |

---

## 🛠 STEP 4 — ADMIN CONTROLS

| Button            | Purpose               |
| ----------------- | --------------------- |
| ➕ Assign Task     | Create tasks          |
| 🏗 Jobs           | Add jobs              |
| 📦 Materials      | Manage inventory      |
| 👷 Electricians   | Manage workers        |
| 💳 Payments       | Client payment system |
| 📜 Transactions   | Payment history       |
| 📊 Reports        | Task reports          |
| 📦 Material Usage | Stock tracking        |
| 📍 Location       | GPS location tracking |
| 👷 Attendance     | Worker attendance     |

---

## 📋 STEP 5 — ADD JOB

Open:

```bash
/jobs
```

Example:

| Field     | Example      |
| --------- | ------------ |
| Job Title | House Wiring |
| Location  | Bangalore    |

---

## 👷 STEP 6 — REGISTER ELECTRICIAN

Open:

```bash
/register
```

| Field    | Example     |
| -------- | ----------- |
| Username | Ravi        |
| Password | ravi123     |
| Role     | electrician |

---

## 📌 STEP 7 — ASSIGN TASK

Open:

```bash
/add_task
```

| Field       | Example      |
| ----------- | ------------ |
| Task Title  | Main Wiring  |
| Electrician | Ravi         |
| Job         | House Wiring |

---

## 📦 STEP 8 — ADD MATERIALS

Open:

```bash
/materials
```

| Material | Qty | Cost |
| -------- | --- | ---- |
| Wire     | 50  | 100  |
| Switch   | 20  | 50   |

---

## 📦 STEP 9 — MATERIAL USAGE TRACKING

Open:

```bash
/material_usage
```

| Field         | Example |
| ------------- | ------- |
| Electrician   | Ravi    |
| Material      | Wire    |
| Quantity Used | 10      |

Stock reduces automatically.

---

## 👷 STEP 10 — ATTENDANCE SYSTEM

Open:

```bash
/attendance
```

Admin can monitor:

* Check-in
* Check-out
* Working hours
* Daily attendance reports

---

## 📍 STEP 11 — GPS LOCATION TRACKING

Open:

```bash
/location
```

Shows:

* Latitude
* Longitude
* Updated time

---

## 💳 STEP 12 — CLIENT PAYMENTS

Open:

```bash
/payments
```

| Field       | Example |
| ----------- | ------- |
| Client Name | Harsha  |
| Amount      | 5000    |

---

## 📜 STEP 13 — TRANSACTION HISTORY

Open:

```bash
/transactions
```

Displays:

* Payer
* Receiver
* Amount
* Status
* Date

---

## 🧾 STEP 14 — DOWNLOAD PDF INVOICE

Open:

```bash
/jobs
```

Click:

```text
🧾 Download Invoice
```

Invoice contains:

* Job Name
* Location
* Date
* Invoice Summary

---

## 📊 STEP 15 — REPORTS

Open:

```bash
/reports
```

Shows:

* Completed Tasks
* Pending Tasks
* Processing Tasks
* Uploaded Reports

---

## 🔓 STEP 16 — LOGOUT

Click Logout to end session.

---

# 👷 ELECTRICIAN WORKFLOW

## 🔐 STEP 1 — ELECTRICIAN LOGIN

Open:

```bash
/login
```

| Field    | Example |
| -------- | ------- |
| Username | Ravi    |
| Password | ravi123 |

---

## 🧰 STEP 2 — ELECTRICIAN DASHBOARD

| Panel           | Purpose           |
| --------------- | ----------------- |
| 🧰 My Tasks     | Assigned tasks    |
| 📍 GPS Location | Current location  |
| 📄 Reports      | Uploaded reports  |
| 📊 Status       | Pending/Completed |

---

## 📋 STEP 3 — VIEW TASKS

Electrician can view:

* Task name
* Created date
* Status
* Reports

---

## 🔄 STEP 4 — UPDATE TASK STATUS

Status options:

* Pending
* Processing
* Completed

---

## 📄 STEP 5 — UPLOAD REPORT

Supported uploads:

* PDF
* Images
* Task Reports

---

## 👷 STEP 6 — CHECK-IN

Open:

```bash
/checkin
```

Attendance starts automatically.

---

## 👷 STEP 7 — CHECK-OUT

Open:

```bash
/checkout/id
```

Working hours are calculated automatically.

---

## 📍 STEP 8 — SHARE LOCATION

Browser asks:

```text
Allow Location?
```

Electrician clicks Allow.

Admin receives live coordinates.

---

## 💰 STEP 9 — VIEW SALARY PAYMENTS

Open:

```bash
/electrician_payments
```

Displays:

* Salary payments
* Payment status
* Transactions

---

## 🔓 STEP 10 — LOGOUT

Click Logout.

---

# 📊 SYSTEM FLOW

```text
Admin Login
   ↓
Create Job
   ↓
Register Electrician
   ↓
Assign Task
   ↓
Add Materials
   ↓
Track Usage
   ↓
Electrician Updates Task
   ↓
Upload Report
   ↓
Admin Checks Reports
   ↓
Generate Invoice
   ↓
Payment
   ↓
Logout
```

---

# ⚙️ INSTALLATION

## 1️⃣ Clone Repository

```bash
git clone https://github.com/harshahiremath591-n/Electritionfinalweb.git
```

---

## 2️⃣ Install Requirements

```bash
pip install flask
pip install flask_sqlalchemy
pip install flask_socketio
pip install razorpay
pip install fpdf
```

---

## 3️⃣ Run Application

```bash
python app.py
```

---

# ☁️ FUTURE UPGRADES

| Feature                 | Future                |
| ----------------------- | --------------------- |
| 🔔 Socket Notifications | Live alerts           |
| ☁️ Deploy Online        | Mobile access         |
| 🤖 AI Auto Assignment   | Smart task management |
| 📱 Mobile App UI        | PWA support           |
| 🛰 Google Maps          | Live map tracking     |
| 🔐 OTP Login            | Advanced security     |

---

# 👨‍💻 DEVELOPED BY

Harsha Hiremath
