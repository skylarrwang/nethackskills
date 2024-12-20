import os
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")

response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": "what sort of information about NetHack do you have? can you give me information about all the different monster types and what should vs shouldn't be fought?",
        }
    ]
)

print(response.choices[0].message['content'])