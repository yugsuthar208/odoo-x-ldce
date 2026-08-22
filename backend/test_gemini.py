import os
from app.config import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

async def test_gemini_models():
    models = ["models/gemini-3.6-flash", "models/gemini-2.5-flash-lite", "models/gemini-flash-latest"]
    async with httpx.AsyncClient(timeout=30.0) as client:
        for m in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/{m}:generateContent?key={GEMINI_API_KEY}"
            try:
                res = await client.post(url, json={
                    "contents": [{"parts": [{"text": "You are Tripora AI. Output in 1 sentence your greeting to travelers."}]}]
                })
                print(f"{m} -> {res.status_code}")
                if res.status_code == 200:
                    print("Generated Output:", res.json()["candidates"][0]["content"]["parts"][0]["text"])
                    return m
            except Exception as e:
                print(f"Error {m}: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini_models())
