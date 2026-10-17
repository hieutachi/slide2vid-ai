FROM python:3.11-slim-bookworm AS builder
WORKDIR /src
COPY pyproject.toml README.md LICENSE THIRD_PARTY_NOTICES.md ./
COPY slidevoice ./slidevoice
RUN python -m pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.11-slim-bookworm AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libreoffice-impress poppler-utils fonts-dejavu-core fonts-noto-core \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 slidevoice \
    && useradd --uid 10001 --gid 10001 --create-home slidevoice \
    && mkdir -p /data && chown 10001:10001 /data
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels slidevoice \
    && rm -rf /wheels
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp/slidevoice
USER 10001:10001
WORKDIR /data
ENTRYPOINT ["slidevoice"]
CMD ["doctor", "--json-output"]