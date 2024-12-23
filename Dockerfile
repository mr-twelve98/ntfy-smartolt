FROM python:3.10-slim

# Install dependencies including supervisor
RUN apt-get update && apt-get install -y supervisor

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["supervisord", "-c", "supervisord.conf"]
