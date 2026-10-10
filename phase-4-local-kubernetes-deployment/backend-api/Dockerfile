FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (cached layer).
# requirements.lock.txt is a complete freeze of the environment Phase III is
# proven to run. --no-deps is deliberate: requirements.txt is stale and cannot
# be resolved at all (fastapi 0.104.1 caps anyio<4.0.0 while mcp 1.26.0 needs
# anyio>=4.5), so resolution is skipped to reproduce the proven set exactly
# rather than substitute a different one. See the lock file's header.
COPY requirements.lock.txt .
RUN pip install --no-cache-dir --no-deps -r requirements.lock.txt

# Copy application code
COPY . .

# Hugging Face Spaces expects port 7860
EXPOSE 7860

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
