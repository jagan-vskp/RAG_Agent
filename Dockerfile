# ============================================================
# RAG Agent Backend - Multi-Stage Production Build
# Final image size: ~850MB-1.2GB (NOT 12.7GB!)
# ============================================================

# ────────────────────────────────────────────────────────────
# Stage 1: Builder - Compile dependencies
# ────────────────────────────────────────────────────────────
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies (gcc, g++ needed for some packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy ONLY requirements file
COPY requirements-docker.txt requirements.txt

# Build wheels (pre-compiled packages)
# --no-cache-dir: Don't store pip cache (saves 2-3GB!)
# --no-deps: Don't auto-install dependencies (we control versions)
# --wheel-dir: Store wheels for next stage
RUN pip wheel \
    --no-cache-dir \
    --no-deps \
    --wheel-dir /build/wheels \
    -r requirements.txt

# ────────────────────────────────────────────────────────────
# Stage 2: Runtime - Minimal production image
# This is the ONLY stage that ends up in final image
# ────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Environment variables for optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install ONLY runtime dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy ONLY pre-built wheels from builder stage
COPY --from=builder /build/wheels /wheels

# Install all packages from wheels, then DELETE wheels
# This saves space in final image
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Copy ONLY application code (not tests, docs, venv, etc.)
COPY main.py \
     config.py \
     llm_client.py \
     rag_schema.py \
     rag_memory.py \
     retriever.py \
     middleware.py \
     ./

# Create non-root user for security
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose backend port
EXPOSE 8080

# Health check (curl must be installed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start application
CMD ["python", "main.py"]