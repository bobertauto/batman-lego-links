#!/usr/bin/env python3
"""Auto-refresh the affiliate page: best-effort dead-link check -> regenerate -> commit+push.
   Conservative: only DEACTIVATES a product on a hard 404/410 (clearly gone). Captcha/unknown
   responses are LEFT ACTIVE and just logged (Amazon bot-blocks server requests, so we never
   remove a live product on a false signal). For a thorough check, run the in-session browser
   checker instead. Intended to run weekly via launchd.
"""
import json, os, subprocess, urllib.request, urllib.error, time

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "products.json")))
TAG = data["tag"]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def check(asin):
    """Return 'dead' (hard 404/410), 'ok' (200/redirect), or 'unknown' (blocked/captcha/err)."""
    url = f"https://www.amazon.com/dp/{asin}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read(60000).decode("utf-8", "ignore").lower()
            if "page not found" in body or "the web address you entered is not a functioning page" in body:
                return "dead"
            return "ok"
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return "dead"
        return "unknown"
    except Exception:
        return "unknown"

changed, log = False, []
for sec in data["sections"]:
    for p in sec["products"]:
        if not p.get("asin") or not p.get("active", True):
            continue
        st = check(p["asin"])
        log.append(f'{st:8} {p["asin"]}  {p["title"][:40]}')
        if st == "dead":
            p["active"] = False
            changed = True
        time.sleep(1.5)

print("\n".join(log))
if changed:
    json.dump(data, open(os.path.join(HERE, "products.json"), "w"), indent=2)
    print("deactivated dead products -> products.json updated")

# regenerate always (picks up any manual json edits too)
subprocess.run(["/Library/Frameworks/Python.framework/Versions/3.14/bin/python3",
                os.path.join(HERE, "generate.py")], check=True)

# commit + push only if the working tree changed
os.chdir(HERE)
diff = subprocess.run(["git", "diff", "--quiet"]).returncode
if diff != 0:
    subprocess.run(["git", "add", "-A"])
    subprocess.run(["git", "commit", "-m", "auto-refresh affiliate links"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("pushed update -> GitHub Pages will redeploy")
else:
    print("no changes to push")
