# Usa una base di Python
FROM python:3.10

# Imposta la directory di lavoro
WORKDIR /app

# Copia requirements.txt e installa le dipendenze
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia il codice del bot
COPY . .

# Comando di avvio
CMD ["python", "bot.py"]

