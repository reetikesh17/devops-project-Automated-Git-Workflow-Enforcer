# Git Workflow Enforcer - Optimized Docker Image
# Multi-stage build for minimal image size

# Stage 1: Builder
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Metadata
LABEL maintainer="DevOps Team"
LABEL description="Automated Git Workflow Enforcer - Validate branch names and commit messages"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install runtime dependencies (git is needed for validation)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application files
COPY src/ ./src/
COPY setup.py .

# Create non-root user for security
RUN useradd -m -u 1000 enforcer && \
    chown -R enforcer:enforcer /app

# Switch to non-root user
USER enforcer

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "src/main/cli.py", "validate-all", "--ci"]

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"
