## User Stories Document

---

## 1. Introduction

This document defines the user stories for the Time Clock Application. User stories describe the functionality of the system from the perspective of employees and administrators.

---

## 2. User Roles

### 2.1 Employee
An employee uses the system to record their working hours, clock in and out, and review their time records.

### 2.2 Administrator
An administrator manages employee accounts, monitors attendance, and edits time records when necessary.

---

## 3. User Stories

### Account Management

#### US-01 – Employee Registration
**User Story:**  
As an employee, I want to register my account in the Time Clock Application so that I can securely access the system and record my work hours.

**Acceptance Criteria:**
- Employees can create a new account.
- Required information must be entered (name, email, password).
- The system stores the information securely.
- The employee can log in after registration.

#### US-02 – Admin Registration
**User Story:**  
As an admin, I want to register my account in the Time Clock Application so that I can securely access the system and manage employee records and attendance reports.

**Acceptance Criteria:**
- The system allows admin account creation.
- Admin accounts have elevated permissions.
- Admins can access administrative tools.

#### US-03 – Employee Login
**User Story:**  
As an employee, I want to log into the Time Clock Application so that I can access my personal dashboard and manage my work hours securely.

**Acceptance Criteria:**
- Employees must enter valid login credentials.
- The system verifies the credentials.
- The employee is redirected to their dashboard.

#### US-04 – Admin Login
**User Story:**  
As an admin, I want to log into the Time Clock Application so that I can access management features and view all employee records.

**Acceptance Criteria:**
- Admin credentials must be verified.
- The admin is redirected to the admin dashboard.
- The admin can access employee management tools.

#### US-05 – User Logout
**User Story:**  
As a user, I want to log out of the system so that my account remains secure when I finish using the application.

**Acceptance Criteria:**
- The system provides a logout button.
- The session ends immediately after logout.
- The user must log in again to access the system.

#### US-06 – Password Reset
**User Story:**  
As a user, I want to reset my password if I forget it so that I can regain access to my account.

**Acceptance Criteria:**
- Users can request a password reset.
- The system verifies the user's email.
- Users can create a new password.

---

### Time Tracking

#### US-07 – Employee Clock In
**User Story:**  
As an employee, I want to clock in at the start of my shift so that my work hours are accurately recorded.

**Acceptance Criteria:**
- The system records the clock-in time.
- Employees cannot clock in twice without clocking out.
- The time is saved in the database.

#### US-08 – Employee Clock Out
**User Story:**  
As an employee, I want to clock out at the end of my shift so that my total work hours for the day are saved correctly.

**Acceptance Criteria:**
- The system records the clock-out time.
- The system calculates total worked hours.
- The information is saved.

---

### Time Tracking and Reporting

#### US-09 – Employee View My Hours
**User Story:**  
As an employee, I want to view my daily, weekly, and monthly hours so that I can track my work schedule and overtime.

**Acceptance Criteria:**
- Employees can access their time records.
- Records can be displayed by day, week, or month.
- Total hours are calculated automatically.

#### US-10 – Admin View Employee Hours
**User Story:**  
As an admin, I want to view employees’ clock-in and clock-out times so that I can monitor attendance and manage payroll efficiently.

**Acceptance Criteria:**
- Admins can view all employee attendance records.
- Admins can filter records by employee or date.
- Total hours worked are displayed.

---

### Employee Record Management

#### US-11 – Admin Edit Employee Records
**User Story:**  
As an admin, I want to update or correct employee clock-in and clock-out records so that the time tracking data remains accurate.

**Acceptance Criteria:**
- Admins can modify time records.
- Updated records are saved in the system.
- Changes are reflected in reports.

#### US-12 – Admin Add New Employee
**User Story:**  
As an admin, I want to add new employees to the system so that they can access the time clock application.

**Acceptance Criteria:**
- Admins can create employee accounts.
- Required employee details must be entered.
- The employee account is saved in the system.

#### US-13 – Admin Delete Employee
**User Story:**  
As an admin, I want to remove employee accounts from the system so that inactive users no longer have access.

**Acceptance Criteria:**
- Admins can delete employee accounts.
- The system confirms deletion before removing the account.
- Deleted users can no longer log in.

---

### Reporting

#### US-14 – Generate Attendance Reports
**User Story:**  
As an admin, I want to generate attendance reports so that I can review employee work hours for payroll or management purposes.

**Acceptance Criteria:**
- Reports can be generated for specific dates.
- Reports include employee clock-in and clock-out times.
- Reports show total hours worked.

#### US-15 – Overtime Calculation
**User Story:**  
As an admin, I want the system to calculate employee overtime so that extra hours worked can be tracked accurately.

**Acceptance Criteria:**
- The system calculates overtime automatically.
- Overtime is displayed in reports.
- Admins can view overtime per employee.

---