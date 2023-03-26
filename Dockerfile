# app/Dockerfile

FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install poetry==1.4.1

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi


EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

COPY webapp ./webapp

WORKDIR /app/webapp

ENTRYPOINT ["streamlit", "run", "Camouflage.py", "--server.port=8501", "--server.address=0.0.0.0"]