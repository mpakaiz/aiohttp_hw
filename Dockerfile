FROM python:3.10.13-alpine3.18
COPY ./app /app

WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir pydantic[email]
ENTRYPOINT gunicorn app:get_app --worker-class aiohttp.GunicornWebWorker --bind 0.0.0.0:8080