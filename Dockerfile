FROM python:3.8.5

WORKDIR .

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Definición de variables de entorno
ENV FLASK_RUN_PORT=4500
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run", "--debug"]