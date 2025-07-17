import os
import requests
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool
from dotenv import load_dotenv
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Key Kam nhn kr rahi, use set kro")

external_client = AsyncOpenAI(
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key = gemini_api_key
)

model = OpenAIChatCompletionsModel(
    model = "gemini-2.5-flash",
    openai_client= external_client
)
# ///////////////////////////////////////////////////////////////////////////////
@function_tool
def get_user_data(min_age: int) -> list[dict]:
    "Retrieve user data based on a minimum age"
    users = [
        {"name": "Muneeb", "age": 22},
        {"name": "Muhammad Ubaid Hussain", "age": 25},
          {"name": "Hadi khan", "age": 32},
        {"name": "Azan", "age": 19},]
    for user in users:
        if user["age"] < min_age:
            users.remove(user)
    return users

# ////////////////////////////////////////////////////////////////////////////////
agent = Agent(
    name="Auntie",
    instructions="You are a warm and wise 'Rishtey Wali Auntie' who helps people find matches",
    model=model,
    tools=[get_user_data]
)
data = input("Enter your requirment: ")
response = Runner.run_sync(agent, data)
print (response.final_output)


contact_no = +923052887779
url = "https://api.ultramsg.com/instance132604/messages/chat"
payload = f"token=duzf89ptksqonyvp&to={contact_no}&body={response.final_output}"
payload = payload.encode('utf8').decode('iso-8859-1')
headers = {'content-type': 'application/x-www-form-urlencoded'}

response = requests.request("POST", url, data=payload, headers=headers)