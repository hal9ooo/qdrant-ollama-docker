FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

ENV OPENAI_API_KEY=""

EXPOSE 8000

CMD ["python", "server.py"]
