# ⏱️ TimeClock App

## Overview

The **TimeClock App** is a Django-based employee time tracking system designed to manage real-world shift operations with structured data models, enforced policies, and auditability.

It supports clock-in/clock-out workflows, meal breaks, scheduled shifts, and administrative controls, all backed by a tested and validated backend.

---

## 🚀 Core Features

### 👤 Employee Functionality

* Clock in and out
* Start and end meal breaks
* Track worked time vs break time
* Associate worked shifts with scheduled shifts

### 🛠️ Admin Functionality

* Create and manage scheduled shifts
* Enforce scheduling policies
* Edit shifts with audit logging
* Track changes via `ShiftEditLog`
* Export timesheet data (CSV)

---

## 🧠 Data Model

The system is built around structured, production-style models:

* **WorkShift** → Actual worked shift (clock in/out)
* **ScheduledShift** → Planned shift created by admins
* **MealBreak** → Breaks tied to a WorkShift
* **TimeclockPolicy** → Global behavior rules (singleton)
* **ShiftEditLog** → Audit trail for admin edits

This separation allows clean business logic, auditability, and future scalability.

---

## 🏗️ Tech Stack

* **Backend:** Django
* **Database:** SQLite (default)
* **Deployment:** Raspberry Pi (Gunicorn-ready)
* **Timezone Handling:** Enabled (UTC-aware)

---

## 📁 Project Structure

```id="projstruct"
timeclock/
├── manage.py
├── db.sqlite3
├── core/                  # Main Django app
│   ├── models.py
│   ├── views.py
│   ├── tests.py
│   └── scripts/
├── timeclock/             # Project config (settings, urls)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

```bash id="setup1"
git clone https://github.com/bwtatum/CAPSTONE.git
cd CAPSTONE
git checkout timeClock-v0.2_T

python3 -m venv .venv
source .venv/bin/activate   # or activate.fish

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

# ⚡ Data Injection & Test Script

## Purpose

To eliminate repetitive manual testing and rapidly generate realistic datasets, a custom script was created.

This script:

* Seeds the database with users and shifts
* Simulates realistic work patterns
* Runs validation checks automatically

---

## 📍 Location

```id="injectloc"
core/scripts/inject_and_test_data.py
```

---

## ▶️ Run the Script

```bash id="runshell"
python manage.py shell
```

```python id="runinject"
exec(open('core/scripts/inject_and_test_data.py').read())
```

---

## 🧠 What It Does

### 🔹 Data Injection

* Creates test users (`test_user_*`)
* Generates multi-day WorkShift records
* Simulates MealBreaks
* Produces realistic time distributions

### 🔹 Built-in Validation

* Confirms users exist
* Confirms shifts are created
* Validates break durations
* Verifies shift integrity

---

## ⚠️ Notes

* Intended for development use only
* Writes directly to the database
* Reset with:

```bash id="flush"
python manage.py flush
```

---

# 🧪 Automated Test Suite

The project includes a structured Django test suite to validate core functionality.

---

## ▶️ Run Tests

```bash id="runtests"
python manage.py test
```

---

## ✅ Current Coverage

Tests validate:

* WorkShift creation
* Shift duration calculations
* MealBreak duration integrity
* Aggregated break time (`break_seconds`)

---

## 🧠 Example Test Logic

```python id="testexample"
shift = WorkShift.objects.create(
    employee=user,
    clock_in=timezone.now(),
    clock_out=timezone.now() + timedelta(hours=8),
)

MealBreak.objects.create(
    shift=shift,
    start_time=shift.clock_in + timedelta(hours=4),
    end_time=shift.clock_in + timedelta(hours=4, minutes=30),
)

assert shift.break_seconds() > 0
```

---

## 🧬 Why Tests Matter

* Prevent regressions during development
* Validate business logic automatically
* Ensure data integrity across features
* Provide confidence for future changes

---

# 🔧 Configuration Notes

### Timezone Support

* Enabled via Django (`USE_TZ = True`)
* All datetime usage is timezone-aware (`timezone.now()`)

### Default Primary Key

```python id="pkfix"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

# 🚀 Future Improvements

* Convert injection script into a Django management command
* Expand test coverage for:

  * Schedule enforcement
  * Policy behavior
  * Admin edit audit logs
* Add CI pipeline for automated testing on push
* Introduce API endpoints for frontend/mobile integration

---

# 👷 Contributors

* Brandon Tatum
* Capstone Project Team

---

# 🧾 Final Notes

If something breaks:

* Verify virtual environment is active
* Ensure migrations are applied
* Re-run tests to validate system state

---

This project represents a fully functional, tested backend system designed with real-world constraints in mind.
