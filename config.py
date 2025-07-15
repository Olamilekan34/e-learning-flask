# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:lekan123@localhost/elearning_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'a7d11f9fcb14e359a348fa8b15ea021c60b90618af85c5dacb98544bc5e21f03'