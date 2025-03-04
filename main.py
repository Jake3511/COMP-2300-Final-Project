import datetime as dt
import json
import base64
import bcrypt


# Optional "LockOut" Exception
class LockOut(Exception):
    def __init__(self, message):
        super().__init__(message)

def get_hashed_password(password):
    '''Gets password from parameter;
    Hashes password;
    Returns password hash'''

    password = password.encode('utf-8') # 
    salt = salt = bcrypt.gensalt() # used to generate a random number
    hashed_password = bcrypt.hashpw(password, salt) # hashed the password using the generated number(salt)
    return base64.b64encode(hashed_password).decode('utf-8') 
    # return password in json formatted string (was giving me an error when tried to save binary string in json format)

def check_hash(password, hashed_password):
    password = password.encode('utf-8')

    stored_hash_bytes = base64.b64decode(hashed_password) # decoded the hashed password back into binary format to compare with hashed password in database

    print(stored_hash_bytes)
    return bcrypt.checkpw(password, stored_hash_bytes) # returns a bool type that checks if password in database is equal to the password entered

def update_database(database: dict) -> None:
    '''Update the database with new information'''
    file = open("database.json", "w")
    json_database = json.dumps(database, indent=4)
    file.write(json_database)
    file.close()

def login() -> bool:
    '''Prompts user for username and password.
    Returns True on a successful login; False otherwise'''

    # lockout_timer is the number of minutes a lockout lasts for
    # and also the amount of time you must wait between login attempts to
    # not increment the "logins" value.
    lockout_timer = 1

    # Get Full Name
    full_name = input("Enter Full Name: ")
    # Get username
    username = input("Enter username\n>> ")

    # Check if username is in database
    try:
        database[username]
        # If username has tried to login too many times in X amount of time
        # Lock them out
        if database[username]["logins"] > 5 and database[username]["time"] >= str(dt.datetime.now() - dt.timedelta(minutes=lockout_timer)):
            print("Account Locked: Too many login attempts!")
            return False
        # If username is in database, prompt for password

        password = input("Enter your password\n>> ") # Moved the print statement here because of some errors I was getting

        if not check_hash(password, database[username]["password_hash"]): # check if password entered matches the one connected with the user name(returns true or false)
            print("Try again.") # returns false
            if database[username]["time"] >= str(dt.datetime.now() - dt.timedelta(minutes=lockout_timer)):
                database[username]["time"] = str(dt.datetime.now())
                database[username]["logins"] += 1
                update_database(database)
                return False
            # If last login was longer than lockout_timer minutes ago,
            # reset logins counter to 1
            else: # returns true
                database[username]["time"] = str(dt.datetime.now())
                database[username]["logins"] = 1
                update_database(database)
                return False
    # If username is not in database, prompt for password;
    # then add username and password to database
    except KeyError:
        password = get_hashed_password(input("Enter your password\n>> ")) # Moved another input statement here for the same error I was getting before
        print(password) # used for testing
        database[username] = {"password_hash": password,
                          "logins": 0,
                          "time": str(dt.datetime.now())}
        update_database(database)
        return False


    # Name is in database; password is correct;
    # reset login attempts to 0
    database[username]["logins"] = 0
    update_database(database)
    return True


#########
# Start #
#########
if __name__ == "__main__":
    # empty database
    database = {}

    while True:
        if not database.keys():
            new_user(database)
        elif login(database):
            # TODO: do stuff once logged in
            break


