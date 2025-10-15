from flask import Flask, request, jsonify
from bson import ObjectId
from datetime import datetime
import google.generativeai as genai
from uuid import uuid4
import os
import json
from db import users_col, chats_col, messages_col
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# ------------------  Helper Function ------------------
# def generate_llm_answer(goal):
#     prompt = f"""
#     You are an expert project planner. Break down this goal into actionable tasks.

#     Each task should include:
#     - A short name
#     - Dependencies
#     - Estimated days
#     Return clean JSON only:
#     [
#       {{ "task": "Task name", "depends_on": [], "estimated_days": 2 }}
#     ]
#     Goal: {goal}
#     """
#     model = genai.GenerativeModel("gemini-2.0-flash-lite")
#     response = model.generate_content(prompt)
#     return response.text


def generate_task_plan(goal: str) -> str:
    # prompt = f"""
    # You are an expert project planner. Your task is to decompose the following goal into a structured, realistic task plan.

    # Each task should have:
    # - A short, descriptive name
    # - Dependencies (names of prerequisite tasks, if any)
    # - An estimated number of days for completion

    # The total timeline should align logically with the goal (for example, if the goal is 'Launch a product in 2 weeks', total estimated days ≈ 14).

    # Output clean JSON ONLY in this format:
    # [
    #   {{ "task": "Task name", "Explanation(How to do)": "Do something", "depends_on": [], "estimated_days": 3 }},
    #   {{ "task": "Next task", "Explanation(How to do)": "Do something", "depends_on": ["Task name"], "estimated_days": 2 }}
    # ]

    # Guidelines:
    # - Keep task names clear and actionable (e.g., 'Design UI mockups' instead of 'UI design').
    # - Ensure dependencies make sense (a task should not depend on a future task).
    # - Balance timelines so they fit within the overall goal duration.
    # - Avoid extra text, explanations, or markdown formatting.

    # Goal: {goal}
    # """
    prompt = f"""
    You are an expert project planner. Break down this goal into actionable tasks.

    Each task should include:
    - A short name
    - Dependencies
    - Estimated days
    Return clean JSON only:
    [
      {{ "task": "Task name","Explanation(How to do)": "Do something", "depends_on": [], "estimated_days": 2 }}
    ]
    Goal: {goal}
    """
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content(prompt)
    return response.text

@app.route("/sign_up",methods=["POST"])
def sign_up():
    data=request.get_json()
    user_id=data.get("user_id")
    #creates a new chat and saves the new default chat to mongodb
    chat_name=f"NewChat_{uuid4().hex[:6]}"
    chat_doc = {
        "chat_id": str(uuid4()), #random uuid for chatid
        "user_id": user_id,
        "title": chat_name,
        "created_at": datetime.utcnow().isoformat()
    }
    #inserts the chat document into the chats collection, which holds just the chats data for all users
    chats_col.insert_one(chat_doc)
    chat_doc["_id"] = str(chat_doc["_id"])
    return jsonify({"message":"User Created",'user_id':user_id})


@app.route("/login",methods=["POST"])
def login_user():
    data=request.get_json()
    user_id=data.get("user_id")
    doc=chats_col.find_one({'user_id':user_id})
    if not doc:
        return jsonify({"Message":"There is no user, please sign up"})
    return jsonify({"message":"User Logged In",'user_id':doc['user_id']})

#new chat creator
@app.route("/create_chat", methods=["POST"])
def create_chat():
    """
    This function creates a new chat for our user with a `user_id` , it will contain nothing but just exist until a user inputs some query and the LLM answers it.
    Data requires:
    - `user_id`
    - `chat_name` or None

    """
    data = request.get_json()
    user_id = data.get("user_id")
    chat_name = data.get("chat_name", f"NewChat_{uuid4().hex[:6]}") #this newchat with uuid creates a random chatname instead of a chosen one

    #if no user
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    chat_doc = {
        "chat_id": str(uuid4()), #random uuid for chatid
        "user_id": user_id,
        "title": chat_name,
        "created_at": datetime.utcnow().isoformat()
    }
    #inserts the chat document into the chats collection, which holds just the chats data for all users
    chats_col.insert_one(chat_doc)
    chat_doc["_id"] = str(chat_doc["_id"])
    return jsonify({"message": "Chat created", "chat": chat_doc}), 201


#LLM answers user query
@app.route("/answer_query", methods=["POST"])
def answer_user_query():
    """
    Requires:
    - `user_id`
    - `chat_id`
    - `query`
    """
    data = request.get_json()
    user_id = data.get("user_id")
    chat_id = data.get("chat_id")
    query = data.get("query")

    if not all([user_id, chat_id, query]):
        return jsonify({"error": "user_id, chat_id, and query required"}), 400

    # Get LLM answer
    raw_answer = generate_task_plan(query)

    #cleans JSON if any formatting exists
    cleaned = raw_answer.strip().replace("```json", "").replace("```", "").strip()
    try:
        plan_data = json.loads(cleaned)
        readable_output = f"\nGoal: {query}\n" + "=" * (6 + len(query)) + "\n\n"
        for i, item in enumerate(plan_data, start=1):
            deps = ", ".join(item.get("depends_on", [])) if item.get("depends_on") else "None"
            readable_output += (
                f"{i}. {item['task']}\n"
                f"   • Depends on: {deps}\n"
                f"   • Estimated days: {item.get('estimated_days', '?')}\n\n"
            )
    except:
        readable_output = raw_answer

    #stores both the query and the llm answer in the mongodb messages_col (message collection)
    messages = [
        {
            "chat_id": chat_id,
            "user_id": user_id,
            "sender": "user",
            "message": query,
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "chat_id": chat_id,
            "user_id": user_id,
            "sender": "bot",
            "message": readable_output,
            "timestamp": datetime.utcnow().isoformat()
        }
    ]

    messages_col.insert_many(messages)

    return jsonify({"answer": readable_output})


#returns all chats
@app.route("/get_chats", methods=["POST"])
def show_all_chats():
    """
    Requires the users `user_id`
    """
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    #finds list of all chats (the newchat etc )
    chats = list(chats_col.find({"user_id": user_id}, {"_id": 0}))
    return jsonify({"chats": chats})


#gets the prev n messages
@app.route("/get_messages", methods=["POST"])
def retrieve_previous_messages():
    """
    Requires the users user_id, chat_id and n, so that we can retrieve the past messages for that chat and retrieve some `n` messages (which include the llm answer and user query)
    """
    data = request.get_json()
    user_id=data.get("user_id")
    chat_id = data.get("chat_id")
    n = int(data.get("n", 10))  # default 20 messages
    n=n*2 #to ensure that i always get pairs back
    if not chat_id:
        return jsonify({"error": "chat_id required"}), 400

    messages = (
        messages_col.find({"user_id":user_id,"chat_id": chat_id}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(n)
    )
    # Reverse so earliest message appears first
    # messages = list(messages)[::-1]
    messages=list(messages)

    return jsonify({"messages": messages})


if __name__ == "__main__":
    app.run(debug=True,use_reloader=False, port=5000)
