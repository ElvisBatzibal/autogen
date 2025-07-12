import os
import httpx
from dotenv import load_dotenv
from datetime import datetime

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

async def fetch_messages_without_response():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/messages?intent=eq.consulta_pedido&order_checked=is.true",
            headers=supabase_headers
        )
        messages = response.json()

        # Filtrar solo mensajes que aún no tienen respuesta
        pending = []
        for msg in messages:
            check = await client.get(
                f"{SUPABASE_URL}/rest/v1/responses?message_id=eq.{msg['id']}",
                headers=supabase_headers
            )
            if not check.json():
                pending.append(msg)
        return pending

async def get_order(order_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/orders?order_id=eq.{order_id}",
            headers=supabase_headers
        )
        data = response.json()
        return data[0] if data else None

def build_prompt(order):
    return (
        f"Redacta una respuesta amable, breve y clara para un cliente que preguntó por el estado de su pedido.\n\n"
        f"Estado del pedido: {order['status']}\n"
        f"Fecha de envío: {order.get('shipped_date')}\n"
        f"Entrega estimada: {order.get('delivery_estimate')}\n\n"
        f"La respuesta debe ser cordial y profesional, como si fueras un agente de atención al cliente. Finaliza con Saludos cordiales. Equipo de Atención al Cliente.\n\n"
    )

async def generate_response(prompt: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=openai_headers,
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "Eres un agente de atención al cliente."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
        )
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

async def save_response(message_id: str, response_text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{SUPABASE_URL}/rest/v1/responses",
            headers=supabase_headers,
            json={
                "message_id": message_id,
                "agent_response": response_text,
                "sent_at": datetime.utcnow().isoformat()
            }
        )

async def main():
    messages = await fetch_messages_without_response()
    print(f"💬 Mensajes sin respuesta: {len(messages)}")

    for msg in messages:
        print(f"\n📝 Mensaje: {msg['message']}")
        # Extraer order_id del mensaje
        order_id = next((word for word in msg["message"].split() if "ORD" in word), None)
        if not order_id:
            print("⚠️  No se pudo detectar un order_id en el mensaje.")
            continue

        order = await get_order(order_id.strip('#'))
        if not order:
            print(f"❌ Pedido {order_id} no encontrado.")
            continue

        prompt = build_prompt(order)
        response_text = await generate_response(prompt)
        print(f"✅ Respuesta generada:\n{response_text}\n")

        await save_response(msg["id"], response_text)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())