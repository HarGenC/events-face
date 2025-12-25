FROM python:3.12-slim

RUN pip install --no-cache-dir uv

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv config virtualenvs.create false

RUN uv sync --no-interaction --no-ansi

COPY . /app

ENV DJANGO_SETTINGS_MODULE=src.core.settings

CMD ["uv", "run", "gunicorn", "src.core.wsgi:application", "--bind", "0.0.0.0:8000" ]