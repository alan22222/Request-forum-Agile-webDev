# app.py
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import db, User, Question, Category, Answer, question_categories
from database import create_database
from auth import login as auth_login, signup as auth_signup, logout as auth_logout

app = Flask(__name__)
app.secret_key = 'agile web dev'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Create database before the Flask app starts
@app.before_request
def before_request_func():
    with app.app_context():
        create_database(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def home():
    return render_template("home.html", user=current_user)

# Other routes

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Login route implementation
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        return auth_login(email, password)
    return render_template('login.html', user=current_user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Signup route implementation
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        return auth_signup(username, email, password)
    return render_template('signup.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    # Logout route implementation
    return auth_logout()

@app.route('/category', methods=['GET', 'POST'])
def category():
    # Category route implementation
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

    return render_template('category.html',user=current_user)

@app.route('/question', methods=['GET', 'POST'])
def question():
    # Question route implementation
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
    return render_template('questiontemplate.html', categories=categories,user=current_user)


@app.route('/feed', methods=['GET', 'POST'])
def feed():
    # Feed route implementation
    questions = Question.query.all() 
    return render_template('feed.html', questions=questions,user=current_user)


@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question_details(question_id):
    # Question details route implementation
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
        return redirect(url_for('question_details', question_id=question_id, user=current_user))

    answers = Answer.query.filter_by(question_id=question_id).all()
    return render_template('question_details.html', question=question, answers=answers, user=current_user)


if __name__ == '__main__':
    create_database(app)
    app.run(debug=True)
