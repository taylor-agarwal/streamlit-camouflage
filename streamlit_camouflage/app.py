import logging

from fastapi import FastAPI
import uvicorn

from streamlit_camouflage.v1.endpoints import router as v1_router

app = FastAPI()

v1_app = FastAPI()
v1_app.include_router(v1_router)

app.mount('/v1', v1_app)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="localhost", port=80)