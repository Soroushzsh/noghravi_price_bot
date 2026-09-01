FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY manage.py .
COPY templates ./templates
COPY static ./static
RUN useradd --create-home --uid 10001 bot && mkdir /data /app/staticfiles && chown -R bot:bot /data /app/staticfiles
USER bot
ENV PYTHONPATH=/app/src PYTHONDONTWRITEBYTECODE=1 DJANGO_SETTINGS_MODULE=noghre_time.settings
RUN DJANGO_SECRET_KEY=collectstatic-only-not-used-at-runtime-7c4bfb56 python manage.py collectstatic --noinput
CMD ["python", "-m", "silver_bot", "run"]
