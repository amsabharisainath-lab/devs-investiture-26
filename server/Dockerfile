FROM python:3.12-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        wget \
        ca-certificates \
        libjpeg62-turbo \
        libxrender1 \
        libfontconfig1 \
        libx11-6 \
        libxext6 \
        libssl3 \
        fonts-liberation \
        xfonts-75dpi \
        xfonts-base \
    && wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6.1-3.bookworm_amd64.deb || apt-get install -f -y \
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]