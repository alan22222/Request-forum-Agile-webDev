# app.py
from auth import login as auth_login
from auth import logout as auth_logout
from auth import signup as auth_signup
from database import create_database
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from models import Answer, Category, Question, User, db, question_categories

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
# Authorisation Routes

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Login route implementation
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        return auth_login(email, password)
    return render_template('login.html', user=current_user)

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Signup route implementation
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        return auth_signup(username, email, password)
    return render_template('signup.html', user=current_user)

# Logout Redirect
@app.route('/logout')
@login_required
def logout():
    # Logout route implementation
    return auth_logout()

# Content Routes

# Combined Category Creation and Post Submission Page
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
         # If the form is submitted for creating a new category
        if 'new_category' in request.form:
            title = request.form.get('title')
            if title:
                # Filter Duplicate Fields
                category_exists = Category.query.filter_by(title = title).first()
                if category_exists:
                    flash('Category already exists', 'error')
                    # Redirect to the same page to clear form data and refresh
                    return redirect(url_for('create'))
                else:
                    new_category = Category(title=title)
                    db.session.add(new_category)
                    db.session.commit()
                    flash('Category added successfully!', 'success')

                    # Redirect to the same page to clear form data and refresh
                    return redirect(url_for('create'))
            else:
                flash('The title is required.', 'error')
                # Redirect to the same page to clear form data and refresh
                return redirect(url_for('create'))
            
        # If the form is submitted for posting a new question
        elif 'new_question' in request.form:
            title = request.form.get('title')
            body = request.form.get('body')
            category_ids = request.form.getlist('category')

            if not title or not body:
                flash('Both title and body are required.', 'error')
                # Redirect to the same page to clear form data and refresh
                return redirect(url_for('create'))
            else:
                new_question = Question(title=title, body=body, user_id=current_user.id)
                db.session.add(new_question)
                db.session.flush()

                if category_ids:
                    categories = Category.query.filter(Category.id.in_(category_ids)).all()
                    new_question.categories.extend(categories)

                db.session.commit()
                flash('Question submitted successfully!', 'success')

                # Redirect to the feed page
                return redirect(url_for('feed'))
            
    categories = Category.query.all()
    return render_template('create.html', categories=categories, user=current_user)

# Feed View Page
@app.route('/feed', methods=['GET', 'POST'])
def feed():
    # Feed route implementation
    categories = Category.query.all() # Fetch all categories from the database

    category_filter = request.args.get('category') # Get category filter from query parameters
    sort = request.args.get('sort') # Get sort parameter from query parameters

    questions = Question.query

    if category_filter: # Filter questions based on the specified category
        questions = Question.query.join(Question.categories).filter(Category.title == category_filter)
    else:
        category_filter = ""

    if sort == 'newest':
        questions = questions.order_by(Question.id.desc())  # Sort by newest
    elif sort == 'oldest':
        questions = questions.order_by(Question.id)  # Sort by oldest
    else:
        questions = questions.order_by(Question.id.desc())  # Sort by newest DEFAULT

    questions = questions.all()

    return render_template('feed.html', categories=categories, questions=questions, user=current_user, category_set=category_filter)

# Post Detail Page
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

# Profile User Page
@app.route('/userprofile/<int:profile_id>', methods=['GET','POST'])
@login_required
def profile(profile_id):
    profile_user = User.query.get(profile_id)
    if not profile_user:
        flash('User not found.', 'error')
        return redirect(url_for('home'))
    
    posts = Question.query.filter_by(user_id=profile_user.id).all()
    comments = Answer.query.filter_by(user_id=profile_user.id).all()
    
    return render_template('userprofile.html', user=current_user, profile_user=profile_user, posts=posts, comments=comments)


if __name__ == '__main__':
    before_request_func()
    app.run(debug=True)
