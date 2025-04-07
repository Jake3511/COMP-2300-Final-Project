import datetime as dt
import base64
import bcrypt
import pwinput
import re


SALT = bcrypt.gensalt() # used to generate a random number

ACTION_LIST = ["help", "add", "list", "send", "exit"]


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
    return get_hashed_password(password) # Moved another input statement here for the same error I was getting before


def new_user(database:dict)->bool:
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
            print("Password Attempts Exceeded")
            return False

    print("\nPasswords Match.")
    print("User Registered.\n")

    database["User"] = {}
    database["User"][username] = {
        "Full_Name": full_name,
        "Password_Hash": passwd1,
        "Logins": 0,
        "Time": str(dt.datetime.now())
    }

    return True


def login(database:dict)->bool:
    '''Prompts user for username and password.
    Returns True on a successful login; False otherwise'''

    # Lockout_timer is the number of minutes a lockout lasts for
    # and also the amount of time you must wait between login attempts to
    # not increment the "logins" value.
    lockout_timer = 1 # TODO: make longer

    flag:bool = False
    while (flag == False):
        print("Login:")
        if (len(database) == 0):
            print("No users are registered with this client.")
            ques = input("Do you want to register a new user (y/n)?\n")
            if ((ques).lower() == 'y'):
                new_user(database)
            elif (ques.lower() == 'n'):
                flag = True
        else:
            ques = input("Do you want to register a new user (y/n)?\n")
            if ((ques).lower() == 'y'):
                new_user(database)
            elif (ques.lower() == 'n'):
                flag = True

    
    username = input("Enter Email Address: ").lower()

    # Check if username is in database
    try:
        database["User"][username]
    except KeyError:
        print("Invalid Email.")
        return False

    # If username has tried to login too many times in X amount of time
    # Lock them out
    if database["User"][username]["Logins"] > 5 and database["User"][username]["Time"] >= str(dt.datetime.now() - dt.timedelta(minutes=lockout_timer)):
        print("Account Locked: Too many login attempts!")
        return False

    # If username is in database, prompt for password
    password = get_password("Enter Password: ")

    if not comp_str(password, database["User"][username]["Password_Hash"]): # check if password entered matches the one connected with the user name(returns true or false)
        print("Try Again.") # returns false
        if database["User"][username]["Time"] >= str(dt.datetime.now() - dt.timedelta(minutes=lockout_timer)):
            database["User"][username]["Time"] = str(dt.datetime.now())
            database["User"][username]["Logins"] += 1
            return False
        # If last login was longer than lockout_timer minutes ago,
        # reset logins counter to 1
        else: # returns true
            database["User"][username]["Time"] = str(dt.datetime.now())
            database["User"][username]["Logins"] = 1
            return False

    # Name is in database; password is correct;
    # reset login attempts to 0
    database["User"][username]["Time"] = str(dt.datetime.now())
    database["User"][username]["Logins"] = 0
    return True


def secure_drop(database:dict)->None:
    print("Welcome to SecureDrop")
    print('Type "help" For Commands\n')

    while True:
        command = input("secure_drop> ").lower()
        if command in ACTION_LIST:
            actions(ACTION_LIST.index(command), database)
        else:
            print("Command Not recognized. Please try again.")


def actions(command:str, database:dict)->None:
    match ACTION_LIST[command]:
        case "help":
            print('\t"add" -> Add a new contact')
            print('\t"list" -> List all online contacts')
            print('\t"send" -> Transfer file to contact')
            print('\t"exit" -> Exit SecureDrop')
        case "add":
            full_name, email = get_name_and_email("\t")
            try:
                database["Contacts"].append([full_name, email])
            except KeyError:
                database["Contacts"] = []
                database["Contacts"].append([full_name, email])
        case "list": # TODO: flesh out later in semester
            try:
                for contact, email in database["Contacts"]:
                    print(f"\t* {contact} <{email}>")
            except KeyError:
                print("\tContact List Is Empty.")
            pass
        case "send":
            pass
        case "exit":
            print("Goodbye.")
            exit(0)

    
def get_name_and_email(indent="")->list:
    # Get Full Name
    full_name = input(f"{indent}Enter Full Name: ")
    # Get username/email
    # TODO: validate password via regex
    username = input(f"{indent}Enter Email Address: ").lower()

    return full_name, username
