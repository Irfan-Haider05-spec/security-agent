import json

# JSON file ko kholke python main padho
def load_json(filename):
    with open(filename, "r", encoding="utf-8", errors="replace") as f:
        return json.load(f)

# Semgrep k results ko common shakal do.
def parse_semgrep():
    data = load_json("semgrep-out.json")
    findings = []
    for item in data.get("results", []):
        findings.append({
            "tool": "Semgrep",
            "title": item.get("check_id", "unknown"),
            "severity": item.get("extra", {}).get("severity", "UNKNOWN"),
            "location": item.get("path", "") + ":" + str(item.get("start", {}).get("line", "")),
            "details": item.get("extra", {}).get("message", "")
        })
    return findings

# Trivy k results ko simple shakal do.
def parse_trivy():
    data = load_json("trivy-out.json")
    findings = []
    for result in data.get("Results", []):
        vulns = result.get("Vulnerabilities")
        if not vulns:          # agar is result mein koi vulnerability nahi, chhod do
            continue
        for vuln in vulns:
            sev = vuln.get("Severity", "UNKNOWN")
            if sev not in ("CRITICAL", "HIGH"):   # sirf badi aag; MEDIUM/LOW abhi chhod do
                continue
            findings.append({
                "tool": "trivy",
                "title": vuln.get("VulnerabilityID", "unknown") + " in " + vuln.get("PkgName", ""),
                "severity": sev,
                "location": vuln.get("PkgName", "") + " " + vuln.get("InstalledVersion", ""),
                "detail": vuln.get("Title", "") + " | Fix: upgrade to " + vuln.get("FixedVersion", "N/A")
            })
    return findings

# Gitleaks ke results ko common shakl do
def parse_gitleaks():
    data = load_json("gitleaks-out.json")
    findings = []
    for item in data:
        findings.append({
            "tool": "gitleaks",
            "title": "Hardcoded secret: " + item.get("RuleID", "unknown"),
            "severity": "HIGH",
            "location": item.get("File", "") + ":" + str(item.get("StartLine", "")),
            "detail": item.get("Description", "Secret/key found in code")
        })
    return findings

# teeno ko alag-alag gino
s = parse_semgrep()
t = parse_trivy()
g = parse_gitleaks()

all_findings = s + t + g

# duplicates hatao — same title + location ek hi baar
unique = {}
for f in all_findings:
    key = f["title"] + "|" + f["location"]
    unique[key] = f
all_findings = list(unique.values())

with open("all-findings.json", "w", encoding="utf-8") as f:
    json.dump(all_findings, f, indent=2)

print(f"Total (duplicates hatane ke baad): {len(all_findings)} -> all-findings.json")

