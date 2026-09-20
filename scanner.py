import subprocess
import sys

# Jis Project ko Scan Karna Hai os ka Folder
TARGET = sys.argv[1] if len(sys.argv) > 1 else "backend"

def run_semgrep(target):
    print(f"Semgrep is Running on {target}...")
    subprocess.run([
        "semgrep",
        "--config=auto",
        target,
        "--json",
        "--output", "semgrep-out.json"
    ])
    print("Semgrep Scan completed. Results saved in semgrep-out.json")


def run_trivy(target):
    print(f"Trivy is running on {target}...")
    subprocess.run([
        "trivy", "fs", target,
        "--scanners=vuln",
        "--include-dev-deps",
        "--format=json",
        "--output=trivy-out.json"
    ])
    print("Trivy Scan completed. Results saved in trivy-out.json")


def run_gitleaks(target):
    print(f"Gitleaks is running on {target}...")
    subprocess.run([
        "gitleaks", "detect",
        "--source", target,
        "--report-path", "gitleaks-out.json",
        "--report-format", "json"
    ])
    print("Gitleaks Scan completed. Results saved in gitleaks-out.json")


run_semgrep(TARGET)
run_trivy(TARGET)
run_gitleaks(TARGET)
