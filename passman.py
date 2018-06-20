#!/usr/bin/env python3
# don't forget : chmod +x passman.py

import bcrypt
from models import *
from colorama import init
from termcolor import colored, cprint

init()

line = "\n" + ('=' * 25) + "\n"
current_user = None

def initialize():
    """Create the database and tables if they don't already exist"""
    db.connect()
    db.create_tables([Password, User], safe = True)

def check_users():
    users = User.select()
    if not users.exists():
        create_user()


def create_user():
    """Create a new user"""
    print(line)
    cprint('Create a new user', 'magenta', attrs=['bold'])
    new_user = False
    while new_user == False:
        username = input(f"Enter a {colored('username', 'cyan')}: ")
        password = input(f"Enter a {colored('password', 'cyan')}: ")
        confirmation = input(f"Confirm {colored('password', 'cyan')}: ")

        errors = []
        if username == "":
            errors.append('Missing username')
        if password == "":
            errors.append('Missing password')
        if confirmation == "":
            errors.append('Missing password confirmation')
        if password != confirmation:
            errors.append('Password and confirmation do not match')

        if len(errors) > 0:
            cprint("** Error - User cannot be saved", 'red')
            for error in errors:
                cprint(f"** {error}", 'red')
            print(line)
            continue

        query = User.select().where(User.username == username)
        if query.exists():
            print("Username unavailable. Please try again.")
            continue


        hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        global current_user
        current_user = User.create(
            username = username,
            password_hash = hash
        )
        cprint("User created successfully!", 'green')
        new_user = True


def login():
    global current_user
    if not current_user:
        login = False
    else:
        login = True

    while login == False:
        entered_username = input("Please enter your user name: ")
        entered_password = input("Please enter your master password: ")

        query = User.select().where(User.username == entered_username)
        if not query.exists():
            print("User '{}' not found".format(entered_username))
            continue

        created_user = User.get(User.username == entered_username)
        encoded_entered_password = bytes(entered_password, 'utf-8')
        encoded_stored_hash = bytes(created_user.password_hash, 'utf-8')

        hash = bcrypt.hashpw(encoded_entered_password, encoded_stored_hash).decode('utf-8')

        if created_user.password_hash == hash:
            login = True
        else:
            print("Password not valid for user '{}'".format(entered_username))
            continue

def menu_loop():
    """Show the menu"""
    choice = None

    print(line)

    while choice != 'q':
        print("Enter" + colored(" 'q' ", 'yellow') + "to quit.")
        for key, value in menu.items():
            print(colored(key, 'magenta') + ") " + value.__doc__)

        choice = input(colored('Action', 'cyan') + ': ').lower().strip()

        if choice in menu:
            menu[choice]()

def add_password():
    """Add a password"""
    application = input("Enter the application name: ")
    login = input("Enter the login name (email or username): ")
    password = input("Enter password: ")
    password_again = input("Confirm password: ")
    notes = input("(optional) Enter notes/ additional info: ")

    errors = []
    if application == "":
        errors.append('Missing application')
    if login == "":
        errors.append('Missing login')
    if password == "":
        errors.append('Missing password')
    if password_again == "":
        errors.append('Missing password confirmation')
    if password != password_again:
        errors.append('Password and confirmation do not match')

    if len(errors) > 0:
        print("** Error - Password cannot be saved")
        for error in errors:
            print("** " + error)
        print(line)

    if not errors:
        if input("Save password? [Yn] ").lower() != 'n':
            global current_user
            Password.create(
                user = current_user,
                application = application,
                login = login,
                password = password,
                notes = notes
            )
            print("Saved successfully!")

def view_passwords(search_query = None):
    """View all passwords"""
    passwords = Password.select().order_by(Password.modified_at.desc())
    if search_query:
        passwords = passwords.where(Password.application.contains(search_query))

    if not passwords:
        cprint("No records found...", 'yellow')
        print(line)

    for password in passwords:
        modified_at = password.modified_at.strftime('%B %d, %Y')
        print("\n" + ('=' * 25))
        print(f"Application Name: {password.application}")
        print(f"Login Credentials: {password.login}")
        print(f"Password: {password.password}")
        print(f"Notes: {password.notes}")
        print(f"Last Modified: {modified_at}")
        print(('=' * 25) + "\n")
        print('n) for next password')
        print('q) return to main menu')

        next_action = input("Action: [Nq] ").lower().strip()
        if next_action == 'q':
            break

def search_passwords():
    """Search all passwords by application name"""
    query = input("Search: ").lower().strip()
    view_passwords(query)


def delete_password(password):
    """Delete a password"""

menu = OrderedDict([
    ('a', add_password),
    ('v', view_passwords),
    ('s', search_passwords),
    ('c', create_user)
])

if __name__ == '__main__':
    initialize()
    check_users()
    login()
    menu_loop()
