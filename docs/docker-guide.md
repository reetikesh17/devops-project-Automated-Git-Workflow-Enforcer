# Docker Guide

## Overview

The Git Workflow Enforcer is available as a Docker image for easy deployment and integration into containerized environments.

## Quick Start

### Pull and Run

```bash
# Build the image
docker build -t git-workflow-enforcer .

# Run validation
docker run --rm -v $(pwd):/workspace -w /workspace git-workflow-enforcer
```

### Using Docker Compose

```bash
# Run validation
docker-compose up enforcer

# Run in development mode
docker-compose run --rm enforcer-dev

# Run tests
docker-compose up enforcer-test
```

## Building the Image

### Basic Build

```bash
docker build -t git-workflow-enforcer:latest .
```

### Build with Tag

```bash
docker build -t git-workflow-enforcer:v1.0.0 .
```

### Build with Build Args

```bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t git-workflow-enforcer:latest \
  .
```

### Multi-platform Build

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t git-workflow-enforcer:latest \
  .
```

## Running the Container

### Basic Usage

```bash
# Validate current directory
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer
```

### Validate Specific Branch and Commit

```bash
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer \
  python src/main/cli.py validate-all \
    --ci \
    feature/JIRA-123-test \
    "feat: add new feature"
```

### Validate Branch Only

```bash
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer \
  python src/main/cli.py validate-branch --ci
```

### Validate Commit Only

```bash
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer \
  python src/main/cli.py validate-commit --ci
```

### With Custom Configuration

```bash
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer \
  python src/main/cli.py validate-all \
    --ci \
    --config /workspace/custom-rules.json
```

### Interactive Mode

```bash
docker run --rm -it \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer \
  /bin/bash
```

## Docker Compose

### Services

The `docker-compose.yml` defines three services:

#### 1. enforcer (Default)

Runs validation with auto-detection:

```bash
docker-compose up enforcer
```

#### 2. enforcer-dev (Development)

Interactive shell for development:

```bash
docker-compose run --rm enforcer-dev
```

Inside the container:
```bash
# Run validation
python src/main/cli.py validate-all

# Run tests
pytest tests/

# Run specific command
python src/main/cli.py validate-branch feature/JIRA-123-test
```

#### 3. enforcer-test (Testing)

Runs test suite:

```bash
docker-compose up enforcer-test
```

### Custom Commands

```bash
# Validate with custom config
docker-compose run --rm enforcer \
  python src/main/cli.py validate-all --ci --config custom-rules.json

# Run specific validation
docker-compose run --rm enforcer \
  python src/main/cli.py validate-branch --ci

# Run with verbose output
docker-compose run --rm enforcer \
  python src/main/cli.py validate-all --ci --verbose
```

## CI/CD Integration

### GitLab CI

```yaml
validate:
  image: git-workflow-enforcer:latest
  script:
    - python src/main/cli.py validate-all --ci
```

### Jenkins

```groovy
pipeline {
    agent {
        docker {
            image 'git-workflow-enforcer:latest'
        }
    }
    stages {
        stage('Validate') {
            steps {
                sh 'python src/main/cli.py validate-all --ci'
            }
        }
    }
}
```

### CircleCI

```yaml
version: 2.1

jobs:
  validate:
    docker:
      - image: git-workflow-enforcer:latest
    steps:
      - checkout
      - run: python src/main/cli.py validate-all --ci
```

### Azure Pipelines

```yaml
pool:
  vmImage: 'ubuntu-latest'

container: git-workflow-enforcer:latest

steps:
  - script: python src/main/cli.py validate-all --ci
    displayName: 'Validate Git Workflow'
```

### GitHub Actions

```yaml
jobs:
  validate:
    runs-on: ubuntu-latest
    container:
      image: git-workflow-enforcer:latest
    steps:
      - uses: actions/checkout@v4
      - run: python src/main/cli.py validate-all --ci
```

## Image Details

### Base Image

- **Base:** `python:3.11-slim`
- **Size:** ~150MB (optimized with multi-stage build)
- **Architecture:** linux/amd64, linux/arm64

### Installed Packages

- Python 3.11
- Git (for branch/commit detection)
- Project dependencies (from requirements.txt)

### Security Features

- Non-root user (`enforcer`)
- Minimal base image
- No unnecessary packages
- Read-only volume mounts recommended

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHONUNBUFFERED` | Python unbuffered output | `1` |
| `NO_COLOR` | Disable colored output | `0` |
| `PATH` | Python path | `/root/.local/bin:$PATH` |

## Optimization

### Image Size

The Dockerfile uses several optimization techniques:

1. **Multi-stage build** - Separate builder and runtime stages
2. **Slim base image** - `python:3.11-slim` instead of full image
3. **Layer caching** - Copy requirements.txt first
4. **Cleanup** - Remove apt lists and cache
5. **User packages** - Install to user directory
6. **.dockerignore** - Exclude unnecessary files

### Build Cache

```bash
# Use BuildKit for better caching
DOCKER_BUILDKIT=1 docker build -t git-workflow-enforcer .

# Use cache from registry
docker build \
  --cache-from git-workflow-enforcer:latest \
  -t git-workflow-enforcer:latest \
  .
```

## Publishing

### Docker Hub

```bash
# Tag image
docker tag git-workflow-enforcer:latest username/git-workflow-enforcer:latest
docker tag git-workflow-enforcer:latest username/git-workflow-enforcer:v1.0.0

# Push to Docker Hub
docker push username/git-workflow-enforcer:latest
docker push username/git-workflow-enforcer:v1.0.0
```

### GitHub Container Registry

```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag image
docker tag git-workflow-enforcer:latest ghcr.io/username/git-workflow-enforcer:latest

# Push
docker push ghcr.io/username/git-workflow-enforcer:latest
```

### Private Registry

```bash
# Tag for private registry
docker tag git-workflow-enforcer:latest registry.company.com/git-workflow-enforcer:latest

# Push
docker push registry.company.com/git-workflow-enforcer:latest
```

## Troubleshooting

### Permission Denied

**Problem:** Cannot access files in mounted volume

**Solution:** Run with correct user ID:
```bash
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  --user $(id -u):$(id -g) \
  git-workflow-enforcer
```

### Git Not Found

**Problem:** Git commands fail inside container

**Solution:** Git is included in the image. Ensure you're using the correct image:
```bash
docker run --rm git-workflow-enforcer git --version
```

### Cannot Detect Branch

**Problem:** Auto-detection fails in container

**Solution:** Mount .git directory:
```bash
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.git:/workspace/.git:ro \
  -w /workspace \
  git-workflow-enforcer
```

### Configuration Not Found

**Problem:** Custom config file not found

**Solution:** Ensure file is in mounted directory:
```bash
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer \
  python src/main/cli.py validate-all --ci --config /workspace/config/rules.json
```

## Best Practices

1. **Use specific tags** instead of `latest` in production
2. **Mount volumes read-only** when possible
3. **Run as non-root user** (default in our image)
4. **Use .dockerignore** to reduce build context
5. **Enable BuildKit** for faster builds
6. **Scan images** for vulnerabilities regularly
7. **Use multi-stage builds** for smaller images
8. **Cache layers** effectively

## Security Scanning

### Scan with Trivy

```bash
# Install Trivy
# https://github.com/aquasecurity/trivy

# Scan image
trivy image git-workflow-enforcer:latest
```

### Scan with Docker Scout

```bash
# Enable Docker Scout
docker scout quickview git-workflow-enforcer:latest

# Get detailed CVE report
docker scout cves git-workflow-enforcer:latest
```

### Scan with Snyk

```bash
# Install Snyk CLI
# https://snyk.io/

# Scan image
snyk container test git-workflow-enforcer:latest
```

## Advanced Usage

### Custom Entrypoint

```bash
docker run --rm \
  --entrypoint python \
  git-workflow-enforcer \
  src/main/cli.py --help
```

### Environment Variables

```bash
docker run --rm \
  -e NO_COLOR=1 \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer
```

### Network Mode

```bash
# Host network (for accessing local services)
docker run --rm \
  --network host \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer
```

### Resource Limits

```bash
docker run --rm \
  --memory="256m" \
  --cpus="0.5" \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer
```

## Examples

### Validate in CI Pipeline

```bash
#!/bin/bash
# validate.sh

docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer \
  python src/main/cli.py validate-all --ci

if [ $? -eq 0 ]; then
  echo "✅ Validation passed"
  exit 0
else
  echo "❌ Validation failed"
  exit 1
fi
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  git-workflow-enforcer \
  python src/main/cli.py validate-all --ci
```

### Makefile Integration

```makefile
.PHONY: validate
validate:
	docker run --rm \
		-v $(PWD):/workspace \
		-w /workspace \
		git-workflow-enforcer

.PHONY: validate-branch
validate-branch:
	docker run --rm \
		-v $(PWD):/workspace \
		-w /workspace \
		git-workflow-enforcer \
		python src/main/cli.py validate-branch --ci

.PHONY: validate-commit
validate-commit:
	docker run --rm \
		-v $(PWD):/workspace \
		-w /workspace \
		git-workflow-enforcer \
		python src/main/cli.py validate-commit --ci
```

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Project Repository](https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer)

## Support

For Docker-related issues:
1. Check this documentation
2. Verify Docker installation: `docker --version`
3. Check image: `docker images | grep git-workflow-enforcer`
4. Review logs: `docker logs <container-id>`
5. Report issues on GitHub
