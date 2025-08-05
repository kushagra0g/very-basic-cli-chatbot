from openai import OpenAI
import db
import utils
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(
    api_key = os.getenv("key"),
    base_url = r"https://generativelanguage.googleapis.com/v1beta/openai/"
    )

model_preference_dictionary = {
                                0 : "gemini-2.0-flash-lite-001",
                                1 : "gemini-2.0-flash",
                                2 : "gemini-2.5-flash-preview-04-17"
                                }

# This function will generate a response, and append it to the conversation history. Then proceed to return the list.
def get_response_and_append(conversation_history, model_preference):
    try:
        model = model_preference_dictionary.get(model_preference)
        response = client.chat.completions.create(
            model=model,
            messages=conversation_history
        )
        response_content = response.choices[0].message.content
        timestamp = utils.get_timestamp()
        # Appending the response in the conversation history. With timestamps and role.
        conversation_history.append({"role" : "assistant",
                                     "content" : response_content,
                                     "timestamp" : timestamp
                                     })

    except Exception as e:
        print("error occurred. : " + str(e))

    finally:
        return conversation_history

def conversation_loop(conversation_history):
    print("You have successfully started the conversation. If you want to talk to a specific model, input 'specific'.\n"
          "Either, to continue with the default model, press Enter.")
    model_choice = input().lower()
    model_preference = 0

    # Choosing specific model logic
    if model_choice=="specific":
        print("available model choices : ")
        print(model_preference_dictionary)
        print("Input the index number of the model you want to use.")
        model_preference = int(input())
        # If index number exceeds the number of models available in the dictionary.
        if model_preference>len(model_preference_dictionary):
            print("Invalid index number. Default model is selected. Restart the conversation to change the model.")

    # Code to handle the case where conversation history is empty, since it would require adding a system prompt.
    if not conversation_history:
        sys_prompt = input("System prompt : ")
        timestamp = utils.get_timestamp()
        conversation_history.append({
                                    "role" : "system",
                                    "content" : sys_prompt,
                                    "timestamp" : timestamp
                                    })

    print("Start the conversation! To exit, input exit/quit.")
    while True:
        # Get user input
        user_response = input("User : ")
        # Exit / Break logic
        if user_response.lower() == "exit" or user_response.lower() == "quit":
            print("You have successfully left the conversation.")
            break
        timestamp = utils.get_timestamp()

        # Appending user response into conversation_history
        conversation_history.append({
                                    "role" : "user",
                                    "content" : user_response,
                                    "timestamp" : timestamp
                                    })
        # Getting the new conversation history, with the latest assistant response.
        conversation_history = get_response_and_append(conversation_history, model_preference)

        # Printing the latest response, assumption that latest response will be of the assistant.
        print("Assistant : " + conversation_history[-1]['content'])
    return conversation_history

def login_or_signup():
    while True:
        choice = input("Do you want to login, or signup? Input (login/signup) : ").lower()
        if choice == "login":
            username = db.login()
            return username
        elif choice == "signup":
            db.signup()
        else:
            print("Invalid input. Try again.")
def main():
    username = login_or_signup()
    conversation_history, user_choice = db.loading_conversation_history(username)
    conversation_history = conversation_loop(conversation_history)
    db.save_conversation(username, conversation_history, user_choice)
    print("Hope you have a great day! Come back soon.")


main()