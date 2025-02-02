from flask import Flask, render_template
from controllers.controllers import *
from model.model import * 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shreyash.db"
app.config["SECRET_KEY"] = "shreyash"

db.init_app(app)
app.register_blueprint(controllers)

def create_admin():

    with app.app_context():
        admin_email = "shreyashmad_admin@MAD1P.com"
        admin_user = User.query.filter_by(email = admin_email).first()
        if not admin_user:
            admin_username = "S_admin"
            admin_password = "S4091"
            admin_user = User( username=admin_username, email=admin_email, password = admin_password, roles="Admin")
            db.session.add(admin_user)
            db.session.commit()
            print("Admin created successfully")
        else:
            print("Admin already exists")


with app.app_context():
    db.create_all()
    create_admin()
    
#SEARCH FUNCTIONALITY
#SUMMARY
#BLOCK AND UNLOCKS THE USER SO THAT USER CAN'T ACCESS ANYMORE
#USER CAN START THE QUIZ AND FINISH WITHIN THE DURATION PROVIDED  AND SEE THEIR SCORES
#USERS CAN SEE A SUMMARY REPORT OF THEIR PAST QUIZZES

    



if __name__ == "__main__":
    app.run(debug = True, port = 6005)
