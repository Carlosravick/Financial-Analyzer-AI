FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para FAISS/Pandas
RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]