python3 -m venv .venv
source .venv/bin/activate  # Para Mac/Linux
pip install python-multipart
pip install uvicorn
pip install -r requirements.txt
#python main.py
#uvicorn main:app --reload
# Cierra cualquier proceso que use el puerto 8002
PID=$(lsof -ti:8002)
if [ -n "$PID" ]; then
  echo "Cerrando proceso en puerto 8002 (PID: $PID)..."
  kill -9 $PID
fi

# Inicia la aplicación en puerto 8002
uvicorn main:app --reload --port 8002