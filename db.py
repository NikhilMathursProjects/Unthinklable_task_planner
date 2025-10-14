from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client["chatbot_db"]

users_col = db["users"]
chats_col = db["chat_sessions"]
messages_col = db["chat_messages"]
