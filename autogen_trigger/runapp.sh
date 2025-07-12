python3 -m venv .venv
source .venv/bin/activate  # Para Mac/Linux
pip install python-multipart
pip install uvicorn
pip install -r requirements.txt
#python main.py
# Cierra cualquier proceso que use el puerto 8001
PID=$(lsof -ti:8001)
if [ -n "$PID" ]; then
  echo "Cerrando proceso en puerto 8001 (PID: $PID)..."
  kill -9 $PID
fi
uvicorn trigger_autogen:app --host 0.0.0.0 --port 8001 --reload