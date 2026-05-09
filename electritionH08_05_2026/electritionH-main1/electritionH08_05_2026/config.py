class Config:

    SECRET_KEY = "supersecretkey"

    SQLALCHEMY_DATABASE_URI = "sqlite:///electrician.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "static/uploads"

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # ================= RAZORPAY =================

    RAZORPAY_KEY_ID = "rzp_live_SnEyLRRXXElOT0"

    RAZORPAY_KEY_SECRET = "j2lyqAtl1YpRutK92q18H69X"