FROM python:3.12-slim

# Run as non-root — an auditing tool should model the least-privilege
# posture it audits for.
RUN useradd --create-home --shell /usr/sbin/nologin auditor

WORKDIR /app

# System libraries required by weasyprint (PDF/HTML report generation) —
# Pango/Cairo/GDK-PixBuf aren't present in the slim base image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Dependencies first, code second: Docker caches layers top-down, so
# this ordering means code edits don't re-trigger a full pip install.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY scripts/ scripts/
COPY rules/ rules/
COPY tests/fixtures/ tests/fixtures/

RUN mkdir -p reports && chown -R auditor:auditor /app

USER auditor
ENTRYPOINT ["python", "-m", "scripts.run_agent"]
CMD ["--fixtures"]
