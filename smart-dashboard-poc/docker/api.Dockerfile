FROM python:3.10-slim

WORKDIR /app

COPY ./smart-dashboard-poc /app

RUN apt-get update && \
    apt-get install -y gcc curl build-essential && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get clean

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
