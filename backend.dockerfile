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

RUN poetry install --without dev,webapp && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.10-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY streamlit_camouflage /app/streamlit_camouflage

WORKDIR /app

EXPOSE 8080

CMD ["uvicorn", "streamlit_camouflage.api:app", "--host", "$ADDRESS", "--port", "$PORT"]