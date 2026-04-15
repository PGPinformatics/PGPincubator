FROM python:3-alpine

WORKDIR /app/catalog
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "generate.py"]
