from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique = True)
    email = db.Column(db.String(50), nullable=False, unique = True)
    password = db.Column(db.String(50), nullable=False)
    #post = db.relationship("Post", backref="user",lazy = True)


    roles = db.Column(db.String(10), nullable=False, default="Student")  # 'admin' or 'student'

    # Relationships
    scores = db.relationship("Score", back_populates="user")

# Subject table
class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(700), nullable=True)
    # Relationships
    chapters = db.relationship("Chapter", back_populates="subject", cascade="all, delete-orphan")

# Chapter table
class Chapter(db.Model):
    __tablename__ = "chapters"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(700), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)

    # Relationships
    subject = db.relationship("Subject", back_populates="chapters")
    quizzes = db.relationship("Quiz", back_populates="chapter", cascade="all, delete-orphan")

# Quiz table
class Quiz(db.Model):
    __tablename__ = "quizzes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapters.id"), nullable=False)

    date = db.Column(db.Date, nullable=False)  
    time = db.Column(db.Time, nullable=False)  
    duration = db.Column(db.Integer, nullable=False) 
    rules = db.Column(db.String(500), nullable=True)  
    # Relationships
    chapter = db.relationship("Chapter", back_populates="quizzes")
    questions = db.relationship("Question", back_populates="quiz", cascade="all, delete-orphan")

# Question table
class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True) #Question_id
    title = db.Column(db.String(100), nullable=False)
    statement = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # e.g., A ,B ,C D
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False,  primary_key=True) #COMPOSITE KEY

    # Relationships
    quiz = db.relationship("Quiz", back_populates="questions")


class UserResponse(db.Model):
    __tablename__ = "user_responses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    selected_option = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    
# Score table
class Score(db.Model):
    __tablename__ = "scores"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    percent = db.Column(db.Float, nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="scores")
    quiz = db.relationship("Quiz")
