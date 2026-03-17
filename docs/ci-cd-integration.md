# CI/CD Integration

## GitHub Actions

```yaml
- name: Validate branch
  run: python -m src.main.cli validate-branch "${{ github.ref_name }}"

- name: Validate commit
  run: python -m src.main.cli validate-commit "${{ github.event.head_commit.message }}"
```

## GitLab CI

```yaml
validate:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python -m src.main.cli validate-branch $CI_COMMIT_REF_NAME
    - python -m src.main.cli validate-commit "$CI_COMMIT_MESSAGE"
```

## Jenkins

```groovy
stage('Validate') {
    steps {
        sh 'pip install -r requirements.txt'
        sh "python -m src.main.cli validate-branch ${env.BRANCH_NAME}"
        sh "python -m src.main.cli validate-commit '${env.GIT_COMMIT_MESSAGE}'"
    }
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed |
| 1 | Validation failed |
| 2 | Configuration error |

## Notes

- Use `--verbose` for detailed output in logs
- Rules are loaded from `src/config/rules.json` — commit this file to your repo
- All validators return non-zero exit codes on failure, making them pipeline-safe
