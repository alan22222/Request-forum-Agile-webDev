from datetime import datetime
from os import makedirs, path

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_manager,
                         login_required, login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()
DB_NAME='database.db'
app = Flask(__name__)
app.secret_key = 'agile web dev'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    questions = db.relationship('Question', backref='author', lazy=True)
    # answers = db.relationship('Answer', backref='responder', lazy=True)
    answers = db.relationship('Answer', backref='author', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.String(10000), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answers = db.relationship('Answer', backref='question', lazy=True)
    categories = db.relationship('Category', secondary='question_categories', back_populates='questions')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    questions = db.relationship('Question', secondary='question_categories', back_populates='categories')

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(10000), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

question_categories = db.Table('question_categories',
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# with app.app_context():
#     db.create_all()

def create_database(app):
    db_path = path.join('website', DB_NAME)
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
            print('Created Database')
    else:
        print("already exixts")


login_manager=LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
# @login_required
def home():
    return render_template("home.html",user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')

        user=User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                flash('Logged in successfully',category='success')
                login_user(user,remember=True)
                return redirect(url_for('home'))
            else:
                flash('Incorrect password,try again',category='error')
        else:
            flash('Email does not exist',category='error')


    return render_template('login.html',user=current_user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user=User.query.filter_by(email=email).first()
        if user:
            flash('Email alreay exist',category='error')

        elif len(username) < 4:
            flash("Username must be greater than 4 characters.", category='error')
        elif len(email) < 4:
            flash("Email must be greater than 4 characters.", category='error')
        elif len(password) < 7:
            flash("Password is short, must be greater than 7 characters", category='error')
        else:

            new_user=User(username=username,email=email, password= generate_password_hash(password))#sqlmodel=form name
            db.session.add(new_user)
            db.session.commit()
            login_user(user,remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/category', methods=['GET','POST'])
def category():
    if request.method == 'POST':
        title = request.form.get('title')
        if title:  
            new_category = Category(title=title)
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!','success')
            return redirect(url_for('home'))  
        else:
            flash('The title  is required.','error')

    return render_template('category.html')




@app.route('/question', methods=['GET', 'POST'])
def question():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        category_ids = request.form.getlist('category')  # This should be the name of the input field for categories in your form.

        if not title or not body:
            flash('both title and body are required.', 'error')
            return redirect(url_for('question'))

        new_question = Question(title=title, body=body, user_id=current_user.id)
        db.session.add(new_question)
        db.session.flush()  # Ensure 'id' is available if needed before commit for newly created question.

        # Handle categories
        if category_ids:
            categories = Category.query.filter(Category.id.in_(category_ids)).all()
            new_question.categories.extend(categories)
        
        db.session.commit()
        flash('Question submitted successfully!', 'success')
        return redirect(url_for('home'))

    categories = Category.query.all()
    return render_template('questiontemplate.html', categories=categories)


@app.route('/feed', methods=['GET', 'POST'])
def feed():
    questions = Question.query.all() 
    return render_template('feed.html', questions=questions)

# @app.route('/question/<int:question_id>', methods=['GET', 'POST'])
# def question_details(question_id):
#     question = Question.query.get_or_404(question_id)
#     answers = Answer.query.filter_by(question_id=question_id).all()
#     return render_template('question_details.html', question=question, answers=answers)

    

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question_details(question_id):
    question = Question.query.get_or_404(question_id)  # Move this up to use in POST
    if request.method == 'POST':
        body = request.form.get('answer')  # Make sure to get 'answer', not 'body' if your form uses 'answer'
        if not body:
            flash('Your answer cannot be empty.', 'error')
            return redirect(url_for('question_details', question_id=question_id))
        
        new_answer = Answer(body=body, user_id=current_user.id, question_id=question_id)
        db.session.add(new_answer)
        db.session.commit()
        flash('Answer submitted successfully!', 'success')
        return redirect(url_for('question_details', question_id=question_id))

    answers = Answer.query.filter_by(question_id=question_id).all()
    return render_template('question_details.html', question=question, answers=answers)

# chtgpt code
# @app.route('/question/<int:question_id>', methods=['GET', 'POST'])
# def question_details(question_id):
#     if request.method == 'POST':
#         body = request.form.get('answer')  # Make sure to get 'answer', not 'body' if your form uses 'answer'
#         if not body:
#             flash('Your answer cannot be empty.', 'error')
#             return redirect(url_for('question_details', question_id=question_id))
        
#         new_answer = Answer(body=body, user_id=current_user.id, question_id=question_id)
#         db.session.add(new_answer)
#         db.session.commit()
#         flash('Answer submitted successfully!', 'success')
#         return redirect(url_for('question_details', question_id=question_id))

#     answers = Answer.query.filter_by(question_id=question_id).all()
#     return render_template('question_details.html', question=question, answers=answers)




if __name__ == '__main__':
    create_database(app)
    app.run(debug=True)
