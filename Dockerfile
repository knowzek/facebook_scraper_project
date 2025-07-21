FROM mcr.microsoft.com/playwright/python:v1.53.0-jammy

WORKDIR /app
COPY auth.json auth.json

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /output

CMD ["sh", "-c", "python main.py && cp landing_page.png /output/landing_page.png"]

