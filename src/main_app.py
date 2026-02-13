# Time Clock Application Capstone Project

# To Do List:
# User Account - Register, login, and logout functionality
# Calculate hours worked - Calculate total hours worked based on clock in and clock out times, per week and per day
# Timesheet view - users see their own hours, admin sees everyone's hours
# Admin tools - edit, delte, or export time entries
# Decide on lunch break functionality
# Implement a more secure login system with hashed passwords and a database of users

from datetime import datetime


def main():
    # Call Login function
    try:
        employee_id = login()
    
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return
    
    # Display current weekday, date, and time EX: Thursday, February 12, 2026 01:53:33 PM
    now = datetime.now()
    print(now.strftime("%A, %B %d, %Y %I:%M:%S %p"))
    
    # Call time clock functions to clock in, clock out, and lunch break
    # To Do:  Decide on lunch break functionality
    time_clock_menu(employee_id)
    

# Login function, must enter valid employee ID and password
# To Do: Implement a more secure login system with hashed passwords and a database of users
def login():
    employee_id = input("Enter your employee ID: ")
    password = input("Enter your password: ")
    # For simplicity, we will just check if the employee ID and password are not empty
    if employee_id and password:
        print("Login successful!")
        return employee_id
    else:
        print("Invalid employee ID or password. Please try again.")

# Display a menu with options to clock in, clock out, lunch break, or logout of the application
def time_clock_menu(employee_id):
    while True:
        print("\nMenu:")
        print("1. Clock In")
        print("2. Clock Out")
        print("3. Lunch Break")
        print("4. Logout")
        choice = input("Enter your choice (1-4): ")
            
        if choice == "1":
            clock_in(employee_id)
        elif choice == "2":
            clock_out(employee_id)
        elif choice == "3":
            lunch_break(employee_id)
        elif choice == "4":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")

# Function clock in an employee
def clock_in(employee_id):
    print(f"Employee {employee_id} clocked in.")

# Function clock out an employee
def clock_out(employee_id):
    print(f"Employee {employee_id} clocked out.")

# Function for lunch break
def lunch_break(employee_id):
    print(f"Employee {employee_id} is on a lunch break.")


if __name__ == "__main__":   main()