# Take the rclone binary from the official image
FROM rclone/rclone:1.76 AS rclone

FROM python:3.14-alpine
# Time zone data comes via pip (tzdata), so no apk needed
COPY --from=rclone /usr/local/bin/rclone /usr/local/bin/rclone

WORKDIR /app
COPY app/requirements.txt .
# Robust against slow or flaky connections to PyPI: longer timeout, more retries
# and up to 3 complete attempts with a pause in between.
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_DEFAULT_TIMEOUT=60 PIP_RETRIES=10
RUN for i in 1 2 3; do \
      pip install --no-cache-dir -r requirements.txt && exit 0; \
      echo "pip install failed (attempt $i of 3), retrying in 15 seconds ..."; sleep 15; \
    done; \
    echo "ERROR: Python packages could not be downloaded from PyPI. Check the Docker host's internet connection/DNS."; \
    exit 1
COPY app/ .

ARG VERSION=1.37.0
LABEL org.opencontainers.image.title="MirrorSync" org.opencontainers.image.version=$VERSION
ENV TZ=Europe/Berlin CONFIG_DIR=/config LOG_DIR=/logs PORT=8080 PYTHONUNBUFFERED=1
VOLUME ["/config", "/logs"]
EXPOSE 8080
HEALTHCHECK --interval=60s --timeout=5s CMD wget -qO- "http://127.0.0.1:${PORT}/health" || exit 1
CMD ["python", "app.py"]
