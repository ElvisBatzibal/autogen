from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import httpx
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def form_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    message: str = Form(...)
):
    async with httpx.AsyncClient() as client:
        # Buscar cliente
        resp = await client.get(f"{SUPABASE_URL}/rest/v1/customers?email=eq.{email}", headers=headers)
        data = resp.json()

        if data:
            customer_id = data[0]["id"]
        else:
            customer_id = str(uuid.uuid4())
            await client.post(f"{SUPABASE_URL}/rest/v1/customers", headers=headers, json={
                "id": customer_id,
                "name": name,
                "email": email,
                "phone": phone
            })

        # Guardar mensaje
        message_id = str(uuid.uuid4())
        await client.post(f"{SUPABASE_URL}/rest/v1/messages", headers=headers, json={
            "id": message_id,
            "customer_id": customer_id,
            "channel": "Web",
            "message": message
        })

    # Ejecutar flujo completo desde trigger_autogen
    try:
        async with httpx.AsyncClient() as client:
            print("Conectando con el trigger de Autogen...")
            trigger_response = await client.post("http://localhost:8001/run-agents", json={"message_id": message_id})
            print("🚀 Ejecutando flujo Autogen...")
            print(f"Respuesta del trigger: {trigger_response.text}")
            if trigger_response.status_code == 200:
                print("✅ Flujo Autogen ejecutado correctamente")
            else:
                print(f"⚠️ Error al ejecutar Autogen: {trigger_response.text}")
    except Exception as e:
        print(f"❌ No se pudo conectar al trigger: {e}")

    # Obtener la respuesta más reciente
    async with httpx.AsyncClient() as client:
        query = (
                f"{SUPABASE_URL}/rest/v1/messages"
                f"?customer_id=eq.{customer_id}"
                f"&message=eq.{message}"
                f"&select=response"
                f"&order=created_at.desc"
                f"&limit=1"
            )
        resp = await client.get(query, headers=headers)

        try:
            data = resp.json()
        except Exception as e:
            return templates.TemplateResponse("respuesta.html", {
                "request": request,
                "respuesta": "❌ No se pudo interpretar la respuesta del servidor."
            })

        if not isinstance(data, list) or not data:
            return templates.TemplateResponse("respuesta.html", {
                "request": request,
                "respuesta": "❌ Hubo un error al procesar tu mensaje. Intenta nuevamente más tarde."
            })

        return templates.TemplateResponse("respuesta.html", {
            "request": request,
            "respuesta": data[0].get("respuesta", "❓ Sin respuesta generada.")
        })

@app.get("/respuesta")
async def obtener_respuesta(message_id: str):
    async with httpx.AsyncClient() as client:
        query = (
            f"{SUPABASE_URL}/rest/v1/messages"
            f"?id=eq.{message_id}"
            f"&select=response"
        )
        resp = await client.get(query, headers=headers)
        try:
            data = resp.json()
        except Exception:
            return JSONResponse(status_code=500, content={"status": "error", "message": "Respuesta no válida"})

        if not isinstance(data, list) or not data:
            return JSONResponse(status_code=404, content={"status": "pending"})

        respuesta = data[0].get("response")
        if not respuesta:
            return JSONResponse(status_code=202, content={"status": "pending"})

        return JSONResponse(status_code=200, content={"status": "ready", "respuesta": respuesta})