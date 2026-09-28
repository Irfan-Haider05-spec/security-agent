import json
from datetime import datetime

# report padho
with open("ai-report.json", "r", encoding="utf-8") as f:
    findings = json.load(f)

# severity ka order (CRITICAL sabse upar)
order = {"CRITICAL": 0, "HIGH": 1, "ERROR": 2, "MEDIUM": 3, "WARNING": 4, "LOW": 5, "INFO": 6}
findings.sort(key=lambda x: order.get(x["severity"].upper(), 99))

# har severity kitni hai — ginti
counts = {}
for f in findings:
    sev = f["severity"].upper()
    counts[sev] = counts.get(sev, 0) + 1

# har severity ka rang
colors = {
    "CRITICAL": "#b71c1c", "HIGH": "#e64a19", "ERROR": "#e64a19",
    "MEDIUM": "#f9a825", "WARNING": "#f9a825", "LOW": "#388e3c", "INFO": "#607d8b"
}

# summary ka HTML banao
summary_html = ""
for sev, num in counts.items():
    c = colors.get(sev, "#607d8b")
    summary_html += f'<span class="badge" style="background:{c}">{sev}: {num}</span> '

# har finding ka HTML banao
cards_html = ""
for f in findings:
    sev = f["severity"].upper()
    c = colors.get(sev, "#607d8b")
    explanation = f["explanation"].replace("\n", "<br>")
    cards_html += f"""
    <div class="card">
      <div class="card-head">
        <span class="badge" style="background:{c}">{sev}</span>
        <span class="tool">{f['tool']}</span>
      </div>
      <h3>{f['title']}</h3>
      <p class="loc">📍 {f['location']}</p>
      <div class="explain">{explanation}</div>
    </div>
    """

# poora page
html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Security Report</title>
<style>
  @media print {{
    button {{ display: none; }}
  }}
  body {{ font-family: Arial, sans-serif; background:#f4f4f4; margin:0; padding:20px; color:#222; }}
  h1 {{ color:#1a237e; }}
  .meta {{ color:#666; margin-bottom:20px; }}
  .badge {{ color:#fff; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold; }}
  .summary {{ margin:20px 0; }}
  .card {{ background:#fff; border-radius:8px; padding:16px; margin-bottom:14px; box-shadow:0 1px 4px rgba(0,0,0,0.1); }}
  .card-head {{ display:flex; gap:10px; align-items:center; margin-bottom:8px; }}
  .tool {{ color:#666; font-size:13px; text-transform:uppercase; }}
  .loc {{ color:#777; font-size:13px; }}
  .explain {{ background:#fafafa; padding:12px; border-radius:6px; margin-top:8px; line-height:1.6; }}
  h3 {{ margin:6px 0; }}
</style>
</head>
<body>
  <button onclick="window.print()"
    style="position:fixed; top:20px; right:20px; padding:10px 18px; background:#1a237e; color:#fff; border:none; border-radius:8px; cursor:pointer; font-size:14px; z-index:100;">
    ⬇ Download / Print Report
  </button>
  <h1>🛡️ Security Scan Report</h1>
  <p class="meta">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} &nbsp;|&nbsp; Total findings: {len(findings)}</p>
  <div class="summary">{summary_html}</div>
  {cards_html}
</body>
</html>"""

with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Report ban gayi -> report.html")