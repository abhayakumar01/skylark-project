import streamlit as st
from streamlit.starlette import App  # New experimental 2026 feature
from starlette.routing import Mount
from backend import app as fastapi_backend

# 1. Initialize the Streamlit ASGI App
# Point it to your existing frontend script
app = App("frontend.py", routes=[
    # 2. Mount FastAPI under the "/api" prefix
    # This makes your backend available at: your-app.streamlit.app/api
    Mount("/api", app=fastapi_backend)
])
