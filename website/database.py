# database.py
from os import path
from flask import Flask

from models import db

def create_database(app):
    # Function to create database
    db_path = path.join(app.root_path, 'database.db')
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
            print('Created Database')
    else:
        print("already exixts")