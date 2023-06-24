FROM python:3.11.4-slim-bullseye
RUN apt-get update && \
    rm -rf /var/lib/apt

WORKDIR /db_backend/

ENV VIRTUAL_ENV="/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv $VIRTUAL_ENV

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

COPY ./src/ ./src/

CMD uvicorn src.main:app --host 0.0.0.0 --port 8000
