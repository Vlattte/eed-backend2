FROM python:3.10-slim

WORKDIR ./eed_backend2
COPY ./ ./
RUN pip install -r requirements.txt --no-cache-dir

CMD uvicorn server:app --port 8083 --reload