FROM python:3.10-slim

WORKDIR /var/www

RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080

CMD ["python", "app.py"]
