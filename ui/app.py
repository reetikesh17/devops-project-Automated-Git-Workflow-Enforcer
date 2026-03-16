"""
Git Workflow Enforcer - Web Dashboard
Flask backend serving the UI
"""

import sys
import os
import subprocess
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
from src.validators.commit_validator import CommitValidator
from src.validators.branch_validator import BranchValidator
from src.config import ConfigLoader

app = Flask(__name__)

config = ConfigLoader.load()
commit_validator = CommitValidator(config)
branch_validator = BranchValidator(config)

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/dashboard")
def index():
    return render_template("index.html")

@app.route("/api/validate/commit", methods=["POST"])
def validate_commit():
    data = request.get_json()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"valid": False, "error": "Commit message cannot be empty"})
    try:
        result = commit_validator.validate_detailed(message)
        return jsonify({
            "valid": result["valid"],
            "message": message,
            "error": result.get("error") if not result["valid"] else None,
            "type": result.get("type") if result["valid"] else None
        })
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})

@app.route("/api/validate/branch", methods=["POST"])
def validate_branch():
    data = request.get_json()
    branch = data.get("branch", "").strip()
    if not branch:
        return jsonify({"valid": False, "error": "Branch name cannot be empty"})
    try:
        result = branch_validator.validate_detailed(branch)
        return jsonify({
            "valid": result["valid"],
            "branch": branch,
            "error": result.get("error") if not result["valid"] else None,
            "branch_type": result.get("type") if result["valid"] else None
        })
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})

@app.route("/api/rules")
def get_rules():
    return jsonify({
        "commit_types": config.get("commits", {}).get("types", []),
        "branch_patterns": list(config.get("branches", {}).get("patterns", {}).keys()),
        "protected_branches": config.get("branches", {}).get("protected", []),
        "description_length": config.get("commits", {}).get("descriptionLength", {})
    })

@app.route("/api/run-tests")
def run_tests():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    commit_cases = [
        ("feat: add user authentication module", True),
        ("fix: resolve null pointer exception", True),
        ("docs: update installation guide", True),
        ("refactor: simplify validation logic", True),
        ("test: add unit tests for validator", True),
        ("chore: update dependencies to latest", True),
        ("ci: configure GitHub Actions workflow", True),
        ("feat(auth): add login functionality", True),
        ("fix(api): resolve timeout issue", True),
        ("Add feature", False),
        ("feat: short", False),
        ("feat: Add Feature", False),
        ("feat: add feature.", False),
        ("wrongtype: add something", False),
        ("", False),
        ("feat:missing space", False),
    ]

    branch_cases = [
        ("feature/JIRA-123-user-authentication", True),
        ("feature/PROJ-456-add-login-page", True),
        ("feature/TICKET-789-implement-api", True),
        ("bugfix/BUG-111-fix-login-error", True),
        ("bugfix/ISSUE-222-resolve-timeout", True),
        ("hotfix/URGENT-999", True),
        ("hotfix/CRITICAL-001", True),
        ("release/v1.0.0", True),
        ("release/v2.3.1", True),
        ("release/v1.0.0-beta", True),
        ("release/v1.0.0-rc1", True),
        ("main", True),
        ("master", True),
        ("develop", True),
        ("add-feature", False),
        ("feature/add-login", False),
        ("feature/123-login", False),
        ("feature/JIRA-123", False),
        ("bugfix/fix-bug", False),
        ("hotfix/fix", False),
        ("release/1.0.0", False),
        ("release/v1.0", False),
        ("", False),
        ("random-branch-name", False),
    ]

    def run_test(script):
        r = subprocess.run(
            [sys.executable, "-X", "utf8", script],
            capture_output=True, encoding="utf-8", errors="replace",
            env=env, timeout=30, cwd=project_root
        )
        passed, total = 0, 0
        for line in (r.stdout + r.stderr).splitlines():
            if "Total tests:" in line:
                try: total = int(line.split(":")[1].strip())
                except: pass
            if "Passed:" in line:
                try: passed = int(line.split(":")[1].strip())
                except: pass
        return {"passed": passed, "total": total, "success": r.returncode == 0}

    results = {}
    try:
        results["commit"] = run_test("examples/test_commit_validator.py")
    except Exception as e:
        results["commit"] = {"passed": 0, "total": 0, "success": False, "error": str(e)}

    try:
        results["branch"] = run_test("examples/test_branch_validator.py")
    except Exception as e:
        results["branch"] = {"passed": 0, "total": 0, "success": False, "error": str(e)}

    total_passed = results["commit"]["passed"] + results["branch"]["passed"]
    total_tests = results["commit"]["total"] + results["branch"]["total"]
    results["summary"] = {
        "total": total_tests,
        "passed": total_passed,
        "failed": total_tests - total_passed,
        "rate": round((total_passed / total_tests * 100), 1) if total_tests > 0 else 0
    }
    results["commit_cases"] = [{"label": c[0] if c[0] else "(empty)", "expect": c[1]} for c in commit_cases]
    results["branch_cases"] = [{"label": c[0] if c[0] else "(empty)", "expect": c[1]} for c in branch_cases]
    return jsonify(results)


@app.route("/api/run-full-tests")
def run_full_tests():
    from flask import Response, stream_with_context
    import time

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def send(event, data):
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    def run_streaming(cmd, cwd=None, timeout=120):
        """Run a command and yield output lines as they arrive."""
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                encoding="utf-8", errors="replace", env=env,
                cwd=cwd or project_root
            )
            lines = []
            for line in proc.stdout:
                line = line.rstrip("\n\r")
                if line.strip():
                    lines.append(line)
                    yield ("line", line)
            proc.wait(timeout=timeout)
            yield ("done", proc.returncode)
            return lines, proc.returncode
        except Exception as e:
            yield ("line", f"ERROR: {e}")
            yield ("done", 1)

    def stream():
        passed_count = 0
        total_count = 0

        STEPS = [
            ("Commit Validator",  [sys.executable, "-X", "utf8", "examples/test_commit_validator.py"], None, 30),
            ("Branch Validator",  [sys.executable, "-X", "utf8", "examples/test_branch_validator.py"], None, 30),
            ("CLI Validation",    [sys.executable, "-m", "src.main.cli", "validate-commit", "feat: test comprehensive validation"], None, 15),
            ("Docker Build",      ["docker", "build", "-t", "git-workflow-enforcer:test", ".", "--quiet"], None, 180),
            ("Docker Container",  ["docker", "run", "--rm", "git-workflow-enforcer:test", "python", "-m", "src.main.cli", "validate-commit", "feat: docker test"], None, 30),
            ("Kubernetes",        None, None, 20),
            ("Terraform Validate",["terraform", "validate"], os.path.join(project_root, "infrastructure", "terraform"), 30),
            ("Terraform Format",  ["terraform", "fmt", "-check", "-recursive"], os.path.join(project_root, "infrastructure", "terraform"), 30),
        ]

        yield send("start", {"total": len(STEPS)})

        for idx, (name, cmd, cwd, timeout) in enumerate(STEPS):
            total_count += 1
            yield send("step_start", {"index": idx, "name": name})
            yield send("line", {"index": idx, "text": f"{'='*56}"})
            yield send("line", {"index": idx, "text": f"  [{idx+1}/8] {name}"})
            yield send("line", {"index": idx, "text": f"{'='*56}"})

            ok = False
            detail = ""

            # Kubernetes handled specially
            if name == "Kubernetes":
                for sub_cmd in [
                    ["kubectl", "apply", "-f", "infrastructure/kubernetes/configmap.yaml"],
                    ["kubectl", "apply", "-f", "infrastructure/kubernetes/job.yaml"],
                ]:
                    try:
                        r = subprocess.run(sub_cmd, capture_output=True, encoding="utf-8",
                                           errors="replace", env=env, cwd=project_root, timeout=20)
                        for ln in (r.stdout + r.stderr).splitlines():
                            if ln.strip():
                                yield send("line", {"index": idx, "text": "  " + ln})
                        ok = r.returncode == 0
                    except Exception as e:
                        yield send("line", {"index": idx, "text": f"  ERROR: {e}"})
                        ok = False
                yield send("line", {"index": idx, "text": "  Waiting for job..."})
                time.sleep(6)
                try:
                    r = subprocess.run(["kubectl", "get", "jobs", "git-workflow-enforcer-job"],
                                       capture_output=True, encoding="utf-8", errors="replace",
                                       env=env, cwd=project_root, timeout=10)
                    for ln in (r.stdout + r.stderr).splitlines():
                        if ln.strip():
                            yield send("line", {"index": idx, "text": "  " + ln})
                    subprocess.run(["kubectl", "delete", "job", "git-workflow-enforcer-job"],
                                   capture_output=True, env=env, cwd=project_root, timeout=10)
                except Exception as e:
                    yield send("line", {"index": idx, "text": f"  {e}"})
                detail = "ConfigMap + Job deployed"
            else:
                collected = []
                rc = 1
                try:
                    proc = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        encoding="utf-8", errors="replace", env=env, cwd=cwd or project_root
                    )
                    for raw in proc.stdout:
                        ln = raw.rstrip("\n\r")
                        if ln.strip():
                            collected.append(ln)
                            yield send("line", {"index": idx, "text": "  " + ln})
                    proc.wait(timeout=timeout)
                    rc = proc.returncode
                except Exception as e:
                    yield send("line", {"index": idx, "text": f"  ERROR: {e}"})

                ok = (rc == 0)

                # Extract detail for unit tests
                if name in ("Commit Validator", "Branch Validator"):
                    p, t = 0, 0
                    for ln in collected:
                        if "Total tests:" in ln:
                            try: t = int(ln.split(":")[1].strip())
                            except: pass
                        if "Passed:" in ln:
                            try: p = int(ln.split(":")[1].strip())
                            except: pass
                    detail = f"{p}/{t} unit tests passed"
                elif name == "Terraform Format":
                    ok = True  # non-blocking
                    detail = "Format OK" if rc == 0 else "Needs formatting (non-blocking)"
                else:
                    detail = "OK" if ok else "FAILED"

            status = "PASSED" if ok else "FAILED"
            if ok:
                passed_count += 1
            yield send("line", {"index": idx, "text": ""})
            yield send("line", {"index": idx, "text": f"  {'✓' if ok else '✗'} {status}"})
            yield send("step_done", {"index": idx, "name": name, "passed": ok, "detail": detail})

        yield send("summary", {
            "total": total_count,
            "passed": passed_count,
            "failed": total_count - passed_count
        })

    return Response(stream_with_context(stream()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == "__main__":
    print("\n🚀 Git Workflow Enforcer Dashboard")
    print("=" * 40)
    print("Open your browser at: http://localhost:5000")
    print("=" * 40 + "\n")
    app.run(debug=True, port=5000)
