FROM python:3.11.4-slim-bullseye
RUN apt-get update
RUN apt-get install -y curl 
RUN rm -rf /var/lib/apt

ENV WORKDIR=/backend

WORKDIR $WORKDIR

ENV VIRTUAL_ENV="$WORKDIR/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv $VIRTUAL_ENV

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir


COPY alembic/ alembic/
COPY alembic.ini .
COPY mypy.ini .
COPY database_app/ database_app/
COPY main.py .

CMD alembic upgrade head && python -O -m uvicorn main:app --host 0.0.0.0 --port 8000
