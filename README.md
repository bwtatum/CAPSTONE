# 🚀 CSC289 Capstone Project

> **Course:** CSC289 – Capstone  
> **Institution:** Wake Technical Community College  
> **Term:** Spring 2026  
> **Team:** *Team 9*

---

## 📌 Project Overview

This repository contains the source code, documentation, and supporting materials for our **CSC289 Capstone Group Project**.

The goal of this project is to design, build, and deliver a complete, real-world application that demonstrates the technical, analytical, and collaborative skills developed throughout the Computer Science curriculum.

Our project emphasizes:
- Practical problem solving
- Clean, maintainable code
- Realistic system design
- Team collaboration and version control best practices

---

## 🎯 Problem Statement

Many real-world systems suffer from inefficiencies, lack of automation, or poor data visibility.  
This project addresses those challenges by providing a solution that is:

- Efficient
- Scalable
- User-friendly
- Backed by data and sound engineering principles

---

## 🧠 Solution Summary

Our application provides:

- A structured backend for managing data and logic
- A user-friendly interface for interaction and visualization
- Automated workflows to reduce manual effort
- Clear separation of concerns between components

The system was designed with extensibility and future enhancements in mind.

---

## 🛠️ Tech Stack

**Languages & Frameworks**
- Python
- Django
- HTML, CSS, JavaScript

**Data & Storage**
- SQLite (development)
- PostgreSQL (production-ready)

**Tools & Platforms**
- Git & GitHub
- Docker (optional deployment)
- VS Code

---

## 🗂️ Project Structure

```text
.
├── docs/               # Project documentation
├── src/                # Application source code
    ├── timeclock-app/
        ├── core/
        ├── timeclock/            
├── static
├──tests/              # Unit and integration tests
├── .gitignore
├── README.md
└── requirements.txt

## 🗂️ CMDs needed to run on a local end // Updated by Art for finalized branch

 - Change the directory if needed
cd src
cd timeclock-app

python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations --merge
python manage.py migrate

 - Create your Django super user if you do not have one yet
python manage.py createsuperuser

python manage.py runserver

---

## 👤 How the Application Works

### 🟢 Employee Flow

1. Login at `/accounts/login/`
2. Access dashboard at `/dashboard/`
3. Clock in or clock out
4. View recent shifts at `/timesheet/`

### 👨‍💼 Admin Flow

Admins must belong to the **Admin** group.

Admin features:

- `/portal/` → Admin dashboard  
- `/portal/schedule/` → Schedule + policy management  
- `/admin/` → Full Django admin site  

---

## ⚙️ Policy System

The `TimeclockPolicy` model controls:

- ⏰ Strict schedule enforcement  
- 🕒 Grace window for early/late clock-in  
- 🚫 Whether unscheduled clock-ins are allowed  
- ✍️ Whether admin edits require a reason  

Only **one policy record** exists (singleton pattern).

---

## 🧪 Testing

Run unit tests with:

```
python manage.py test
```

Tests cover:

- Strict vs non-strict scheduling  
- Grace window logic  
- Double clock-in prevention  
- Clock-out validation  
- Portal admin permission enforcement  

---

## 🔒 Production Notes

Before deploying:

- Set `DEBUG = False`  
- Configure `ALLOWED_HOSTS`  
- Move `SECRET_KEY` to environment variable  
- Use Gunicorn or similar WSGI server  
- Consider PostgreSQL for production database  

---

## 🔮 Future Improvements

- ⏳ Overtime calculation  
- ☕ Break tracking system  
- 📊 Reporting dashboard  
- 📤 CSV export for payroll  
- 🎛️ Role-based UI refinement  
- 🌍 API endpoints  

---

## 👨‍💻 Author

CSC154 Capstone Project – Group 9  
Built with Django ❤️
