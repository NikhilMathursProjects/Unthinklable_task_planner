so this function helps the user get an answer back while also storing the data simultaneously with the query and answer together, tell me if this is fine
def answer_user_query():
    #gets data in terms of 1 user query along with their username and chatid and whatever else is required to save to the db
    the query is checked to ensure no issue and is not null (this will also be checked in frontend etc)
    then we pass this query with the prompt to the llm and get the answer back in terms of some json, which is fine, i have the code to make it look proper here:
    readable_output = f"\nGoal: {goal}\n" + "=" * (6 + len(goal)) + "\n\n"
    for i, item in enumerate(plan_data, start=1):
        deps = ", ".join(item["depends_on"]) if item["depends_on"] else "None"
        readable_output += (
            f"{i}. {item['task']}\n"
            f"   • Depends on: {deps}\n"
            f"   • Estimated days: {item['estimated_days']}\n\n"
        )
    Now i add to the chat history for this particular chatid, the user query and the llm answer, with the timestamp and everything else thats required, you can tell me what more is needed etc.
    Then i return the json string of answer to the frontend basically

def show_all_chats()
    takes data in the form of the username and returns all chatids, names etc

def retrive_n_prev_chats()
    takes some data as username and chatid etc and returns the most recent n chats for that user and chatid so that the user can see the chats, also tell me how to dynamically load more chats, maybe thats upto the frontend but tell memoryview

def create_new_chat()
    data is username and chat name if given else 'NewChat'+uuid or whatever to make it unique ,whatever is the best way to ensure that we can create new chats and use them etc

this is all the pseudocode that i know, tell me if this is possible to implement