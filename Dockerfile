FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --only-binary=all -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["sh", "-c", "exec gunicorn app:app --workers 2 --timeout 120 --bind 0.0.0.0:${PORT:-10000}"]
