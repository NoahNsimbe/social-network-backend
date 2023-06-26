# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.6
ARG PROJECT_DIR=/backend

FROM python:${PYTHON_VERSION}-slim as base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR $PROJECT_DIR
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
RUN pip install --upgrade pip setuptools wheel
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

USER appuser
COPY . $PROJECT_DIR/

FROM base as web
EXPOSE 8000
CMD python manage.py migrate && gunicorn 'social_network_backend.wsgi' --bind=0.0.0.0:8000

FROM base as tests
CMD python manage.py migrate && python manage.py flush --noinput && python manage.py test