FROM python:3.12-slim AS build
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc libffi-dev rustc cargo \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv pip install --system .
RUN uv pip install --system "uvicorn[standard]"

FROM python:3.12
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=8000
COPY --from=build /usr/local /usr/local
WORKDIR /app
COPY . .

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
