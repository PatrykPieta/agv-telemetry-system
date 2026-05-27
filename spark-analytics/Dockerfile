FROM python:3.9-bullseye

# Instalacja Javy 11 (Bullseye nadal ją wspiera!)
RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    rm -rf /var/lib/apt/lists/*
# ... góra pliku bez zmian ...
WORKDIR /app

# Najpierw kopiujemy i instalujemy zależności (żeby Docker zapisał je w Cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Na końcu kopiujemy nasz właściwy skrypt
COPY analytics.py .

CMD ["python", "-u", "analytics.py"]