import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    MAIL_SERVER = 'smtp.gmail.com'


    SQLALCHEMY_TRACK_MODIFICATIONS = False


