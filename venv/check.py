import os
import google.generativeai as genai

# Environment variable se API key lena
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content("Hello! Jow are you?")

print(response.text)

