FROM python:3.8-slim
WORKDIR /app

RUN pip install cryptography

COPY src/ /app/

CMD ["python3"]
