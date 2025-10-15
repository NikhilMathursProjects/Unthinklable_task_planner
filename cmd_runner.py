import requests

BASE_URL = "http://127.0.0.1:5000"

def sign_up()->str:
    """simple sign up"""
    user_id=input("Enter your User ID:").strip()
    if not user_id:
        print("User id cannot be NULL")
        return sign_up()
    url=f"{BASE_URL}/login"
    data={'user_id':user_id}
    res=requests.post(url,json=data)
    print(f"{res.json()['message']} with user id: {user_id}")
    return user_id

def login() -> str:
    """Simple login by entering user_id."""
    user_id = input("Enter your User ID: ").strip()
    if not user_id:
        print("User ID cannot be empty!")
        return login()
    #passing to /login
    url=f"{BASE_URL}/login"
    data={'user_id':user_id}
    res=requests.post(url,json=data)
    print(f"{res.json()['message']} with user_id: {user_id}")
    return user_id

def create_new_chat(user_id: str) -> tuple[str, str]:
    """Create a new chat session."""
    chat_name = input("Enter chat name (or press Enter for default): ").strip() or None
    url = f"{BASE_URL}/create_chat"
    data = {"user_id": user_id, "chat_name": chat_name}
    try:
        res = requests.post(url, json=data)
        res.raise_for_status()
        chat = res.json()["chat"]
        print(f"Chat '{chat['title']}' created with Chat ID: {chat['chat_id']}")
        return chat["chat_id"], chat["title"]
    except Exception as e:
        print(f"Error creating chat: {e}")
        return None, None

def list_and_select_chat(user_id: str) -> tuple[str, str]:
    """List all chats and allow the user to select one."""
    url = f"{BASE_URL}/get_chats"
    try:
        res = requests.post(url, json={"user_id": user_id})
        res.raise_for_status()
        chats = res.json().get("chats", [])
        if not chats:
            print("No chats found.")
            return None, None
        print("\nYour chats:")
        for i, chat in enumerate(chats, 1):
            print(f"{i}. {chat['title']} (ID: {chat['chat_id']})")
        # Ask user to select
        while True:
            choice = input("Select chat number: ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(chats):
                    chat = chats[idx]
                    print(f"Selected Chat: {chat['title']} (ID: {chat['chat_id']})")
                    return chat["chat_id"], chat["title"]
                else:
                    print("Invalid selection, try again.")
            except ValueError:
                print("Enter a valid number.")
    except Exception as e:
        print(f"Error fetching chats: {e}")
        return None, None

def ask_query(user_id: str, chat_id: str):
    """Ask a question to the chatbot."""
    query = input("Your question: ").strip()
    if not query:
        print("Query cannot be empty!")
        return
    url = f"{BASE_URL}/answer_query"
    data = {"user_id": user_id, "chat_id": chat_id, "query": query}
    try:
        res = requests.post(url, json=data)
        res.raise_for_status()
        answer = res.json().get("answer", "No answer received")
        print("\nChatbot Answer:\n" + answer + "\n")
    except Exception as e:
        print(f"Error asking query: {e}")

def fetch_previous_messages(user_id: str, chat_id: str, n: int = 5):
    """Fetch last N message pairs from the chat."""
    url = f"{BASE_URL}/get_messages"
    data = {"user_id": user_id, "chat_id": chat_id, "n": n}
    try:
        res = requests.post(url, json=data)
        res.raise_for_status()
        messages = res.json().get("messages", [])
        print("\nLast messages:\n")
        for msg in messages:
            sender = "You" if msg["sender"] == "user" else "Bot"
            print(f"{sender}: {msg['message']}")
    except Exception as e:
        print(f"Error fetching messages: {e}")

def run_terminal_chatbot(user_id: str):
    """Main loop for terminal-based chatbot."""
    chat_id = None
    chat_name = None

    while True:
        print("\nMenu:")
        print("1. New Chat")
        print("2. List & Select Chat")
        print("3. Ask Query")
        print("4. Show Last Messages")
        print("5. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            chat_id, chat_name = create_new_chat(user_id)
        elif choice == "2":
            chat_id, chat_name = list_and_select_chat(user_id)
        elif choice == "3":
            if not chat_id:
                print("No chat selected. Create or select a chat first.")
                continue
            ask_query(user_id, chat_id)
        elif choice == "4":
            if not chat_id:
                print("No chat selected. Create or select a chat first.")
                continue
            print("How many messages ago would you like to see ?")
            n=int(input())
            fetch_previous_messages(user_id, chat_id, n)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    user_id = login()
    run_terminal_chatbot(user_id)
