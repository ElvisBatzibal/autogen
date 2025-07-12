python3 -m venv .venv
source .venv/bin/activate  # Para Mac/Linux
pip install python-multipart
pip install uvicorn
pip install -r requirements.txt
#python main.py
uvicorn main:app --reload