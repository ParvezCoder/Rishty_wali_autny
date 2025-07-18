import os
import streamlit as st
import asyncio
import requests
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool
# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    st.error("❌ API key missing. Please set your GEMINI_API_KEY in .env file.")
    st.stop()
# Setup external client and model
external_client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=gemini_api_key
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)
# Tool function: Male users
@function_tool
def get_user_data_male(min_age: int, job_required: str = "Doesn't Matter", car_required: str = "Doesn't Matter", min_balance: int = 0) -> list[dict]:
    users = [
        {"name": "Muneeb", "gender": "male", "age": 22, "Job": "Yes", "Gari/car": "Yes", "Home": "Yes", "Bank_balance": 1130000},
        {"name": "Parvez Ahmed", "gender": "male", "age": 25, "Job": "Yes", "Gari/car": "Yes", "Home": "Yes", "Bank_balance": 1130000},
        {"name": "Hadi khan", "gender": "male", "age": 32, "Job": "No", "Gari/car": "yes", "Home": "No", "Bank_balance": 1300},
        {"name": "Azan", "gender": "male", "age": 19, "Job": "No", "Gari/car": "no", "Home": "Yes", "Bank_balance": 400000},
    ]

    def match(user):
        if user["age"] < min_age:
            return False
        if job_required != "Doesn't Matter" and user["Job"].lower() != job_required.lower():
            return False
        if car_required != "Doesn't Matter" and ("yes" not in user["Gari/car"].lower() if car_required == "Yes" else "no" not in user["Gari/car"].lower()):
            return False
        if user["Bank_balance"] < min_balance:
            return False
        return True

    return [user for user in users if match(user)]

# Tool function: Female users
@function_tool
def get_user_data_female(min_age: int, job_required: str = "Doesn't Matter", car_required: str = "Doesn't Matter", min_balance: int = 0) -> list[dict]:
    users = [
        {"name": "Sana", "gender": "Female", "age": 22, "Job": "Yes", "Gari/car": "no", "Home": "Yes", "Bank_balance": 2000},
        {"name": "Muskan", "gender": "Female", "age": 31, "Job": "Yes", "Gari/car": "yes / having V8 car", "Home": "Yes", "Bank_balance": 1500},
        {"name": "Areeba", "gender": "Female", "age": 35, "Job": "Yes", "Gari/car": "no", "Home": "Yes", "Bank_balance": 1130000},
        {"name": "Nimra", "gender": "Female", "age": 45, "Job": "Yes", "Gari/car": "yes / having V8 car", "Home": "Yes", "Bank_balance": 1130000},
        {"name": "Mehik", "gender": "Female", "age": 19, "Job": "no", "Gari/car": "no", "Home": "no", "Bank_balance": 600},
    ]

    def match(user):
        if user["age"] < min_age:
            return False
        if job_required != "Doesn't Matter" and user["Job"].lower() != job_required.lower():
            return False
        if car_required != "Doesn't Matter" and ("yes" not in user["Gari/car"].lower() if car_required == "Yes" else "no" not in user["Gari/car"].lower()):
            return False
        if user["Bank_balance"] < min_balance:
            return False
        return True

    return [user for user in users if match(user)]

# Setup the Agent
agent = Agent(
    name="Auntie",
    instructions="You are a warm and wise 'Rishtey Wali Auntie' who helps people find matches.",
    model=model,
    tools=[get_user_data_male, get_user_data_female]
)

# Set Streamlit UI configuration
st.set_page_config(page_title="🤝 Rishtey Wali Auntie", layout="centered")

# UI Layout
# Set Streamlit UI configuration
st.set_page_config(page_title="🤝 Rishtey Wali Auntie", layout="centered")

# UI Layout with image on right and text on left
left_col, right_col = st.columns([2, 1])  # 2:1 ratio for better spacing

with left_col:
    st.markdown("<h2>💍 Rishtey Wali Auntie</h2>", unsafe_allow_html=True)

with right_col:
    st.image("marraige.png", use_container_width=True)


# Step 1: Get User Info
st.subheader("🧍‍♂️ Step 1: Your Information")
user_name = st.text_input("Your Name")

user_whatsapp = st.text_input("WhatsApp Number (with country code)", placeholder="+923001234567")
# Step 2: Match Requirements
st.subheader("🔍 Step 2: Your Match Requirements")
looking_for_gender = st.selectbox("You are looking for a:", ["Male", "Female"])  # 👈 NEW
required_age = st.number_input("Minimum Age", min_value=18, max_value=100, step=1)
job_required = st.selectbox("Should they have a job?", ["Doesn't Matter", "Yes", "No", ])
car_required = st.selectbox("Should they have a car?", ["Doesn't Matter", "Yes", "No", ])
min_balance = st.number_input("Minimum Bank Balance (PKR)", min_value=0)
result_formate = st.selectbox("Aap ko result kis format mein chahiye?", [",", "Result Should be in Tabular formate", "Result Should be in Number-wise, 1,2,3... ", "Result Should be in Bullet formate"])
# result_formate = st.text_input("Aap ko result kis format mein chahiye?  Number-wise/ Tabular form / Bullet points")
# Final user query string for Auntie
user_input = (
    f"Show me {looking_for_gender.lower()} rishtas where age >= {required_age}, "
    f"job = {job_required}, car = {car_required}, bank balance >= {min_balance}, "
    f"{result_formate}, "
)


# Button to trigger the match search
if st.button("💌 Find Rishtay"):
    if not user_name or not user_whatsapp:
        st.warning("Please enter your name and WhatsApp number.")
    else:
        with st.spinner("Auntie is thinking... 💭"):
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            response = loop.run_until_complete(Runner.run(agent, user_input))
            final_output = response.final_output

            # Combine everything into a WhatsApp message
            message = f"👤 Name: {user_name}\n📞 WhatsApp: {user_whatsapp}\n🧑‍🤝‍🧑 Requirements:\n{user_input}\n\n📋 Auntie's Matches:\n{final_output}"

            # Show on UI
            st.success("Auntie's Response:")
            st.markdown(final_output)

            # Send result to user's WhatsApp
            contact_no = user_whatsapp  # 👈 Send to the user's own number
            url = "https://api.ultramsg.com/instance132604/messages/chat"
            token = "duzf89ptksqonyvp"
            payload = f"token={token}&to={contact_no}&body={message}"
            payload = payload.encode('utf8').decode('iso-8859-1')
            headers = {'content-type': 'application/x-www-form-urlencoded'}

            try:
                whatsapp_response = requests.post(url, data=payload, headers=headers)
                if whatsapp_response.status_code == 200:
                    st.success("✅ Response sent to your WhatsApp!")
                else:
                    st.error(f"❌ WhatsApp Error: {whatsapp_response.text}")
            except Exception as e:
                st.error(f"📴 Failed to send WhatsApp message: {e}")
