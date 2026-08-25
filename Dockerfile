FROM python:3.12-slim
WORKDIR /app
COPY src ./src
COPY requirements.txt .
RUN useradd --create-home --uid 10001 bot && mkdir /data && chown bot:bot /data
USER bot
ENV PYTHONPATH=/app/src PYTHONDONTWRITEBYTECODE=1
CMD ["python", "-m", "silver_bot", "run"]
