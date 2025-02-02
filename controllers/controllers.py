from model.model import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for, flash, session, Blueprint
from datetime import datetime

controllers = Blueprint('controllers', __name__)

@controllers.route('/')
def home():
    return render_template('admin_login.html')

@controllers.route('/admin/quiz_management', methods = ['get', 'post'])
def admin_quiz_management():
    
    subjects = Subject.query.all()  # Fetch all subjects for the dashboard
    chapters = Chapter.query.all()  # Fetch all chapters
    quizzes = Quiz.query.all()  # Fetch all quizzes
    questions = Question.query.all()  # Fetch all questions
    return render_template('admin_dashboard_1.html', subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions)

# Admin login
@controllers.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, roles='Admin').first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['role'] = user.roles
            flash("Admin login successful!")
            return redirect(url_for('controllers.admin_dashboard'))
        else:
            flash("Invalid admin credentials. Please try again.")
    return render_template('admin_login.html')

# User login
@controllers.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.roles
            flash("Login successful!")
            if user.roles == 'Admin':
                return redirect(url_for('controllers.admin_dashboard'))
            return redirect(url_for('controllers.user_dashboard'))
        else:
            flash("Invalid login credentials. Please try again.")
    return render_template('user_login.html')

# User registration
@controllers.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please use another email.")
            return redirect(url_for('controllers.register'))

        new_user = User(username=username, email=email, password=password, roles='student')
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for('controllers.login'))
    return render_template('user_register.html')

# User dashboard
@controllers.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('controllers.login'))
    return render_template('user_dashboard.html')




# Admin dashboard
@controllers.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'Admin':
        flash('Unauthorized access.')
        return redirect(url_for('controllers.admin_login'))
    
    users = User.query.all()  # Fetch all users for the dashboard
    subjects = Subject.query.all()  # Fetch all subjects for the dashboard
    chapters = Chapter.query.all()  # Fetch all chapters
    quizzes = Quiz.query.all()  # Fetch all quizzes
    questions = Question.query.all()  # Fetch all questions
    return render_template('admin_dashboard.html', users=users, subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions)








# CRUD operations for Subjects
@controllers.route('/create_subject', methods=['GET', 'POST'])
def create_subject():
    if request.method == 'POST':
            
        sname = request.form['sname']
        desc = request.form['desc']
        new_subject = Subject(name=sname , description = desc)
        
        db.session.add(new_subject) # add both together always!!
        
        db.session.commit()
        flash("Subject created successfully!")
        return redirect(url_for('controllers.admin_quiz_management'))
    return render_template('create_subject.html')

@controllers.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        subject.name = request.form['sname']
        subject.description = request.form['desc']
        db.session.commit()
        flash("Subject updated successfully!")
        return redirect(url_for('controllers.admin_quiz_management'))
    return render_template('edit_subject.html', subject=subject)

@controllers.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully!")
    return redirect(url_for('controllers.admin_quiz_management'))







# CRUD operations for Chapters
@controllers.route('/create_chapter/<int:subject_id>', methods=['GET', 'POST'])
def create_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        cname = request.form['cname']
        
        desc = request.form['desc']
        new_chapter = Chapter(name=cname, subject_id=subject_id, description=desc)
        db.session.add(new_chapter)
        db.session.commit()
        flash("Chapter created successfully!")
        return redirect(url_for('controllers.admin_quiz_management'))
    #subjects = Subject.query.all()
    return render_template('create_chapter.html', subject=subject)

@controllers.route('/edit_chapter/<int:chapter_id>/<int:subject_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id, subject_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        chapter.name = request.form['cname']
        chapter.description = request.form['desc']
        #chapter.subject_id = request.form['subject_id']
        db.session.commit()
        flash("Chapter updated successfully!")
        return redirect(url_for('controllers.admin_quiz_management'))
    #subjects = Subject.query.all()
    return render_template('edit_chapter.html', chapter=chapter, subject=subject)

@controllers.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!")
    return redirect(url_for('controllers.admin_quiz_management'))




@controllers.route('/admin/quizzes', methods = ['get', 'post'])
def admin_quizzes():
    subjects = Subject.query.all()  # Fetch all subjects for the dashboard
    chapters = Chapter.query.all()  # Fetch all chapters
    quizzes = Quiz.query.all()  # Fetch all quizzes
    questions = Question.query.all()  # Fetch all questions
    return render_template('admin_dashboard_quiz.html', subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions)


# CRUD operations for Quizzes (MILESTONE - 3)
@controllers.route('/create_quiz/<int:chapter_id>/<int:subject_id>', methods=['GET', 'POST'])
def create_quiz(chapter_id, subject_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        title = request.form['qname']
        date = request.form['qdate']
        duration = request.form['qduration']
        rules = request.form['qrules']
        time = request.form['qtime']
        
        try:
            date = datetime.strptime(date, "%Y-%m-%d").date() # AS  SQLite Date type only accepts Python date objects as input.
            time = datetime.strptime(time, "%H:%M").time()
        except ValueError:
            flash("Invalid date format!", "error")
            return redirect(url_for('controllers.create_quiz', chapter_id=chapter_id, subject_id=subject_id))

        
        #chapter_id = request.form['chapter_id']
        new_quiz = Quiz(title=title, chapter_id=chapter_id, date = date, time = time, duration = duration, rules = rules)
        db.session.add(new_quiz)
        db.session.commit()
        flash("Quiz created successfully!")
        return redirect(url_for('controllers.admin_quizzes'))
    #chapters = Chapter.query.all()
    return render_template('create_quiz.html', chapter=chapter, subject=subject)

# Edit a Quiz (MILESTONE - 3)
@controllers.route('/edit_quiz/<int:quiz_id>/<int:chapter_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id, chapter_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter = Chapter.query.get_or_404(chapter_id)
    #subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        quiz.title = request.form['qname']
        #quiz.chapter_id = request.form['chapter_id']
        date = request.form['qdate']
        quiz.duration = request.form['qduration']
        quiz.rules = request.form['qrules']
        time = request.form['qtime']
        
        try:
            quiz.date = datetime.strptime(date, "%Y-%m-%d").date() # AS  SQLite Date type only accepts Python date objects as input.
            quiz.time = datetime.strptime(time, "%H:%M").time()
        except ValueError:
            flash("Invalid date or time format!", "error")
            return redirect(url_for('controllers.edit_quiz',quiz_id = quiz_id, chapter_id=chapter_id))
        
        
        
        
        db.session.commit()
        flash("Quiz updated successfully!")
        return redirect(url_for('controllers.admin_quizzes'))
    
    #chapters = Chapter.query.all()
    return render_template('edit_quiz.html', quiz=quiz, chapter=chapter)

# Delete a Quiz (MILESTONE - 3)
@controllers.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully!")
    return redirect(url_for('controllers.admin_quizzes'))








# CRUD operations for Questions (MILESTONE - 3)
@controllers.route('/create_question/<int:quiz_id>/<int:chapter_id>', methods=['GET', 'POST'])
def create_question(quiz_id, chapter_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter = Chapter.query.get_or_404(chapter_id)
    
    last_question = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.id.desc()).first()
    next_question_number = 1 if last_question is None else last_question.id + 1
    
    if request.method == 'POST':
        #qid = request.form['qid']
        qtitle = request.form['qtitle']
        qstatement = request.form['qstatement']
        
        op_a = request.form['op1']
        op_b = request.form['op2']
        op_c = request.form['op3']
        op_d = request.form['op4']
        
        cop = request.form['cop']
       
        new_question = Question(id = next_question_number, title=qtitle, statement=qstatement, option_a = op_a, option_b = op_b, option_c = op_c, option_d = op_d, correct_option = cop,quiz_id = quiz_id)
        db.session.add(new_question)
        db.session.commit()
        
        flash("Question created successfully!")
        return redirect(url_for('controllers.admin_quizzes'))
    
    #quizzes = Quiz.query.all()
    return render_template('create_question.html', quiz=quiz, chapter= chapter)

# Editing a question (MILESTONE - 3)

@controllers.route('/edit_question/<int:question_id>/<int:quiz_id>', methods=['GET', 'POST'])
def edit_question(question_id,quiz_id):
    
    question = Question.query.get_or_404((question_id, quiz_id)) #SINCE COMPOSITE KEY PASS AS TUPLE
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        question.title = request.form['qtitle']
        
        question.statement = request.form['qstatement']
        
        question.option_a = request.form['op1']
        question.option_b = request.form['op2']
        question.option_c = request.form['op3']
        question.option_d = request.form['op4']
        
        question.correct_option = request.form['cop']
        
        
        
        db.session.commit()
        
        flash("Question updated successfully!")
        return redirect(url_for('controllers.admin_quizzes'))
    
    #quizzes = Quiz.query.all()
    return render_template('edit_question.html', question=question, quiz=quiz)


# Deleting a question (MILESTONE - 3)
@controllers.route('/delete_question/<int:question_id>/<int:quiz_id>', methods=['POST'])
def delete_question(question_id,quiz_id):
    question = Question.query.get_or_404((question_id, quiz_id)) #SINCE COMPOSITE KEY PASS AS TUPLE
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully!")
    return redirect(url_for('controllers.admin_quizzes'))








# Block a user (MILESTONE - 3)
@controllers.route('/block/<int:user_id>', methods=['POST'])
def block_user(user_id):
    if 'user_id' not in session or session.get('role') != 'Admin':
        flash("Unauthorized access.")
        return redirect(url_for('controllers.admin_login'))
    
    user = User.query.get(user_id)
    if user and user.roles != 'Admin':  # Can't block an admin!!
        user.roles = 'blocked'  # Changes the user from 'student' to 'blocked'
        db.session.commit()
        flash(f"User '{user.username}' has been blocked.")
    else:
        flash("Admin cant be blocked.")
    
    return redirect(url_for('controllers.admin_dashboard'))

# Unblock a user (MILESTONE - 3)
@controllers.route('/unblock/<int:user_id>', methods=['POST'])
def unblock_user(user_id):
    if 'user_id' not in session or session.get('role') != 'Admin':
        flash("Unauthorized access.")
        return redirect(url_for('controllers.admin_login'))
    
    user = User.query.get(user_id)
    if user and user.roles == 'blocked':  # Only unblocking blocked users
        user.roles = 'student'  # Restore original role, assuming default is 'student'
        db.session.commit()
        flash(f"User '{user.username}' has been unblocked.")
    else:
        flash("Admin cant be unblocked.")
    
    return redirect(url_for('controllers.admin_dashboard'))










# Search functionality (MILESTONE - 3)
@controllers.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
    subjects = Subject.query.filter(Subject.name.like(f'%{query}%')).all() # Fetching all records from the subject db
    chapters = Chapter.query.filter(Chapter.name.like(f'%{query}%')).all()
    quizzes = Quiz.query.filter(Quiz.name.like(f'%{query}%')).all()
    questions = Question.query.filter(Question.text.like(f'%{query}%')).all()
    return render_template('search.html', subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions)






# Logout
@controllers.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('controllers.admin_login'))
