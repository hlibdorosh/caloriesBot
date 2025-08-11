# openai_utils.py
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def chat_with_openai(message: str):
    try:
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = await client.chat.completions.create(
            model="gpt-4", # или gpt-4-0613 / gpt-4-turbo
        messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка: {str(e)}"
