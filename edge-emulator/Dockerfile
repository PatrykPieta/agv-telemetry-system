FROM python:3.9-slim
WORKDIR /app
# Kopiujemy listę bibliotek
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Kopiujemy kod emulatora
COPY . .
# Odpalamy!
CMD ["python", "-u", "main.py"]