from fastapi import FastAPI
from fastapi.responses import JSONResponse
import subprocess
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class TriggerRequest(BaseModel):
    message_id: str

app = FastAPI()


@app.post("/run-agents")
async def run_agents(request: TriggerRequest):
    try:
        # Ruta al archivo autogen_main.py
        print("Ejecutando el script de Autogen...")
        print(f"Message ID recibido: {request.message_id}")
        autogen_script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "agents", "autogen", "autogen_main.py")
        )
        print(f"Ruta del script: {autogen_script_path}")
        print("Iniciando ejecución del script de Autogen...")
        # Ejecutar el script autogen_main.py con el message_id
        result = subprocess.run(
            ["python", autogen_script_path, request.message_id],
            capture_output=True,
            text=True,
            check=True
        )
        print("Respuesta del script de Autogen:")
        print(result.stdout)
        print("Script ejecutado correctamente.")
        # Validar si la salida contiene mensajes de error visibles
        if "❌" in result.stdout or "error" in result.stdout.lower():
            print("Se detectó un posible error en la salida del script.")
            return JSONResponse(status_code=200, content={
                "status": "error",
                "output": result.stdout
            })
        
        return JSONResponse(status_code=200, content={
            "status": "success",
            "output": result.stdout
        })

    except subprocess.CalledProcessError as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "error": e.stderr
        })