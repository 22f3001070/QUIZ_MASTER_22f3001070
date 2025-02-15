from flask import Flask, render_template
from controllers.controllers import *
from model.model import * 
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


db.init_app(app)
app.register_blueprint(controllers)

def create_admin():
    
    with app.app_context():
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_username = "S_admin"
            admin_user = User(username=admin_username, email=admin_email, password=admin_password, roles="Admin")
            db.session.add(admin_user)
            db.session.commit()
            print("Admin created successfully")
        else:
            print("Admin already exists")

with app.app_context():
    db.create_all()
    create_admin()
    
# (Done) SEARCH FUNCTIONALITY
# (Done) SUMMARY



# ( Added ) Time_stamp in the scores
# ( Completed ) When u click the button it sends a response at that very moment creating multiple scores, we need to ensure 1 q sends only 1 respond and never more!
# (Allowed) Confirm once if the date and time of the quiz is deadline or the actual time of taking a quiz 

# Another functionality is admin can hide or visible the quiz when they create
# Another functionality is showing incorrect and correct reponses to to users for each question
# Another functionality is assigning different points to questions rather than a fixed 1.

# (Added) Adding a logo!

#Limitations: 
# 1) HAVE TO CHANGE THE TIME WHILE EDITING THE QUIZ, 
# 2) PLACEHOLDER FOR THE OPTION ARLEADY SELECTED BY THE USER, 
# 3) Deleting the Quiz by admin removes all the records for the users including their scores and summary pertaining to that quiz

# Aesthetics (DONE)

# Report
# Video
    



if __name__ == "__main__":
    app.run(debug = True, port = 6005)
