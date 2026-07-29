FROM python:3.11-slim

WORKDIR /app

# Install uv for faster dependency management
RUN pip install uv

# Install dependencies
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt

# Copy source code
COPY . ./

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
