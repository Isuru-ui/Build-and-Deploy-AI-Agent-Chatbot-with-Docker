FROM python:3.9-slim

COPY . /app/

WORKDIR /app

RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

EXPOSE 8000 7860

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8000 & streamlit run ui.py --server.port 7860 --server.address 0.0.0.0"]