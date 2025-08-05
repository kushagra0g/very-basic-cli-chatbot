import sqlite3
import utils
import bcrypt
import pickle



db = "database.db" # database path
conn = sqlite3.connect(db) # if database path is not valid, sqlite3 creates a database in the root directory.
c = conn.cursor()
def create_table():
    c.execute("""CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username text UNIQUE NOT NULL,
        email text UNIQUE NOT NULL,
        first_name text,
        last_name text,
        password blob NOT NULL,
        timestamp text,
        conversations blob
        )""")
    commit()

# Hashing the password to store it in the database.
def hash_password(password):
    password = password.encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed

# Code block to execute a signup process
def signup():
    print("You have chosen to signup.")
    username, first_name, last_name, email = "", "", "", ""
    try :
        while True:
            username = input("Enter your desired username.\n")
            email = input("Enter your email\n")
            first_name = input("Enter your first name\n")
            last_name = input("Enter your last name\n")
            c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
            if c.fetchone() is not None:
                print("Entered username or email is already in use. Try again.")
                continue
            else:
                while True:
                    password = input("Input a password : ")
                    confirm_password = input("Confirm your password : ")
                    if password != confirm_password:
                        print("They are not the same, try again.")
                        continue
                    elif password == confirm_password:
                        break
                password = hash_password(password)
                timestamp = utils.get_timestamp()
                c.execute("INSERT INTO users (username, email, first_name, last_name, password, timestamp, conversations) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (username, email, first_name, last_name, password, timestamp, None))
                commit()
                print("You have successfully signed up! Now kindly proceed to login.")
                break

    except Exception as e:
        print("Error occurred. : " + str(e))

# Login code
def login():
     while True:
        username = input("Enter your username.\n")

        # Handling invalid username case
        c.execute("SELECT * FROM users WHERE username = ? ", (username, ))
        user_data = c.fetchone()
        if user_data is None:
            print("Username does not exist, try again.")
            continue
        elif user_data is not None:
            original_hash = user_data[5]
            password = input("Enter your password.\n").encode('utf-8')
            if bcrypt.checkpw(password, original_hash):
                print("You are successfully logged in!")
                return username
            elif bcrypt.checkpw(password, original_hash) is False:
                print("Incorrect password. Try again.")
                continue

# Function to load previous conversations.
def loading_conversation_history(username):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_data = c.fetchone()
    conversation_history_all = user_data[7]
    if conversation_history_all is None:
        return [], (0,0)
    elif conversation_history_all is not None:
        conversation_history_all = pickle.loads(conversation_history_all)
        print(f"You currently have {len(conversation_history_all)} conversations. Do you want to choose or go with the default?")
        user_choice = input("To go with the latest conversation, press enter.\n"
                            "To start a new conversation, input 'new'.\n"
                            "To print out all your conversations, input 'print'.\n").lower()
        if user_choice == "print":
            index = 0
            for conversation in conversation_history_all:
                print(f"{index}. convo : {conversation}")
                index+=1
            user_choice = int(input("Enter the index of the conversation you want to continue. : "))
            # Returns a specific conversation, with a tuple of the user choice and the number of total conversations the user has.
            return conversation_history_all[user_choice], (user_choice, len(conversation_history_all))
        elif user_choice == "new":
            return [], (100, len(conversation_history_all))
        else:
            return conversation_history_all[-1], (-1, len(conversation_history_all))

def save_conversation(username, conversation_history, user_choice):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_data = c.fetchone()
    # Case where conversation history is empty.
    if user_choice[0] == 0:
        conversation_history_all = [conversation_history]

    # Case where user chose to continue his latest conversation
    elif user_choice[0] == -1:
        conversation_history_all = user_data[7]
        conversation_history_all[-1] = conversation_history

    # Case where user wanted to start a new conversation
    elif user_choice[0] == 100:
        conversation_history_all = user_data[7]
        conversation_history_all.append(conversation_history)

    # Case where user chose to continue a specific conversation
    else:
        conversation_history_all = user_data[7]
        conversation_history_all[user_choice[0]] = conversation_history

    # Updating the database
    pickled_convo = pickle.dumps(conversation_history_all)
    c.execute("""UPDATE users SET conversations = ?
                WHERE username = ?
                """, (pickled_convo, username))

    commit()
def commit():
    conn.commit()