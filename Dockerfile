FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

COPY --chown=1000:1000 .env /app/.env

CMD ["python", "run.py"]