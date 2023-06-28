FROM python:3.11.4-slim-bullseye
RUN apt-get update && \
    rm -rf /var/lib/apt

ENV WORKDIR=/backend

WORKDIR $WORKDIR

ENV VIRTUAL_ENV="$WORKDIR/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv $VIRTUAL_ENV

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir


COPY mypy.ini .
COPY ./database_app/ ./database_app/

CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000
