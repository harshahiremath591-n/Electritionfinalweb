import os
from datetime import timedelta

class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "supersecret"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///electrician.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "static/uploads"

    REMEMBER_COOKIE_DURATION = timedelta(days=3650)

    PERMANENT_SESSION_LIFETIME = timedelta(days=3650)

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = False

    RAZORPAY_KEY_ID = "rzp_live_SnEyLRRXXElOT0"

    RAZORPAY_KEY_SECRET = "j2lyqAtl1YpRutK92q18H69X"