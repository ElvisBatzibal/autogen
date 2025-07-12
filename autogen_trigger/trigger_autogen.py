from fastapi import FastAPI
from fastapi.responses import JSONResponse
import subprocess
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


@app.post("/run-agents")
async def run_agents():
    try:
        # Ruta al archivo autogen_main.py
        print("Ejecutando el script de Autogen...")
        autogen_script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "agents", "autogen", "autogen_main.py")
        )
        print(f"Ruta del script: {autogen_script_path}")
        print("Iniciando ejecución del script de Autogen...")
        # Ejecutar el script autogen_main.py
        result = subprocess.run(
            ["python", autogen_script_path],
            capture_output=True,
            text=True,
            check=True
        )
        print("Respuesta del script de Autogen:")
        print(result.stdout)
        print("Script ejecutado correctamente.")
        return JSONResponse(status_code=200, content={
            "status": "success",
            "output": result.stdout
        })

    except subprocess.CalledProcessError as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "error": e.stderr
        })