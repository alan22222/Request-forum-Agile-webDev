# auth.py
from flask import flash, redirect, render_template, request, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User

login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def login(email, password):
    user = User.query.filter_by(email=email).first()
    if user:
        if check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash('Logged in successfully', category='success')
            return redirect(url_for('home'))
        else:
            flash('Incorrect password, try again', category='error')
    else:
        flash('Email does not exist', category='error')
    return render_template('login.html', user=current_user)

def signup(username, email, password):
    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email already exists', category='error')
    elif len(username) < 4:
        flash('Username must be greater than 4 characters.', category='error')
    elif len(email) < 4:
        flash('Email must be greater than 4 characters.', category='error')
    elif len(password) < 7:
        flash('Password is short, must be greater than 7 characters', category='error')
    else:
        new_user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        flash('Account created!', category='success')
        return redirect(url_for('home'))
    return render_template('signup.html', user=current_user)

@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

