import base64
import bcrypt
import datetime as dt
import key_gen as k
import json
import pwinput


SALT = bcrypt.gensalt() # used to generate a random number

ACTION_LIST = ["help", "add", "list", "send", "exit"]

CONTACTS = "Contacts"
DATABASE_CLIENT = "./database_client.bin"
FULL_NAME = "Full_Name"
LOGIN_COM = "Login"
LOGINS = "Logins"
PASSWORD = "Password"
TIME = "Time"
USER = "User"


def actions_server(database:dict, command:str, username:str, data:list)->str:
    match command:
        case "add":
            email, full_name = data
            added_back = False

            try:
                if database[USER][username][CONTACTS][email]:
                    return "Contact Already Added."
            except KeyError:
                pass

            try:
                if not database[USER][email][CONTACTS] == {}:
                    added_back = True
                    database[USER][email][CONTACTS][username][1] = True
                else:
                    added_back = False
            except KeyError:
                added_back = False

            try:
                database[USER][username][CONTACTS][email] = [full_name, added_back]
            except KeyError:
                database[USER][username][CONTACTS] = {}
                database[USER][username][CONTACTS][email] = [full_name, added_back]

            return "Contact Added."

        case "list": # TODO: add online test
            contacts = list(database[USER][username][CONTACTS].items())
            if len(contacts) > 0:
                friend = False
                msg = str()
                for email, value in contacts:
                    contact, added_back_bool = value
                    if added_back_bool == True:
                        friend = True
                        msg += f"\t* {contact} <{email}>"
                    if not contacts[-1] == (email, [contact, added_back_bool]):
                        msg += "\n"
                if friend:
                    return msg
                else:
                    return "\tNo Contacts Added You Back"
            else:
                return "\tContact List Is Empty."

        case "send": # TODO: add
            return '\t"send" Not Yet Implemented.'
        case _:
            return "\tInvalid Command."


def comp_str(p1:str, p2:str)->bool:
    return p1 == p2


def get_email(indent="")->str:
    # TODO: validate password via regex
    while True:
        email1 = input(f"{indent}Enter Email Address: ").lower()
        email2 = input(f"{indent}Enter Email Address Again: ").lower()

        if email1 == email2:
            return email1
        else:
            print("Emails Did Not Match.")
            continue


def get_hashed_password(password:str)->str:
    '''Gets password from parameter;
    Hashes password;
    Returns password hash'''

    password = password.encode('utf-8')
    salt = open("./Salt.bin", "rb").read()
    hashed_password = bcrypt.hashpw(password, salt) # hashed the password using the generated number(SALT)
    return base64.b64encode(hashed_password).decode('utf-8')

    # return bcrypt.hashpw(password, salt) # hashed the password using the generated number(SALT)
    # return password in json formatted string (was giving me an error when tried to save binary string in json format)


def get_name_and_email(indent="")->list:
    # Get Full Name
    full_name = input(f"{indent}Enter Full Name: ")
    # Get username/email
    username = get_email(indent)

    return full_name, username


def get_password(msg:str)->str:
    password = pwinput.pwinput(prompt=msg, mask="*")
    return get_hashed_password(password)


def login_client()->list:
    '''Client-side log in function.
    Generates a list containing;
    successful_loging:bool, new_user:bool, email:str,
    full_name:str, hashed_password:str'''

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
            email = input("Enter Your Email: ").lower()
            full_name = None
            password = get_password("Enter Password: ")

        if success:
            return [True, new, email, full_name, password]
        else:
            return failed
    except:
        return failed


def login_server(database:dict, new:bool, user:list, password:str)->list:
    '''Server-side log in function.
    Compares passed in parameters to passed in database.
    If user is new, vereifies their account doesn't already exist,
    then add account to datbase.
    If user already exists, or is not "new",
    attempt to log in using passed in user and password data.'''

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

    # If user has tried to log in too many time within the
    # lockout period, return account locked message,
    # update time of last log in attempt to now,
    # and stop before checking password
    if database[USER][email][LOGINS] > 5 and database[USER][email][TIME] >= str(dt.datetime.now() - dt.timedelta(minutes=lockout_timer)):
        database[USER][email][TIME] = str(dt.datetime.now())
        return [False, "Account Locked: Too Many Log In Attempts!"]

    # Validate password
    passwd_correct = comp_str(password, database[USER][email][PASSWORD])

    # If password is correct, set time of last log in to now,
    # and reset log in attempts to 1
    if passwd_correct:
        database[USER][email][TIME] = str(dt.datetime.now())
        database[USER][email][LOGINS] = 1

        return [True, "Log In Successfully."]
    else:
        # If password is incorrect, set time of last log in to now,
        # and increment number of log in attempts
        database[USER][email][TIME] = str(dt.datetime.now())
        database[USER][email][LOGINS] += 1

        return [False, "Log In Failed."]


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
            print("\nPassword Attempts Exceeded.")
            return [False, None, None, None]

    print("Passwords Match.")
    return [True, username, full_name, passwd1]


def update_database(database:dict, file_name)->None:
    with open(file_name, "w") as db_file:
        db_file.write(json.dumps(database))
