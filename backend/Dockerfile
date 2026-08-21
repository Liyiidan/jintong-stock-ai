FROM python:3.11-slim

WORKDIR /app

ARG INSTALL_DATA_DEPS=false

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-core.txt /app/requirements-core.txt
RUN pip install --no-cache-dir -r /app/requirements-core.txt
COPY requirements-data.txt /app/requirements-data.txt
RUN if [ "$INSTALL_DATA_DEPS" = "true" ]; then pip install --no-cache-dir -r /app/requirements-data.txt; fi

COPY app /app/app
COPY scripts /app/scripts

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
