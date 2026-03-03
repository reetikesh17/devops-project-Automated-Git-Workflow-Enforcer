# Git Workflow Enforcer - Multi-Stage Optimized Docker Image
# This Dockerfile uses multi-stage builds to minimize final image size

# ============================================================================
# Stage 1: Builder - Install dependencies and prepare application
# ============================================================================
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
# Using --target to install to a specific directory that we can copy
RUN pip install --no-cache-dir --target=/build/packages -r requirements.txt || \
    echo "No dependencies to install"

# Copy application source code
COPY src/ ./src/
COPY setup.py .

# Verify the structure
RUN ls -la /build && \
    ls -la /build/src || true

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-slim

# Metadata labels
LABEL maintainer="DevOps Team" \
      description="Automated Git Workflow Enforcer - Validate branch names and commit messages" \
      version="1.0.0" \
      org.opencontainers.image.source="https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer" \
      org.opencontainers.image.title="Git Workflow Enforcer" \
      org.opencontainers.image.description="Validate Git workflows with Conventional Commits"

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/*

# Create non-root user early
RUN useradd -m -u 1000 -s /bin/bash enforcer && \
    mkdir -p /app && \
    chown -R enforcer:enforcer /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder --chown=enforcer:enforcer /build/packages /usr/local/lib/python3.11/site-packages/

# Copy application files from builder
COPY --from=builder --chown=enforcer:enforcer /build/src ./src/
COPY --from=builder --chown=enforcer:enforcer /build/setup.py ./

# Switch to non-root user
USER enforcer

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/usr/local/lib/python3.11/site-packages:$PYTHONPATH \
    PATH=/home/enforcer/.local/bin:$PATH

# Expose no ports (this is a CLI tool)
# EXPOSE directive not needed

# Health check to verify Python and app are working
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command - validate all with CI mode
CMD ["python", "src/main/cli.py", "validate-all", "--ci"]

# Build arguments for customization (optional)
ARG BUILD_DATE
ARG VCS_REF
LABEL org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.revision=$VCS_REF
