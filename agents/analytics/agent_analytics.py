import os
import httpx
from dotenv import load_dotenv
from collections import Counter
from datetime import datetime, timezone

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer " + SUPABASE_API_KEY,
    "Content-Type": "application/json"
}

async def fetch_all_intents():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/messages?select=intent",
            headers=headers
        )
        messages = response.json()
        intents = [msg["intent"] for msg in messages if msg["intent"]]
        return intents

async def save_analytics(summary_date: str, intent_summary: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{SUPABASE_URL}/rest/v1/analytics",
            headers=headers,
            json={
                "summary_date": summary_date,
                "top_intents": intent_summary,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        )

async def main():
    intents = await fetch_all_intents()
    counts = dict(Counter(intents))
    print(f"📊 Resumen de intenciones del día: {counts}")

    today = datetime.now(timezone.utc).date().isoformat()
    await save_analytics(today, counts)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())