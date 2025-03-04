import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Test message, respond with 'Working' please."}
    ],
    max_tokens=50
)

print(response.choices[0].message.content.strip())
