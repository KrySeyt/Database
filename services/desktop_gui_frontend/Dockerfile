FROM python:3.11.4-slim-bullseye

RUN apt-get update
RUN apt-get install xauth -y
RUN rm -rf /var/lib/apt

ENV WORKDIR=/desktop_gui_frontend/

WORKDIR $WORKDIR

ENV VIRTUAL_ENV="$WORKDIR/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv $VIRTUAL_ENV

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

COPY mypy.ini .
COPY ./src/ ./src/

CMD /bin/bash
