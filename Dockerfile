# Base image
FROM django:1.10

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000
