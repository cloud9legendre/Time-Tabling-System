FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Run from root, targeting the module inside src
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
