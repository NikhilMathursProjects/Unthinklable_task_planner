from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import json
from pymongo import MongoClient
from datetime import datetime
import uuid

app = Flask(__name__)
uri=os.getenv("MONGO_URI")
database_name=os.getenv("MONGO_DATABASE")
collection_name=os.getenv("MONGO_COLLECTION")

#configure and get the collection
client=MongoClient(uri)
collection=client[database_name][collection_name]


# Configure Google Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_task_plan(goal: str) -> str:
    prompt = f"""
    You are an expert project planner. Your task is to decompose the following goal into a structured, realistic task plan.

    Each task should have:
    - A short, descriptive name
    - Dependencies (names of prerequisite tasks, if any)
    - An estimated number of days for completion

    The total timeline should align logically with the goal (for example, if the goal is 'Launch a product in 2 weeks', total estimated days ≈ 14).

    Output clean JSON ONLY in this format:
    [
      {{ "task": "Task name", "Explanation(How to do)": "Do something", "depends_on": [], "estimated_days": 3 }},
      {{ "task": "Next task", "Explanation(How to do)": "Do something", "depends_on": ["Task name"], "estimated_days": 2 }}
    ]

    Guidelines:
    - Keep task names clear and actionable (e.g., 'Design UI mockups' instead of 'UI design').
    - Ensure dependencies make sense (a task should not depend on a future task).
    - Balance timelines so they fit within the overall goal duration.
    - Avoid extra text, explanations, or markdown formatting.

    Goal: {goal}
    """
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content(prompt)
    return response.text


@app.post("/create_chat")
def create_chat():
    username = request.json.get("username")
    title = request.json.get("title", "New Chat")
    chat_id = f"chat_{uuid.uuid4().hex[:8]}"
    
    db.chat_history.insert_one({
        "username": username,
        "chat_id": chat_id,
        "title": title,
        "timestamp": datetime.utcnow().isoformat(),
        "messages": []
    })
    return jsonify({"chat_id": chat_id, "status": "created"})



# @app.route("/save_chat_history",methods=["POST"])
# def save_chat_history():



@app.route("/plan", methods=["POST"])
def plan():
    data = request.get_json()
    goal = data.get("goal", "")
    if not goal:
        return jsonify({"error": "Goal not provided"}), 400

    plan_text = generate_task_plan(goal)

    # Clean Gemini response (remove ```json wrappers)
    try:
        cleaned = plan_text.strip().replace("```json", "").replace("```", "").strip()
        plan_data = json.loads(cleaned)
    except Exception:
        plan_data = [{"task": "Could not parse Gemini output.", "depends_on": [], "estimated_days": 0}]

    # Build readable Markdown-style text
    readable_output = f"\nGoal: {goal}\n" + "=" * (6 + len(goal)) + "\n\n"
    for i, item in enumerate(plan_data, start=1):
        deps = ", ".join(item["depends_on"]) if item["depends_on"] else "None"
        readable_output += (
            f"{i}. {item['task']}\n"
            f"   • Depends on: {deps}\n"
            f"   • Estimated days: {item['estimated_days']}\n\n"
        )

    return jsonify({"goal": goal, "plan": readable_output})


if __name__ == "__main__":
    app.run(debug=True)



