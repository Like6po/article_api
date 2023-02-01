FROM python:3.10-alpine
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
WORKDIR /app/src
CMD uvicorn main:app --host 0.0.0.0 --port 8000 --reload