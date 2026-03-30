FROM python:3-alpine

WORKDIR /app/bcmirror
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "bcmirror.py"]
