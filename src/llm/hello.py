import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
api_key = os.getenv("LLM_API_KEY")
model = os.getenv("LLM_MODEL", "openrouter/free")

client = OpenAI(base_url=base_url, api_key=api_key)

res = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Reply with exactly the word: ready"}],
)
print(res.choices[0].message.content)
