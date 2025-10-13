FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install psycopg2-binary
CMD ["python", "main.py"]
