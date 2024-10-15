FROM python:3.9

WORKDIR /app

COPY .venv/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

COPY app /app

COPY .env /app/.env
COPY database /app/database
COPY run.py /app/run.py

RUN apt-get update && apt-get install -y postgresql-client && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["python", "run.py"]