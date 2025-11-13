import os
import openai

api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    print("❌ OPENAI_API_KEY is not set in environment.")
else:
    print("✅ OPENAI_API_KEY found. Testing access to OpenAI...")

    openai.api_key = api_key

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, who are you?"}
            ]
        )
        print("✅ API Key works!")
        print("Response:", response.choices[0].message.content)

    except Exception as e:
        print("❌ API Key is invalid or request failed.")
        print("Error:", e)
