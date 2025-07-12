from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
import os
from dotenv import load_dotenv
import uuid
from classify.classify_messages import run_classification_process
from orders.agent_orders import run_order_agent_process
from response.agent_responses import run_response_agent_process

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
        await client.post(f"{SUPABASE_URL}/rest/v1/messages", headers=headers, json={
            "customer_id": customer_id,
            "channel": "Web",
            "message": message
        })

    # Ejecutar flujo completo desde trigger_autogen
    try:
        async with httpx.AsyncClient() as client:
            trigger_response = await client.post("http://localhost:8001/run-agents")
            if trigger_response.status_code == 200:
                print("✅ Flujo Autogen ejecutado correctamente")
            else:
                print(f"⚠️ Error al ejecutar Autogen: {trigger_response.text}")
    except Exception as e:
        print(f"❌ No se pudo conectar al trigger: {e}")

    # Obtener la respuesta más reciente
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/messages?select=message,response&order=created_at.desc&limit=1",
            headers=headers
        )
        data = resp.json()
        return templates.TemplateResponse("respuesta.html", {"request": request, "data": data[0]})