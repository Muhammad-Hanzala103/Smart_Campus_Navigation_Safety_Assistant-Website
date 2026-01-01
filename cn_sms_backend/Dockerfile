FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize DB (in production prefer external DB migration)
# RUN python db_init.py 

EXPOSE 5000

ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production

CMD ["gunicorn", "-w", "4", "wsgi:app", "-b", "0.0.0.0:5000"]
