import os
import httpx
from dotenv import load_dotenv
from typing import List

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

supabase_headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

openai_headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

async def fetch_unclassified_messages():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/messages?intent=is.null", headers=supabase_headers)
        return r.json()

async def classify_message(text: str) -> str:
    prompt = (
        "Clasifica la siguiente consulta en una de estas intenciones:\n"
        "- consulta_pedido\n- devolucion\n- reclamo\n- compra\n- pregunta_general\n\n"
        f"Texto: \"{text}\"\nRespuesta (solo la intención):"
    )

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "Eres un clasificador de intenciones para atención al cliente."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    async with httpx.AsyncClient() as client:
        r = await client.post("https://api.openai.com/v1/chat/completions", headers=openai_headers, json=payload)
        completion = r.json()
        return completion["choices"][0]["message"]["content"].strip()

async def update_intent(message_id: str, intent: str):
    async with httpx.AsyncClient() as client:
        await client.patch(
            f"{SUPABASE_URL}/rest/v1/messages?id=eq.{message_id}",
            headers=supabase_headers,
            json={"intent": intent}
        )

async def run_classification_process():
    messages = await fetch_unclassified_messages()
    print(f"📝 Mensajes sin clasificar: {len(messages)}")

    for msg in messages:
        intent = await classify_message(msg["message"])
        print(f"🔍 Mensaje: {msg['message']}")
        print(f"✅ Intención detectada: {intent}")
        await update_intent(msg["id"], intent)

async def main():
    await run_classification_process()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())