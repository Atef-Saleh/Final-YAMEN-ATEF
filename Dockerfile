FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


COPY app/requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY app/src /app/src


ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1


EXPOSE 5000


CMD ["python", "src/main.py"]
