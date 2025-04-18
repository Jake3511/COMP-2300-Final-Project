import datetime as dt
import base64
import bcrypt
import pwinput
import re


SALT = bcrypt.gensalt() # used to generate a random number

ACTION_LIST = ["help", "add", "list", "send", "exit"]

USER = "User"
CONTACTS = "Contacts"
FULL_NAME = "Full_Name"
PASSWORD = "Password"
TIME = "Time"
LOGINS = "Logins"



# Optional "LockOut" Exception
class LockOut(Exception):
    def __init__(self, message):
        super().__init__(message)


def get_hashed_password(password:str)->str:
    '''Gets password from parameter;
    Hashes password;
    Returns password hash'''

    password = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password, SALT) # hashed the password using the generated number(SALT)
    return base64.b64encode(hashed_password).decode('utf-8')
    # return password in json formatted string (was giving me an error when tried to save binary string in json format)


def comp_str(p1:str, p2:str)->bool:
    return p1 == p2


def get_password(msg:str)->str:
    # TODO: add password strength validation?
    password = pwinput.pwinput(prompt=msg, mask="*")
    return get_hashed_password(password)


def new_user()->list:
    '''Creates a new user and adds them to the Database'''
    full_name, username = get_name_and_email()

    passwd1 = ""
    passwd2 = "a"

    n = 0
    while not passwd1 == passwd2:
        n += 1
        passwd1 = get_password("Enter Password: ")
        passwd2 = get_password("Re-enter Password: ")

        if not passwd1 == passwd2:
            print("\nPassword Mis-match.")
            print("Try Again.\n")

        if n > 5:
            print("Password Attempts Exceeded.")
            return [False, None, None, None]

    print("\nPasswords Match.")
    return [True, username, full_name, passwd1]


def login_client()->list:
    failed = [False, None, None, None, None]
    ret_user = input("New or Returning User? (n/r): ").lower()
    while not ret_user in ["n", "r"]:
        ret_user = input("New or Returning User? (n/r): ").lower()
    new:bool = ret_user == "n"

    try:
        success = True
        if new:
            success, email, full_name, password = new_user()
        else:
            full_name, email = get_name_and_email()
            password = get_password()

        if success:
            return [True, ret_user, email, full_name, password]
        else:
            return failed
    except:
        return failed


def login_server(database:dict, new:bool, user:list, password:str)->list:
    '''Prompts user for username and password.
    Returns True on a successful login; False otherwise'''

    email, full_name = user

    # Lockout_timer is the number of minutes a lockout lasts for
    # and also the amount of time you must wait between login attempts to
    # not increment the "logins" value.
    lockout_timer = 5

    if new:
        if email in list(database[USER].values()):
            return login_server(database, False, user, password)
        else:
            database[USER][email] = {}
            database[USER][email][FULL_NAME] = full_name
            database[USER][email][PASSWORD] = password
            database[USER][email][TIME] = str(dt.datetime.now())
            database[USER][email][LOGINS] = 1
            database[USER][email][CONTACTS] = {}

            return [True, "New User Added."]
    else:
        try:
            database[USER][email]
        except KeyError:
            return [False, "Invalid Email."]

    if database[USER][email][LOGINS] > 5 and database[USER][email][TIME] >= str(dt.datetime.now() - dt.timedelta(minutes=lockout_timer)):
        return [False, "Account Locked: Too Many Log In Attempts!"]

    passwd_correct = comp_str(password, database[USER][email][PASSWORD])

    if passwd_correct:
        database[USER][email][TIME] = str(dt.datetime.now())
        database[USER][email][LOGINS] = 1

        return [True, "Log In Successfully."]
    else:
        database[USER][email][TIME] = str(dt.datetime.now())
        database[USER][email][LOGINS] += 1

        return [False, "Log In Failed."]


def actions_server(database:dict, command:int, username:str, data:list)->list:
    match ACTION_LIST[command]:
        case "add":
            email, full_name = data
            added_back = False

            for _, user_email, _ in database[USER][username][CONTACTS]:
                if email == user_email:
                    return [True, "Contact Already Added."]

            try:
                try:
                    if database[USER][email]:
                        added_back = True
                        for _, user, added_back_bool in database[USER][email][CONTACTS]:
                            if email == user:
                                database[USER][email][CONTACTS][user][2] = True
                except KeyError:
                    added_back = False

                database[USER][username][CONTACTS].append([full_name, email, added_back])

            except KeyError:
                database[USER][username][CONTACTS] = []
                database[USER][username][CONTACTS].append([full_name, email, added_back])

            return [True, "Contact Added."]

        case "list": # TODO: add online test
            try:
                contacts = database[USER][username][CONTACTS]
                friend = False
                msg = str()
                for contact, email, added_back_bool in contacts:
                    if added_back_bool == True:
                        friend = True
                        msg.append(f"\t* {contact} <{email}>")
                    if not contacts[-1] == [contact, email, added_back_bool]:
                        msg.append("\n")
                    return msg
                if friend == False:
                    return "\tNo Contacts Added You Back"
            except KeyError:
                return "\tContact List Is Empty."

        case "send": # TODO: flesh out
            pass


def get_name_and_email(indent="")->list:
    # Get Full Name
    full_name = input(f"{indent}Enter Full Name: ")
    # Get username/email
    # TODO: validate password via regex
    username = input(f"{indent}Enter Email Address: ").lower()

    return full_name, username
