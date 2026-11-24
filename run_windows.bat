@echo off
python -m pip install -r requirements.txt
start cmd /k uvicorn api:app --reload
streamlit run app.py
