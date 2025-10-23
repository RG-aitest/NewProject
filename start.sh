#!/bin/bash

# Start FastAPI backend in background
uvicorn backend:app --host 0.0.0.0 --port 8000 &

# Start Streamlit UI in foreground
streamlit run AIBot_UI.py