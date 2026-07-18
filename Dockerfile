FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias necesarias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y datos
COPY main.py .
COPY src/ ./src/
COPY data/ ./data/

# Puerto expuesto por FastAPI
EXPOSE 8000

CMD ["python", "main.py"]
