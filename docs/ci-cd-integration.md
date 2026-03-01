# CI/CD Integration Guide

## Overview

The Git Workflow Enforcer is optimized for CI/CD pipelines with a dedicated `--ci` flag that provides:

- **Structured JSON output** for easy parsing
- **Exit codes 0/1 only** (success/failure)
- **No colored output** (pipeline-friendly)
- **Minimal logging** (warnings and errors only)
- **No interactive prompts**

## CI Mode Features

### Exit Codes

In CI mode, the tool uses simplified exit codes:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | All validations passed |
| 1 | Failure | Any validation, configuration, or runtime error |

This simplifies pipeline logic as you only need to check for success (0) or failure (1).

### JSON Output

All validation results are returned as structured JSON:

```json
{
  "type": "commit",
  "valid": true,
  "status": "pass",
  "validation_type": "feat"
}
```

For failures:

```json
{
  "type": "commit",
  "valid": false,
  "status": "fail",
  "error": "Invalid commit message format",
  "error_type": "INVALID_FORMAT"
}
```

## GitHub Actions Integration

### Basic Workflow

```yaml
name: Validate Git Workflow

on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Validate branch
        run: |
          python src/main/cli.py --ci validate-branch "${{ github.ref_name }}"
      
      - name: Validate commit
        run: |
          python src/main/cli.py --ci validate-commit "${{ github.event.head_commit.message }}"
```

### Advanced Workflow with PR Validation

```yaml
name: PR Validation

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Fetch all history
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Validate all commits in PR
        run: |
          for commit in $(git rev-list origin/${{ github.base_ref }}..${{ github.sha }}); do
            message=$(git log --format=%B -n 1 $commit)
            echo "::group::Validating commit $commit"
            if ! python src/main/cli.py --ci validate-commit "$message"; then
              echo "::error::Commit $commit has invalid message"
              exit 1
            fi
            echo "::endgroup::"
          done
      
      - name: Validate branch name
        run: |
          python src/main/cli.py --ci validate-branch "${{ github.head_ref }}"
      
      - name: Generate summary
        if: always()
        run: |
          echo "## Validation Results" >> $GITHUB_STEP_SUMMARY
          python src/main/cli.py --ci validate-all \
            "${{ github.head_ref }}" \
            "${{ github.event.pull_request.title }}" \
            >> $GITHUB_STEP_SUMMARY
```

### Using JSON Output

```yaml
- name: Validate and parse result
  id: validate
  run: |
    result=$(python src/main/cli.py --ci validate-commit "${{ github.event.head_commit.message }}")
    echo "result=$result" >> $GITHUB_OUTPUT
    echo "$result" | jq .

- name: Check validation status
  run: |
    if [ "$(echo '${{ steps.validate.outputs.result }}' | jq -r .valid)" = "true" ]; then
      echo "✅ Validation passed"
    else
      echo "❌ Validation failed"
      exit 1
    fi
```

## GitLab CI Integration

### Basic Pipeline

```yaml
validate:
  stage: test
  image: python:3.8
  script:
    - python src/main/cli.py --ci validate-branch $CI_COMMIT_REF_NAME
    - python src/main/cli.py --ci validate-commit "$CI_COMMIT_MESSAGE"
  only:
    - merge_requests
    - main
```

### Advanced Pipeline

```yaml
validate-commits:
  stage: validate
  image: python:3.8
  script:
    - |
      for commit in $(git rev-list $CI_MERGE_REQUEST_DIFF_BASE_SHA..$CI_COMMIT_SHA); do
        message=$(git log --format=%B -n 1 $commit)
        python src/main/cli.py --ci validate-commit "$message" || exit 1
      done
  only:
    - merge_requests

validate-branch:
  stage: validate
  image: python:3.8
  script:
    - python src/main/cli.py --ci validate-branch $CI_COMMIT_REF_NAME
  only:
    - merge_requests
```

## Jenkins Integration

### Declarative Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Validate Branch') {
            steps {
                script {
                    def result = sh(
                        script: "python src/main/cli.py --ci validate-branch ${env.BRANCH_NAME}",
                        returnStatus: true
                    )
                    if (result != 0) {
                        error('Branch validation failed')
                    }
                }
            }
        }
        
        stage('Validate Commits') {
            when {
                changeRequest()
            }
            steps {
                script {
                    def commits = sh(
                        script: "git rev-list origin/${env.CHANGE_TARGET}..HEAD",
                        returnStdout: true
                    ).trim().split('\n')
                    
                    commits.each { commit ->
                        def message = sh(
                            script: "git log --format=%B -n 1 ${commit}",
                            returnStdout: true
                        ).trim()
                        
                        def result = sh(
                            script: "python src/main/cli.py --ci validate-commit '${message}'",
                            returnStatus: true
                        )
                        
                        if (result != 0) {
                            error("Commit ${commit} validation failed")
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                // Generate validation report
                sh '''
                    python src/main/cli.py --ci validate-all \
                        "${BRANCH_NAME}" \
                        "${GIT_COMMIT_MESSAGE}" \
                        > validation-report.json
                '''
                archiveArtifacts artifacts: 'validation-report.json'
            }
        }
    }
}
```

## CircleCI Integration

```yaml
version: 2.1

jobs:
  validate:
    docker:
      - image: python:3.8
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: pip install -r requirements.txt
      
      - run:
          name: Validate branch
          command: |
            python src/main/cli.py --ci validate-branch $CIRCLE_BRANCH
      
      - run:
          name: Validate commits
          command: |
            if [ -n "$CIRCLE_PULL_REQUEST" ]; then
              for commit in $(git rev-list origin/main..HEAD); do
                message=$(git log --format=%B -n 1 $commit)
                python src/main/cli.py --ci validate-commit "$message"
              done
            fi

workflows:
  version: 2
  validate:
    jobs:
      - validate
```

## Azure Pipelines Integration

```yaml
trigger:
  - main
  - develop

pr:
  - main
  - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.8'
  
- script: |
    pip install -r requirements.txt
  displayName: 'Install dependencies'

- script: |
    python src/main/cli.py --ci validate-branch $(Build.SourceBranchName)
  displayName: 'Validate branch name'

- script: |
    python src/main/cli.py --ci validate-commit "$(Build.SourceVersionMessage)"
  displayName: 'Validate commit message'

- script: |
    python src/main/cli.py --ci validate-all \
      $(Build.SourceBranchName) \
      "$(Build.SourceVersionMessage)" \
      > $(Build.ArtifactStagingDirectory)/validation-report.json
  displayName: 'Generate validation report'
  condition: always()

- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: '$(Build.ArtifactStagingDirectory)'
    artifactName: 'validation-report'
  condition: always()
```

## Command Reference

### Validate Commit Message

```bash
# Interactive mode (colored output)
python src/main/cli.py validate-commit "feat: add feature"

# CI mode (JSON output, exit 0/1)
python src/main/cli.py --ci validate-commit "feat: add feature"
```

### Validate Branch Name

```bash
# Interactive mode
python src/main/cli.py validate-branch feature/JIRA-123-test

# CI mode
python src/main/cli.py --ci validate-branch feature/JIRA-123-test

# Validate current branch
python src/main/cli.py --ci validate-branch
```

### Validate Both

```bash
# Interactive mode
python src/main/cli.py validate-all feature/JIRA-123-test "feat: add test"

# CI mode
python src/main/cli.py --ci validate-all feature/JIRA-123-test "feat: add test"
```

## Parsing JSON Output

### Using jq

```bash
# Extract validation status
result=$(python src/main/cli.py --ci validate-commit "feat: test")
echo "$result" | jq -r .valid

# Extract error message
echo "$result" | jq -r .error

# Check if validation passed
if [ "$(echo "$result" | jq -r .valid)" = "true" ]; then
  echo "Validation passed"
fi
```

### Using Python

```python
import subprocess
import json

result = subprocess.run(
    ['python', 'src/main/cli.py', '--ci', 'validate-commit', 'feat: test'],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
if data['valid']:
    print(f"✓ Valid {data['validation_type']} commit")
else:
    print(f"✗ Error: {data['error']}")
```

## Best Practices

1. **Always use `--ci` flag in pipelines** for consistent output
2. **Validate all commits in PRs** not just the latest
3. **Cache validation results** to avoid redundant checks
4. **Generate reports** for failed validations
5. **Use structured logging** for debugging
6. **Set up branch protection** rules based on validation
7. **Document validation rules** in your repository

## Troubleshooting

### Exit Code Always 1

Check if you're using `--ci` flag. Without it, exit codes can be 0-4.

### JSON Parsing Errors

Ensure you're capturing stdout only:
```bash
result=$(python src/main/cli.py --ci validate-commit "test" 2>/dev/null)
```

### Validation Passes Locally but Fails in CI

Check that:
- Configuration file is committed
- Python version matches (3.8+)
- No environment-specific issues

## Support

For issues with CI/CD integration:
1. Check this documentation
2. Review example workflows
3. Test locally with `--ci` flag
4. Check project issues on GitHub
