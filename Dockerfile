FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=3000

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p jobs

EXPOSE 3000

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-3000} --workers 1 --threads 8 --timeout 0 --access-logfile - app:app"]
