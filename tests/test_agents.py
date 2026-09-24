from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(
    model=os.getenv('GROQ_MODEL'),
    api_key=os.getenv('GROQ_API_KEY')
)

response = model.invoke("hello world; passing this for testing the api key")

print(response.content)