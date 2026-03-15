
# ⏱️ TimeClock Application

A web-based employee time tracking system built with **Django**.

---

## 🚀 Project Overview

The **TimeClock** application allows employees to:

- 🟢 Clock in  
- 🔴 Clock out  
- 📄 View recent shifts  

Administrators can:

- 📅 Create and manage scheduled shifts  
- ⚙️ Configure scheduling policies  
- ✏️ Edit shift records with audit logging  
- 👥 Manage users via Django Admin  

This project follows a **layered architecture** where business logic is separated from views using a dedicated service layer.

---

## 🏗️ Architecture Overview

```
Browser
   ↓
Django Views
   ↓
Service Layer (services.py)
   ↓
Models
   ↓
SQLite Database
```

### 🧠 Design Principles

- Thin views  
- Business logic centralized in `services.py`  
- Policy-driven behavior  
- Audit logging for admin edits  
- Role-based access control  

---

## 📂 File Structure

```
timeclock/
│
├── manage.py
│
├── timeclock/                # Project configuration
│   ├── settings.py           # Global configuration
│   ├── urls.py               # Root URL routing
│   ├── wsgi.py               # WSGI entrypoint (Gunicorn)
│   ├── asgi.py               # ASGI entrypoint
│
├── core/                     # Main application
│   ├── models.py             # 🗄️ Database models
│   ├── services.py           # 🧩 Business logic layer
│   ├── views.py              # 🌐 Request handling
│   ├── forms.py              # 📝 Admin validation forms
│   ├── policy_forms.py       # ⚙️ Policy configuration form
│   ├── schedule_forms.py     # 📅 Scheduled shift form
│   ├── permissions.py        # 🔐 Portal access decorator
│   ├── admin.py              # 🛠️ Django admin configuration
│   ├── urls.py               # 🔀 App routes
│   ├── tests.py              # 🧪 Unit tests
│
└── db.sqlite3                # 💾 Development database
```

---

## 🛠️ How to Run Locally

### 1️⃣ Clone the repository

```
git clone <repo-url>
cd timeclock
```

### 2️⃣ Create virtual environment

```
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate    # Windows
```

### 3️⃣ Install dependencies

```
pip install openpyxl (Needed for Mircosoft Excel openpyxl warnings, add locally before virtual environment too if needed)
pip install -r requirements.txt
```

### 4️⃣ Run migrations

```
python manage.py migrate
```

### 5️⃣ Create superuser

```
python manage.py createsuperuser
```

### 6️⃣ Run development server

```
python manage.py runserver
```

Open your browser:

```
http://127.0.0.1:8000/
```

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
