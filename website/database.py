# database.py
from os import path, makedirs
from flask import Flask

from models import db

def create_database(app):
    # Create file instances directory if it doesn't exist
    instances_dir = path.join(app.root_path, 'instance')
    db_path = path.join(app.root_path, 'instance/database.db')

    if not path.exists(instances_dir):
        makedirs(instances_dir)
        print('Created instances directory')

        # Create database file if it doesn't exist
        if not path.exists(db_path):
            with open(db_path, 'w'):
                db.create_all()
                pass  # Create an empty file
            print('Created Database')
    elif path.exists(instances_dir):
        # Create database file if it doesn't exist
        if not path.exists(db_path):
            with open(db_path, 'w'):
                db.create_all()
                pass  # Create an empty file
            print('Created Database')