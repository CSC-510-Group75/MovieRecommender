FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/Code/recommenderapp

RUN python initialize_db.py

CMD ["python", "app.py"]
