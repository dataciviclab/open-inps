# Build dalla root del repo:
#   docker build -f dashboard/Dockerfile -t open-inps-dashboard .
# Il registry/ va nell'immagine: sources e SQL page leggono i path GCS.

FROM python:3.12-slim

WORKDIR /app

COPY dashboard/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard/ ./dashboard/
COPY registry/ ./registry/

WORKDIR /app/dashboard
EXPOSE 8501
ENV STREAMLIT_SERVER_HEADLESS=true
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
