# From: https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
# The builder image, used to build the virtual environment
FROM python:3.10-buster as builder

RUN pip install poetry==1.5.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    ENVIRONMENT=prod

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev,api && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.10-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY webapp /app/webapp
COPY images /app/images

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "/app/webapp/Camouflage.py", "--server.port=${PORT}", "--server.address=${ADDRESS}"]