import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b-instruct-q4_K_M"

def ask_model(prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"]

def build_prompt(f):
    return f"""You are a security expert helping a developer.
Explain this security finding clearly and briefly in simple English.

Answer in exactly 3 short sections:
1. Problem: what is wrong (1-2 sentences)
2. Risk: why it matters (1 sentence)
3. Fix: the general steps to fix it (1-2 sentences)

Important: Do NOT invent version numbers, commit hashes, or file names.
If the detail contains an example value, treat it only as an example, not the real answer.
Keep it practical and short.

Finding:
Tool: {f['tool']}
Title: {f['title']}
Severity: {f['severity']}
Location: {f['location']}
Detail: {f.get('detail', f.get('details', ''))}
"""

with open("all-findings.json", "r", encoding="utf-8") as f:
    findings = json.load(f)

results = []
total = len(findings)

with open("progress.json", "w", encoding="utf-8") as pf:
    json.dump({"done": 0, "total": len(findings)}, pf)

for i, finding in enumerate(findings):
    print(f"Processing {i+1}/{total} ...")
    explanation = ask_model(build_prompt(finding))
    results.append({
        "tool": finding["tool"],
        "title": finding["title"],
        "severity": finding["severity"],
        "location": finding["location"],
        "explanation": explanation
    })
    with open("progress.json", "w", encoding="utf-8") as pf:
        json.dump({"done": i + 1, "total": total}, pf)

with open("ai-report.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"\nHo gaya! {total} findings explain kiye -> ai-report.json")