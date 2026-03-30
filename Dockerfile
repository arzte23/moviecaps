FROM ghcr.io/astral-sh/uv:python3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY . .

RUN uv run python manage.py collectstatic --noinput

CMD ["uv", "run", "gunicorn", "django_project.wsgi:application", "--bind", "0.0.0.0:8000"]