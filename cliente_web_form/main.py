from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
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

@app.post("/", response_class=RedirectResponse)
async def form_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    message: str = Form(...)
):
    async with httpx.AsyncClient() as client:
        # 1. Buscar cliente por correo
        print(f"Searching for customer with email: {email}")
        resp = await client.get(f"{SUPABASE_URL}/rest/v1/customers?email=eq.{email}", headers=headers)
        data = resp.json()

        if data:
            customer_id = data[0]["id"]
            print(f"Customer found: {data[0]['name']} with ID {customer_id}")
        else:
            # 2. Crear cliente si no existe
            # add log
            print(f"Creating new customer: {name}, {email}, {phone}")
            customer_id = str(uuid.uuid4())
            await client.post(f"{SUPABASE_URL}/rest/v1/customers", headers=headers, json={
                "id": customer_id,
                "name": name,
                "email": email,
                "phone": phone
            })

        # 3. Guardar mensaje
        print(f"Saving message for customer {customer_id}: {message}")
        await client.post(f"{SUPABASE_URL}/rest/v1/messages", headers=headers, json={
            "customer_id": customer_id,
            "channel": "Web",
            "message": message
        })

    return RedirectResponse(url="/", status_code=303)