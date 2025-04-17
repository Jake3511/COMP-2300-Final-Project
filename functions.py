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
    # try: # Check if username already in use
    #     if username in list(database["User"].values()):
    #         print("User Already Registered.")
    #         return True
    # except KeyError: # Catch if database is empty
    #     database["User"] = {}

    # print("User Registered.\n")

    # database["User"][username] = {
    #     "Full_Name": full_name,
    #     "Password_Hash": passwd1,
    #     "Logins": 0,
    #     "Time": str(dt.datetime.now())
    # }

    # return True


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

    email = user[0]

    # Lockout_timer is the number of minutes a lockout lasts for
    # and also the amount of time you must wait between login attempts to
    # not increment the "logins" value.
    lockout_timer = 1 # Leave as 1 min for testing and demo purposes

    if new:
        if email in list(database["User"].values()):
            return login_server(database, False, user, password)
        else:
            database["User"][email] = {}

            database["User"][email]["Password"] = password

            database["User"][email]["Time"] = str(dt.datetime.now())

            database["User"][email]["Logins"] = 1

            database["User"][email]["Contacts"] = {}

            return [True, "New User Added"]

    try:
        database["User"][email]
    except KeyError:
        return [False, "Invalid Email"]

    if database["User"][email]["Logins"] > 5 and database["User"][email]["Time"] >= str(dt.datetime.now() - dt.timedelta(minutes=lockout_timer)):
        return [False, "Account Locked: Too Many Log In Attempts!"]

    passwd_right = comp_str(password, database["User"][email]["Password"])

    if passwd_right:
        return [True, "Log In Successfully"]

    return [False, "Log In Failed"]

    # flag = False
    # while (flag == False):
    #     print("Login:")
    #     if (len(database) == 0):
    #         print("No users are registered with this client.")
    #         ques = input("Do you want to register a new user (y/n)?\n")
    #         if ((ques).lower() == 'y'):
    #             new_user(database)
    #         elif (ques.lower() == 'n'):
    #             flag = True
    #     else:
    #         ques = input("Do you want to register a new user (y/n)?\n")
    #         if ((ques).lower() == 'y'):
    #             new_user(database)
    #         elif (ques.lower() == 'n'):
    #             flag = True


    # username = input("Enter Email Address: ").lower()

    # # Check if username is in database
    # try:
    #     database["User"][username]
    # except KeyError:
    #     print("Invalid Email.")
    #     return False

    # # If username has tried to login too many times in [lockout_timer]
    # # amount of time lock them out
    # if database["User"][username]["Logins"] > 5 and database["User"][username]["Time"] >= str(dt.datetime.now() - dt.timedelta(minutes=lockout_timer)):
    #     print("Account Locked: Too many login attempts!")
    #     return False

    # # If username is in database, prompt for password
    # password = get_password("Enter Password: ")

    # if not comp_str(password, database["User"][username]["Password_Hash"]): # check if password entered matches the one connected with the user name(returns true or false)
    #     print("Try Again.") # returns false
    #     if database["User"][username]["Time"] >= str(dt.datetime.now() - dt.timedelta(minutes=lockout_timer)):
    #         database["User"][username]["Time"] = str(dt.datetime.now())
    #         database["User"][username]["Logins"] += 1
    #         return False
    #     # If last login was longer than lockout_timer minutes ago,
    #     # reset logins counter to 1
    #     else: # returns true
    #         database["User"][username]["Time"] = str(dt.datetime.now())
    #         database["User"][username]["Logins"] = 1
    #         return False

    # # Name is in database; password is correct;
    # # reset login attempts to 0
    # database["User"][username]["Time"] = str(dt.datetime.now())
    # database["User"][username]["Logins"] = 0

    # secure_drop(database, username)
    # return True


# def secure_drop(database:dict, username:str, command:str)->None:
#     print("Welcome to SecureDrop")
#     print('Type "help" For Commands')

#     if command in ACTION_LIST:
#         actions(ACTION_LIST.index(command), username, database)
#     else:
#         return [True, "Command Not recognized. Please try again."]


def actions_server(database:dict, command:int, username:str, data:list)->list:
    match ACTION_LIST[command]:
        case "add":
            email, full_name = data
            added_back = False
            try:
                try:
                    if database["User"][email]:
                        added_back = True
                        for _, user, added_back_bool in database["User"][email]["Contacts"]:
                            if email == user:
                                database["User"][email]["Contacts"][user][2] = True
                except KeyError:
                    added_back = False

                database["User"][username]["Contacts"].append([full_name, email, added_back])
                return [True, "Contact Added."]

            except KeyError:
                database["User"][username]["Contacts"] = []
                database["User"][username]["Contacts"].append([full_name, email, added_back])

        case "list": # TODO: add online test
            try:
                contacts = database["User"][username]["Contacts"]
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
                    return "No Contacts Added You Back"
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
