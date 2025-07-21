FROM mcr.microsoft.com/playwright/python:v1.53.0-jammy

WORKDIR /app
COPY . .
COPY auth.json auth.json
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
