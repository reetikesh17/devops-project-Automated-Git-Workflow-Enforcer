# Makefile for Git Workflow Enforcer
# Provides convenient commands for Docker operations

.PHONY: help build run test clean push pull shell validate-branch validate-commit validate-all

# Variables
IMAGE_NAME := git-workflow-enforcer
IMAGE_TAG := latest
FULL_IMAGE := $(IMAGE_NAME):$(IMAGE_TAG)
DOCKER_RUN := docker run --rm -v $$(pwd):/workspace -w /workspace

# Default target
help:
	@echo "Git Workflow Enforcer - Docker Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  make build              - Build Docker image"
	@echo "  make run                - Run validation (auto-detect)"
	@echo "  make test               - Run tests in container"
	@echo "  make shell              - Open interactive shell"
	@echo "  make validate-branch    - Validate branch name only"
	@echo "  make validate-commit    - Validate commit message only"
	@echo "  make validate-all       - Validate both branch and commit"
	@echo "  make clean              - Remove Docker image"
	@echo "  make push               - Push image to registry"
	@echo "  make pull               - Pull image from registry"
	@echo "  make size               - Show image size"
	@echo "  make inspect            - Inspect image details"

# Build the Docker image
build:
	@echo "Building Docker image..."
	docker build \
		--build-arg BUILD_DATE=$$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
		--build-arg VCS_REF=$$(git rev-parse --short HEAD) \
		-t $(FULL_IMAGE) .
	@echo "Build complete!"

# Build with no cache
build-no-cache:
	@echo "Building Docker image (no cache)..."
	docker build --no-cache -t $(FULL_IMAGE) .

# Run validation with auto-detection
run:
	@echo "Running validation..."
	$(DOCKER_RUN) $(FULL_IMAGE)

# Run tests
test:
	@echo "Running tests..."
	docker-compose up enforcer-test

# Open interactive shell
shell:
	@echo "Opening interactive shell..."
	docker run --rm -it -v $$(pwd):/workspace -w /workspace $(FULL_IMAGE) /bin/bash

# Validate branch only
validate-branch:
	@echo "Validating branch name..."
	$(DOCKER_RUN) $(FULL_IMAGE) python src/main/cli.py validate-branch --ci

# Validate commit only
validate-commit:
	@echo "Validating commit message..."
	$(DOCKER_RUN) $(FULL_IMAGE) python src/main/cli.py validate-commit --ci

# Validate both
validate-all:
	@echo "Validating branch and commit..."
	$(DOCKER_RUN) $(FULL_IMAGE) python src/main/cli.py validate-all --ci

# Clean up Docker image
clean:
	@echo "Removing Docker image..."
	docker rmi $(FULL_IMAGE) || true
	docker system prune -f

# Show image size
size:
	@echo "Image size:"
	@docker images $(IMAGE_NAME) --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Inspect image
inspect:
	@echo "Image details:"
	@docker inspect $(FULL_IMAGE) | head -50

# Push to registry
push:
	@echo "Pushing image to registry..."
	docker push $(FULL_IMAGE)

# Pull from registry
pull:
	@echo "Pulling image from registry..."
	docker pull $(FULL_IMAGE)

# Docker Compose commands
compose-up:
	docker-compose up enforcer

compose-dev:
	docker-compose run --rm enforcer-dev

compose-down:
	docker-compose down

# Scan for vulnerabilities (requires trivy)
scan:
	@echo "Scanning image for vulnerabilities..."
	@command -v trivy >/dev/null 2>&1 || { echo "Trivy not installed. Install from: https://github.com/aquasecurity/trivy"; exit 1; }
	trivy image $(FULL_IMAGE)

# Show Docker info
info:
	@echo "Docker version:"
	@docker --version
	@echo ""
	@echo "Docker info:"
	@docker info | head -20
