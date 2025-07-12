import os
import httpx
import re
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

async def fetch_messages_to_process():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/messages?intent=eq.consulta_pedido&order_checked=is.false",
            headers=headers
        )
        return response.json()

def extract_order_id(text: str) -> str | None:
    match = re.search(r'(?:#?\s*ORD\s*\d{4})', text, re.IGNORECASE)
    if match:
        raw = match.group(0).upper().replace(" ", "")
        return raw.lstrip('#')  # ← QUITAMOS el símbolo #
    return None

async def get_order_status(order_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/orders?order_id=eq.{order_id.lstrip('#')}",
            headers=headers
        )
        data = response.json()
        return data[0] if data else None

async def mark_as_processed(message_id: str):
    async with httpx.AsyncClient() as client:
        await client.patch(
            f"{SUPABASE_URL}/rest/v1/messages?id=eq.{message_id}",
            headers=headers,
            json={"order_checked": True}
        )

async def log_processing(message_id: str, status: str, detail: str = ""):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{SUPABASE_URL}/rest/v1/order_processing_log",
            headers=headers,
            json={
                "message_id": message_id,
                "status": status,
                "detail": detail
            }
        )

async def main():
    messages = await fetch_messages_to_process()
    print(f"📬 Mensajes para procesar: {len(messages)}")

    for msg in messages:
        print(f"\n Mensaje: {msg['message']}")
        order_id = extract_order_id(msg["message"])
        print(f" Código de pedido extraído: {order_id}")
        if not order_id:
            print("⚠️  No se encontró un código de pedido válido.")
            await log_processing(
                message_id=msg["id"],
                status="no_order_id",
                detail="No se detectó un código de pedido en el mensaje."
            )
            await mark_as_processed(msg["id"])
            continue

        order = await get_order_status(order_id)

        if not order:
            print(f"❌ Pedido {order_id} no encontrado.")
            await log_processing(
                message_id=msg["id"],
                status="not_found",
                detail=f"Pedido {order_id} no encontrado en la base de datos."
            )
        else:
            print(f"✅ Pedido {order_id} encontrado:")
            print(f"    Estado: {order['status']}")
            print(f"    Enviado: {order.get('shipped_date')}")
            print(f"    Entrega estimada: {order.get('delivery_estimate')}")
            await log_processing(
                message_id=msg["id"],
                status="success",
                detail=f"Pedido encontrado: Estado={order['status']}, Entrega={order.get('delivery_estimate')}"
            )

        await mark_as_processed(msg["id"])

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())