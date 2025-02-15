# Quiz Master App

## Overview
Quiz Master is a Flask-based web application that allows administrators to create, edit, and manage quizzes, while users can attempt quizzes within a timed session. The app includes role-based authentication, quiz visibility controls, and result tracking.

## Features
- **Admin Dashboard:** Create, edit, and delete subjects, chapters, quizzes, and questions.
- **User Management:** Admins can block/unblock users.
- **Search Functionality:** Search for users, subjects, quizzes, and questions.
- **Timed Quizzes:** Auto-submission when time runs out.
- **Role-Based Authentication:** Secure access for admins and users.
- **Database Management:** Uses SQLAlchemy and SQLite.
- **Summary:** A detailed summary report of the performances.

---

### Prerequisites
Ensure you have Python installed (preferably Python 3.8+).

## Installation



### Step 1: Clone the Repository
```sh
git clone https://github.com/22f3001070/QUIZ_MASTER_22f3001070.git
cd quiz-master
```
Create a `.env` file in the root directory.
Copy the values from `.env.example` and fill in your details.



### Step 2: Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

### Step 3: Install Dependencies
```sh
pip install -r requirements.txt
```


### Step 5: Run the Application
```sh
python app.py
```

The app will run on **http://127.0.0.1:6005/**.

---



## Usage
- **Admins** can create, edit, and manage quizzes.
- **Users** can register, attempt quizzes, and view results.
- The admin can block/unblock users and manage quiz visibility.
- When a user clicks "Attempt," the quiz timer starts and auto-submits when time expires.

---

## Limitations
- Editing a quiz requires updating the time settings.
- Placeholder for the option already selected by the user.
- Users cannot modify their responses once submitted.
- Deleting a quiz removes all related user data and scores.

---

## Future Enhancements
- **Leaderboard System** to rank users based on quiz scores.
- **Email Notifications** for quiz reminders and results.
- **Advanced Analytics** for admin to track user progress.
- Admin can hide or reveal the quiz when they create
- Another functionality is showing incorrect and correct reponses to to users for each question
- Another functionality is assigning different points to questions rather than a fixed 1.
- **Styling** Add DP for users.
---


## Contributors
Developed by **Shreyash Srivastava**. Contributions are welcome!


