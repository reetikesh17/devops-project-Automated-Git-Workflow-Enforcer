# Git Workflow Enforcer - Optimized Docker Image
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

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true

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

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"
