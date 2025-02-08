from model.model import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for, flash, session, Blueprint
from datetime import datetime, timedelta, timezone


controllers = Blueprint('controllers', __name__)

@controllers.route('/')
def home():
    return render_template('admin_login.html')

@controllers.route('/admin/quiz_management', methods = ['get', 'post'])
def admin_quiz_management():
    
    search_query = request.args.get('search', '').strip()  # Get search query from URL
    
    if search_query:
        subjects = Subject.query.filter(Subject.name.ilike(f"%{search_query}%")).all()  # Case-insensitive search
    else:
        subjects = Subject.query.all()  # Fetch all subjects for the dashboard
    
    
    chapters = Chapter.query.all()  # Fetch all chapters
    quizzes = Quiz.query.all()  # Fetch all quizzes
    questions = Question.query.all()  # Fetch all questions
    return render_template('admin_dashboard_1.html', subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions , search_query=search_query)

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
        
        if user.roles == 'blocked' :
            flash('You have been Blocked. Contact your administrator for more information.')
            return redirect(url_for('controllers.login'))
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.roles
            flash("Login successful!") # Oncce we add the toast in user_dashboard it will reflect there only
            if user.roles == 'Admin':
                return redirect(url_for('controllers.admin_dashboard'))
            flash('Welcome to the Quiz Master platform')
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

        existing_user_email = User.query.filter_by(email=email).first()
        existing_user_username = User.query.filter_by(username=username).first()
        if existing_user_email:
            flash("Email already registered. Please use another email.")
            return redirect(url_for('controllers.register'))
        if existing_user_username:
            flash("Username already registered. Please use another username.")
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
    if 'user_id' not in session :
        flash('Please log in to access the dashboard.')
        return redirect(url_for('controllers.login'))
    
    #quizzes = Quiz.query.all()  
    
    search_query = request.args.get('search_sub', '').strip()  # Get search query from URL
    
    if search_query:
        subjects = Subject.query.filter(Subject.name.ilike(f"%{search_query}%")).all()  # Case-insensitive search
    else:
        subjects = Subject.query.all()  # Fetch all subjects for the dashboard
    
    #subjects = Subject.query.all()  # Fetch all subjects for the dashboard (ALL SUBJECTS ALSO)
    #user_id = session['user_id']
    user = User.query.get(session['user_id'])
    
    search_query_1 = request.args.get('search_quiz', '').strip()  # Get search query from URL
    
    if search_query_1:
        quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{search_query_1}%")).all()  # Case-insensitive search
    else:
        quizzes = Quiz.query.all()  # Fetch all quizzes
    
    
    
    current_time = datetime.now()
    
    upcoming_quizzes = [] #for now the quizzes will go away automically when the time has expired, not interfering with "if attmepted then disappear".
    for quiz in quizzes:
        if quiz.date and quiz.time:  # Ensure both date and time exist
            quiz_datetime = datetime.combine(quiz.date, quiz.time)  # Merge date and time (EXTERNAL SOURCE)
            if quiz_datetime >= current_time:  # Only show upcoming quizzes
                upcoming_quizzes.append(quiz)
                
    # Fetch quizzes assigned to the user's subjects
    #user_quizzes = Quiz.query.join(Chapter).join(Subject).filter(Subject.id == Chapter.subject_id).all()
    # if 'username' not in session:
    #     return redirect(url_for('controllers.login'))  # Redirect to login if not logged in

    #username = session['username']  # Retrieve username from session
    
    return render_template('user_dashboard.html', user=user, quizzes=upcoming_quizzes, subjects = subjects , search_query=search_query , search_query_1=search_query_1)
    
    
    

    
@controllers.route('/start_quiz/<int:quiz_id>')
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    user_id1 = session.get("user_id") 
    
    existing_score = Score.query.filter_by(user_id=user_id1, quiz_id=quiz_id).first() 
    if existing_score:   # else if u try giving the quiz again it willa add another record which shldnt happen as onyl 1 chance shld be given
                         # basically u can't use the submit button again to add anything
        flash("Quiz already attempted!!")
        return redirect(url_for("controllers.user_dashboard"))
    
    if not quiz:
        flash("Quiz not found.", "danger")
        return redirect(url_for('user_dashboard'))

    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if not questions:  
        flash("No questions available!! Contact your administrator for more information.")
        return redirect(url_for('controllers.user_dashboard'))
    
    # Get quiz duration from the database (converting to seconds)
    duration_seconds = quiz.duration * 60  

    # Set quiz start time and end time in session
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=duration_seconds)
    
    session["quiz_start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
    session["quiz_end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
    session["quiz_id"] = quiz_id  
    session["current_question"] = 0  # Start from the first question

    return redirect(url_for("controllers.attempt_quiz", quiz_id=quiz_id))


@controllers.route("/attempt_quiz/<int:quiz_id>", methods=["GET", "POST"])
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    
    total_questions = len(questions)
    current_index = session.get("current_question", 0) #default:0
    user_id1 = session.get("user_id") 
    
    

    # Auto-submit if time runs out
    quiz_end_time = session.get("quiz_end_time")
    end_time = datetime.strptime(quiz_end_time, "%Y-%m-%d %H:%M:%S")
    remaining_time = max(0, (end_time - datetime.now()).seconds)
    print(remaining_time)

    if remaining_time == 0:
        return redirect(url_for("controllers.submit_quiz", quiz_id=quiz_id))

    if request.method == "POST":
        selected_option = request.form.get("selected_option")
        print(selected_option)
        
        existing_response = UserResponse.query.filter_by(
        user_id=session["user_id"],
        quiz_id=quiz_id,
        question_id=questions[current_index].id).first()
        
        print(existing_response)

        if existing_response:
            # If the response exists, update it instead of creating a new one
            if selected_option: # Only update if the user selected an option
                existing_response.selected_option = selected_option
        else:
            # Otherwise, create a new response
            user_response = UserResponse(
                user_id=session["user_id"],
                quiz_id=quiz_id,
                question_id=questions[current_index].id,
                selected_option=selected_option
            )
            
            db.session.add(user_response)
        db.session.commit()

        
        if "next" in request.form and current_index < total_questions - 1:
            session["current_question"] += 1

        
        elif "prev" in request.form and current_index > 0:
            session["current_question"] -= 1

        # Last question
        elif "submit" in request.form:
            return redirect(url_for("controllers.submit_quiz", quiz_id = quiz.id))

    question = questions[session["current_question"]]

    return render_template("start_quiz.html",quiz_id=quiz_id,question=question,total_questions=total_questions,remaining_time=remaining_time,current_index=session["current_question"]
)




@controllers.route("/submit_quiz/<int:quiz_id>")
def submit_quiz(quiz_id):
    
    user_id1 = session.get("user_id") 
    user_responses = UserResponse.query.filter_by(user_id=user_id1, quiz_id=quiz_id).all() # ensures it is the correct user for the quiz
   
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    print(questions)

    
    total_questions = len(questions)
    

    total_score = 0  

    for response in user_responses:
        question = Question.query.get((response.question_id, quiz_id))
        print(response.selected_option)
        if  response.selected_option == question.correct_option:
            total_score += 1 #adds only for the correct user
    percent = (total_score)/total_questions * 100
            
    existing_score = Score.query.filter_by(user_id=user_id1, quiz_id=quiz_id).first() 
    if existing_score:   # else if u try giving the quiz again it willa add another record which shldnt happen as onyl 1 chance shld be given
                         # basically u can't use the submit button again to add anything
        flash("Quiz already attempted!!")
        return redirect(url_for("controllers.user_dashboard"))
    else:
        new_score = Score(user_id=user_id1, quiz_id=quiz_id, score=total_score, percent=percent, max_score=total_questions,submitted_at=datetime.now(timezone.utc))
        db.session.add(new_score)       
    
    db.session.commit()  

    
    return redirect(url_for("controllers.scores"))




@controllers.route("/scores")
def scores():
    user_id = session.get("user_id")
    user = User.query.get(session['user_id']) #as the user_id changes only when logged out
    #quiz_id = session.get("quiz_id")
    #questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    search_query = request.args.get("search_quiz", "").strip()  # Get the search term
    
    print(search_query)
    

    
    #total_questions = len(questions)
    #percent = (Score.score)/total_questions * 100
    
   
    q = (
        db.session.query(Quiz.id.label("quiz_id"), Quiz.title.label("quiz_title"),Quiz.date.label("quiz_date"), Score.score, Score.max_score, Score.percent, Score.submitted_at)
        .join(Score, Score.quiz_id == Quiz.id)
        .filter(Score.user_id == user_id)
        #.all()
    ) #Limitation : If the quiz is deleted by admin the user can't view their scores
    
    
    if search_query:
        q = q.filter(Quiz.title.ilike(f"%{search_query}%"))  # Case-insensitive search

    user_scores = q
    print (user_scores)

    return render_template("scores.html", user_scores=user_scores, user = user , search_query=search_query)






@controllers.route('/view_quiz/<int:quiz_id>') 
def view_quiz(quiz_id):
    if 'user_id' not in session :
        flash('Please log in to access the dashboard.')
        return redirect(url_for('controllers.login'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    
    
    return render_template('view_quiz.html', quiz = quiz)   





# Admin dashboard
@controllers.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'Admin':
        flash('Unauthorized access.')
        return redirect(url_for('controllers.admin_login'))
    
    search_query = request.args.get('search', '').strip()  # Get search query from URL
    
    if search_query:
        users = User.query.filter(User.username.ilike(f"%{search_query}%")).all()  # Case-insensitive search
    else:
        users = User.query.all()  # Fetch all users if no search query
        
    print(users)
    
    #users = User.query.all()  # Fetch all users for the dashboard
    subjects = Subject.query.all()  # Fetch all subjects for the dashboard
    chapters = Chapter.query.all()  # Fetch all chapters
    quizzes = Quiz.query.all()  # Fetch all quizzes
    questions = Question.query.all()  # Fetch all questions
    return render_template('admin_dashboard.html', users=users, subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions,search_query = search_query)








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
    
    search_query = request.args.get('search_quiz', '').strip()  # Get search query from URL
    search_query_1 = request.args.get('search_ques', '').strip()  # Get search query from URL
    
    if search_query:
        quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{search_query}%")).all()  # Case-insensitive search
    else:
        quizzes = Quiz.query.all()  # Fetch all quizzes
        
    #print(questions)
        
    print(search_query_1)      
    if search_query_1:
        questions = Question.query.filter(Question.title.ilike(f"%{search_query_1}%")).all()  # Case-insensitive search
    else:
        questions = Question.query.all()  # Fetch all questions
        
    subjects = Subject.query.all()  # Fetch all subjects for the dashboard
    chapters = Chapter.query.all()  # Fetch all chapters
    
    print(questions)
    
    
 
    
    return render_template('admin_dashboard_quiz.html', subjects=subjects,  search_query=search_query, chapters=chapters, quizzes=quizzes, questions=questions , search_query_1=search_query_1)


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
@controllers.route('/search_user', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
    subjects = Subject.query.filter(Subject.name.like(f'%{query}%')).all() # Fetching all records from the subject db
    chapters = Chapter.query.filter(Chapter.name.like(f'%{query}%')).all()
    quizzes = Quiz.query.filter(Quiz.title.like(f'%{query}%')).all()
    questions = Question.query.filter(Question.title.like(f'%{query}%')).all()
    return render_template('search.html', subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions)





# Logout
@controllers.route('/logout')
def logout_user():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('controllers.login'))

# Logout
@controllers.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('controllers.admin_login'))
