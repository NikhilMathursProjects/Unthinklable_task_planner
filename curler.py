import requests
import time
# # data = {"goal": "Launch a product in 2 weeks"}
url = "http://127.0.0.1:5000/create_chat"
data={'user_id':'119','chat_name':'This chat is something tbh'}
res = requests.post(url, json=data)

# url="http://127.0.0.1:5000/get_chats"
# data={'user_id':'1234'}
# res=requests.post(url,json=data)

# url= "http://127.0.0.1:5000/answer_query"
# data={'user_id':'1234','chat_id':'09d1ad82-5127-4f61-a941-7358a04e9f59','query':'Can you tell me how to learn Data Structures and Algorithms for Leetcode'}
# start=time.time()
# res=requests.post(url,json=data)


# url= "http://127.0.0.1:5000/get_messages"
# data={'user_id':'1234','chat_id':'09d1ad82-5127-4f61-a941-7358a04e9f59','n':3}
# start=time.time()
# res=requests.post(url,json=data)
# print("Time Taken:",time.time()-start)

print("Status:", res.status_code)
print("Text:", res.text)
# print("JSON:", len(res.json()['chats']) if res.headers.get('Content-Type') == 'application/json' else "Not JSON")
print("JSON:", res.json() if res.headers.get('Content-Type') == 'application/json' else "Not JSON")

