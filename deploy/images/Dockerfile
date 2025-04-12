FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache --virtual .build-deps gcc musl-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

COPY hello.py .
COPY static/ static/
COPY templates/ templates/

RUN addgroup -g 1000 appgroup && \
    adduser -D -u 1000 -G appgroup appuser
USER appuser

EXPOSE 8000

ENTRYPOINT ["python", "hello.py"]
