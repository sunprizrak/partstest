FROM python:3.12.3-alpine3.18

WORKDIR /partstest

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]