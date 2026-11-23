# rclone-Binary aus dem offiziellen Image uebernehmen
FROM rclone/rclone:1.68 AS rclone

FROM python:3.12-alpine
# Zeitzonen-Daten kommen per pip (tzdata), daher kein apk noetig
COPY --from=rclone /usr/local/bin/rclone /usr/local/bin/rclone

WORKDIR /app
COPY app/requirements.txt .
# Robust gegen langsame oder wackelige Verbindungen zu PyPI: laengeres Timeout, mehr Wiederholungen
# und bis zu 3 komplette Versuche mit Pause dazwischen.
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_DEFAULT_TIMEOUT=60 PIP_RETRIES=10
RUN for i in 1 2 3; do \
      pip install --no-cache-dir -r requirements.txt && exit 0; \
      echo "pip install fehlgeschlagen (Versuch $i von 3), neuer Versuch in 15 Sekunden ..."; sleep 15; \
    done; \
    echo "FEHLER: Python-Pakete konnten nicht von PyPI geladen werden. Internetverbindung/DNS des Docker-Hosts pruefen."; \
    exit 1
COPY app/ .

ARG VERSION=1.33.0
LABEL org.opencontainers.image.title="MirrorSync" org.opencontainers.image.version=$VERSION
ENV TZ=Europe/Berlin CONFIG_DIR=/config LOG_DIR=/logs PORT=8080 PYTHONUNBUFFERED=1
VOLUME ["/config", "/logs"]
EXPOSE 8080
HEALTHCHECK --interval=60s --timeout=5s CMD wget -qO- "http://127.0.0.1:${PORT}/health" || exit 1
CMD ["python", "app.py"]
