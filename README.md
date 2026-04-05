# ⏱️ TimeClock App (Capstone Project)

A full-stack Django application for managing employee time tracking,
scheduling, and administrative oversight.

------------------------------------------------------------------------

## 🚀 Features

### 👷 Employee

-   Clock in / clock out
-   View personal timesheet
-   Mobile-friendly interface (tablet-ready)

### 🧑‍💼 Admin

-   Manage employee schedules
-   Configure scheduling policies
-   View all timesheets
-   Export timesheets to CSV
-   Role-based dashboard

------------------------------------------------------------------------

## ⚙️ Tech Stack

-   Python 3
-   Django
-   SQLite (default)
-   HTML / CSS (custom UI)
-   JavaScript (light enhancements)

------------------------------------------------------------------------

## 🧠 Key Concepts Implemented

-   Role-based access control (Admin vs Employee)
-   Dynamic dashboards based on user role
-   Form handling with Django ModelForms
-   Clean UI with reusable layout components
-   CSV export functionality
-   Native browser date/time inputs

------------------------------------------------------------------------

## 📂 Project Structure

src/timeclock-app/ ├── core/ │ ├── models.py │ ├── views.py │ ├──
forms.py │ ├── schedule_forms.py │ ├── templates/ │ │ ├── core/ │ │ └──
registration/ │ └── static/

------------------------------------------------------------------------

## ▶️ Running the App

# Activate virtual environment

..venv`\Scripts`{=tex}`\activate`{=tex}

# Run migrations

python manage.py migrate

# Start server

python manage.py runserver

Then visit: http://127.0.0.1:8000

------------------------------------------------------------------------

## 🔐 Test Accounts

-   employee1 → standard employee
-   admin → admin user (must be in Admin group)

------------------------------------------------------------------------

## 📊 Export Feature

Admins can export all timesheet data to CSV from the View Timesheets
page.

------------------------------------------------------------------------

## 🎯 Project Purpose

This application demonstrates: - Real-world workforce management
workflows - Clean separation of roles and permissions - Practical UI/UX
design for internal tools

------------------------------------------------------------------------

## 👨‍💻 Author

Brandon Tatum\
Wake Tech Community College --- Capstone Project

------------------------------------------------------------------------

## 💡 Future Improvements

-   Inline schedule editing
-   Dashboard analytics (hours, trends)
-   API integration
-   Authentication enhancements

------------------------------------------------------------------------

## 🏁 Status

✅ Feature complete\
✅ Demo ready\
🚀 Actively polished
