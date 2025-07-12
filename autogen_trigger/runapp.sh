python3 -m venv .venv
source .venv/bin/activate  # Para Mac/Linux
pip install python-multipart
pip install uvicorn
pip install -r requirements.txt
#python main.py
uvicorn trigger_autogen:app --host 0.0.0.0 --port 8001 --reload