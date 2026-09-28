from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import subprocess
import json
import threading
from score import calculate_score

app = FastAPI()

COLORS = {
    "CRITICAL": "#b71c1c", "HIGH": "#e64a19", "ERROR": "#e64a19",
    "MEDIUM": "#f9a825", "WARNING": "#f9a825", "LOW": "#388e3c", "INFO": "#607d8b"
}

# saara page ek jaisa dikhe — common style + head
PAGE_HEAD = """
<head>
<meta charset="utf-8">
<title>Security Agent</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: 'Segoe UI', Arial, sans-serif; background:#eef1f6; margin:0; padding:0; color:#1f2937; }
  .topbar { background:#1a237e; color:#fff; padding:18px 40px; font-size:22px; font-weight:600; }
  .container { max-width:1000px; margin:30px auto; padding:0 20px; }
  .card { background:#fff; border-radius:10px; padding:26px; box-shadow:0 2px 10px rgba(0,0,0,0.07); margin-bottom:20px; }
  input[type=text] { width:100%; padding:12px; border:1px solid #cbd5e1; border-radius:8px; font-size:15px; }
  label { font-weight:600; display:block; margin-bottom:8px; }
  button { padding:12px 22px; background:#1a237e; color:#fff; border:none; border-radius:8px; font-size:15px; cursor:pointer; margin-top:14px; }
  button:hover { background:#283593; }
  table { width:100%; border-collapse:collapse; }
  th { background:#1a237e; color:#fff; text-align:left; padding:12px; }
  td { padding:12px; border-bottom:1px solid #eee; }
  .badge { color:#fff; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold; }
  .muted { color:#6b7280; font-size:14px; }
  /* loading overlay */
  #overlay { display:none; position:fixed; inset:0; background:rgba(255,255,255,0.85);
             z-index:999; text-align:center; padding-top:15%; }
  .spinner { border:6px solid #e5e7eb; border-top:6px solid #1a237e; border-radius:50%;
             width:56px; height:56px; animation:spin 1s linear infinite; margin:0 auto 18px; }
  @keyframes spin { 100% { transform:rotate(360deg); } }
  .stats { display:flex; gap:16px; flex-wrap:wrap; margin-top:18px; }
  .stat { background:#fff; border:1px solid #eef1f6; border-radius:10px; padding:18px 26px; min-width:110px; text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.05); }
  .stat-num { font-size:32px; font-weight:700; }
  .stat-label { font-size:13px; color:#6b7280; margin-top:4px; letter-spacing:0.5px; }
  .table-wrap { overflow-x:auto; border-radius:8px; }
  table { border-radius:8px; overflow:hidden; }
  .score-box { display:inline-block; background:#1a237e; color:#fff; border-radius:12px; padding:20px 34px; text-align:center; margin-bottom:8px; }
  .score-num { font-size:44px; font-weight:800; line-height:1; }
  .score-grade { font-size:16px; margin-top:6px; opacity:0.9; }
  .score-box .stat-label { color:#c5cae9; margin-top:4px; }
</style>
<script>
  function showLoading(msg) {
    document.getElementById('loadmsg').innerText = msg;
    document.getElementById('overlay').style.display = 'block';
  }
</script>
</head>
"""

def badge(sev):
    c = COLORS.get(sev.upper(), "#607d8b")
    return f'<span class="badge" style="background:{c}">{sev.upper()}</span>'

def overlay():
    return """
    <div id="overlay">
      <div class="spinner"></div>
      <div id="loadmsg" style="font-size:18px; color:#1a237e; font-weight:600;">Processing...</div>
      <div class="muted" style="margin-top:8px;">Please wait, do not close this tab.</div>
    </div>
    """

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html>{PAGE_HEAD}
    <body>
      {overlay()}
      <div class="topbar">🛡️ Security Agent</div>
      <div class="container">
        <div class="card">
          <form action="/scan" method="post" onsubmit="showLoading('Scanning project... (2-3 minutes)')">
            <label>Project folder path</label>
            <input type="text" name="target" placeholder="e.g. backend" />
            <button type="submit">Run Scan</button>
          </form>
          <p class="muted" style="margin-top:16px;">
            Enter a local folder name or full path. The scanner checks code, dependencies, and secrets.
          </p>
        </div>
      </div>
    </body></html>
    """

@app.post("/scan", response_class=HTMLResponse)
def scan(target: str = Form(...)):
    subprocess.run(["python", "scanner.py", target])
    subprocess.run(["python", "collect.py"])

    with open("all-findings.json", "r", encoding="utf-8") as f:
        findings = json.load(f)

    order = {"CRITICAL":0,"HIGH":1,"ERROR":2,"MEDIUM":3,"WARNING":4,"LOW":5,"INFO":6}
    findings.sort(key=lambda x: order.get(x["severity"].upper(), 99))

    # summary counts
    counts = {}
    for f in findings:
        s = f["severity"].upper()
        counts[s] = counts.get(s, 0) + 1

    # security score (loop ke BAHAR — poori list pe ek baar)
    score, grade = calculate_score(findings)

    # summary cards
    cards = ""
    for sev in ["CRITICAL","HIGH","ERROR","MEDIUM","WARNING","LOW","INFO"]:
        if sev in counts:
            c = COLORS.get(sev, "#607d8b")
            cards += f"""
            <div class="stat" style="border-top:4px solid {c}">
              <div class="stat-num" style="color:{c}">{counts[sev]}</div>
              <div class="stat-label">{sev}</div>
            </div>"""

    rows = ""
    for f in findings:
        rows += f"""<tr>
          <td>{badge(f['severity'])}</td>
          <td>{f['tool']}</td>
          <td>{f['title']}</td>
          <td class="muted">{f['location']}</td>
        </tr>"""

    return f"""
    <html>{PAGE_HEAD}
    <body>
      {overlay()}
      <div class="topbar">🛡️ Security Agent</div>
      <div class="container">
        <div class="card">
          <h2 style="margin-top:0;">Scan Complete</h2>
          <p class="muted">Target: <b>{target}</b> &nbsp;|&nbsp; Total findings: <b>{len(findings)}</b></p>
          <div class="score-box">
            <div class="score-num">{score}<span style="font-size:20px;">/100</span></div>
            <div class="score-grade">Grade {grade}</div>
            <div class="stat-label">Security Score</div>
          </div>
          <div class="stats">{cards}</div>
        </div>

        <div class="card">
          <h3 style="margin-top:0;">All Findings</h3>
          <div class="table-wrap">
            <table>
              <tr><th>Severity</th><th>Tool</th><th>Title</th><th>Location</th></tr>
              {rows}
            </table>
          </div>
        </div>

        <div class="card">
          <form action="/report" method="post">
            <input type="hidden" name="target" value="{target}" />
            <p style="margin-top:0;">Generate a detailed AI report with explanations and fixes for each finding.</p>
            <button type="submit">Generate AI Report</button>
          </form>
        </div>
      </div>
    </body></html>
    """

# background mein report banane ka kaam
def run_report_job():
    subprocess.run(["python", "ai_report.py"])
    subprocess.run(["python", "make_report.py"])
    with open("progress.json", "w", encoding="utf-8") as pf:
        json.dump({"done": -1, "total": -1}, pf)   # -1 = poora ho gaya

@app.post("/report", response_class=HTMLResponse)
def report(target: str = Form(...)):
    # report ka kaam background mein shuru karo
    threading.Thread(target=run_report_job).start()

    # progress bar wala page turant dikhao
    return """
    <html>""" + PAGE_HEAD + """
    <body>
      <div class="topbar">🛡️ Security Agent</div>
      <div class="container">
        <div class="card">
          <h2 style="margin-top:0;">Generating AI Report...</h2>
          <p class="muted">The local AI is analysing each finding. This runs on your machine and may take several minutes.</p>
          <div style="background:#e5e7eb; border-radius:20px; height:26px; overflow:hidden; margin-top:20px;">
            <div id="bar" style="background:#1a237e; height:100%; width:0%; transition:width 0.4s; text-align:center; color:#fff; font-size:13px; line-height:26px;">0%</div>
          </div>
          <p id="status" class="muted" style="margin-top:12px;">Starting...</p>
        </div>
      </div>
      <script>
        const timer = setInterval(async () => {
          const res = await fetch('/progress');
          const data = await res.json();
          if (data.done === -1) {
            clearInterval(timer);
            window.location.href = '/view-report';
            return;
          }
          if (data.total > 0) {
            const pct = Math.round(data.done / data.total * 100);
            document.getElementById('bar').style.width = pct + '%';
            document.getElementById('bar').innerText = pct + '%';
            document.getElementById('status').innerText =
              data.done + ' of ' + data.total + ' findings analysed';
          }
        }, 2000);
      </script>
    </body></html>
    """

@app.get("/view-report", response_class=HTMLResponse)
def view_report():
    with open("report.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/progress")
def progress():
    try:
        with open("progress.json", "r", encoding="utf-8") as f:
            return JSONResponse(json.load(f))
    except:
        return JSONResponse({"done": 0, "total": 0})