ARG BUILD_FROM
FROM ${BUILD_FROM}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Copy s6-overlay service definitions. The run script uses
# `#!/usr/bin/with-contenv bashio` so SUPERVISOR_TOKEN and other
# Supervisor-injected env vars are available to the Python process.
COPY rootfs /

EXPOSE 5000
