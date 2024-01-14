import logging
import sys

from fastapi import FastAPI
import uvicorn

sys.path.insert(0, '.')

from streamlit_camouflage.v1.endpoints import router as v1_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()

v1_app = FastAPI()
v1_app.include_router(v1_router)

app.mount('/v1', v1_app)