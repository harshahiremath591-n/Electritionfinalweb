import os

class Config:

    # ================= SECRET =================

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "supersecret"
    )

    # ================= DATABASE =================

    SQLALCHEMY_DATABASE_URI = "sqlite:///electrician.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ================= UPLOADS =================

    UPLOAD_FOLDER = "static/uploads"

    # ================= RAZORPAY =================

    RAZORPAY_KEY_ID = "rzp_live_SnEyLRRXXElOT0"

    RAZORPAY_KEY_SECRET = "j2lyqAtl1YpRutK92q18H69X"