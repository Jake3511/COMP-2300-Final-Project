import base64
import bcrypt
import datetime as dt
import key_gen as k
import pwinput


# TODO: change return user to sending unhashed password
# TODO: compare unhashed password to hashed password for return users
    # in login_server

SALT = bcrypt.gensalt() # used to generate a random number

ACTION_LIST = ["help", "add", "list", "send", "exit"]

CONTACTS = "Contacts"
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

            return "Contact Added."

        case "list": # TODO: add online test
            contacts = database[USER][username][CONTACTS]
            if len(contacts) > 0:
                friend = False
                msg = str()
                for contact, email, added_back_bool in contacts:
                    if added_back_bool == True:
                        friend = True
                        msg += f"\t* {contact} <{email}>"
                    if not contacts[-1] == [contact, email, added_back_bool]:
                        msg += "\n"
                if friend:
                    return msg
                else:
                    return "\tNo Contacts Added You Back"
            else:
                return "\tContact List Is Empty."

        case "send": # TODO: flesh out
            pass
        case _:
            return [True, "\tInvalid Command."]


def comp_str(p1:str, p2:str)->bool:
    return p1 == p2


def get_email(indent="")->str:
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
    # TODO: validate password via regex
    username = get_email(indent)

    return full_name, username


def get_password(msg:str)->str:
    # TODO: add password strength validation?
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
            email = input("Enter Your Email: ")
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
            database[USER][email][CONTACTS] = []

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

