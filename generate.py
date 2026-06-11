#!/usr/bin/env python3
"""Generate index.html from products.json. Run after editing products.json.
   Update links with ZERO manual pasting: edit products.json -> `python3 generate.py` -> git push (Pages auto-deploys).
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "products.json")))
TAG = data["tag"]

def esc(s): return html.escape(s, quote=True)

def product_html(p):
    url = f'https://www.amazon.com/dp/{p["asin"]}/?tag={TAG}'
    return (f'  <a class="btn" href="{url}" target="_blank" rel="noopener nofollow sponsored">\n'
            f'    <span class="ico">{p["icon"]}</span><span class="meta">'
            f'<div class="t">{esc(p["title"])}</div><div class="d">{esc(p["desc"])}</div></span>'
            f'<span class="arr">›</span></a>')

blocks = []
for sec in data["sections"]:
    active = [p for p in sec["products"] if p.get("active", True) and p.get("asin")]
    if not active:
        continue
    blocks.append(f'  <div class="sec">{sec["name"]}</div>')
    blocks.extend(product_html(p) for p in active)

body = "\n".join(blocks)
HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(data["title"])} | {esc(data["handle"])}</title>
<meta name="description" content="{esc(data["tagline"])}">
<style>
  :root{{ --bg:#0c0d10; --card:#16181d; --line:#23262d; --yellow:#ffd400; --txt:#f2f3f5; --sub:#9aa0aa; }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--txt);font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
       -webkit-font-smoothing:antialiased;padding:0 18px 60px;max-width:560px;margin:0 auto}}
  header{{text-align:center;padding:34px 0 14px}}
  .bat{{font-size:40px;line-height:1}}
  h1{{font-size:22px;letter-spacing:.3px;margin:10px 0 4px}}
  .handle{{color:var(--yellow);font-weight:700;font-size:15px}}
  .tag{{color:var(--sub);font-size:13px;margin-top:8px;line-height:1.5}}
  .sec{{margin:26px 0 10px;color:var(--sub);font-size:12px;letter-spacing:1.6px;text-transform:uppercase;font-weight:700}}
  a.btn{{display:flex;align-items:center;gap:14px;background:var(--card);border:1px solid var(--line);
        border-radius:16px;padding:15px 16px;margin:11px 0;text-decoration:none;color:var(--txt);
        transition:transform .08s ease,border-color .15s ease}}
  a.btn:active{{transform:scale(.985)}}
  a.btn:hover{{border-color:var(--yellow)}}
  .ico{{font-size:24px;width:30px;text-align:center}}
  .meta{{flex:1;min-width:0}}
  .t{{font-weight:650;font-size:15px}}
  .d{{color:var(--sub);font-size:12.5px;margin-top:2px}}
  .arr{{color:var(--yellow);font-weight:800;font-size:18px}}
  footer{{margin-top:30px;text-align:center;color:var(--sub);font-size:11px;line-height:1.6}}
</style>
</head>
<body>
  <header>
    <div class="bat">{data["bat"]}</div>
    <h1>{esc(data["title"])}</h1>
    <div class="handle">{esc(data["handle"])}</div>
    <div class="tag">{esc(data["tagline"])}</div>
  </header>

{body}

  <footer>
    As an Amazon Associate I earn from qualifying purchases.<br>© {esc(data["handle"])}
  </footer>
</body>
</html>
"""
open(os.path.join(HERE, "index.html"), "w").write(HTML)
n = sum(1 for s in data["sections"] for p in s["products"] if p.get("active", True) and p.get("asin"))
print(f"generated index.html with {n} active products (tag={TAG})")
