import os
import glob
import re

SCRATCH_DIR = r"C:\Users\Admin\.gemini\antigravity\scratch\generalpedia"

html_files = glob.glob(os.path.join(SCRATCH_DIR, "*.html")) + glob.glob(os.path.join(SCRATCH_DIR, "category", "*.html"))

issues = []

print(f"Auditing {len(html_files)} HTML files...\n")

for fpath in html_files:
    if fpath.endswith("template_body.html"):
        continue
    rel_path = os.path.relpath(fpath, SCRATCH_DIR).replace("\\", "/")
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Check H1 count
    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
    h1_count = len(h1_matches)

    # 2. Check Meta Description
    meta_m = re.search(r'<meta name="description" content="(.*?)">', html, re.DOTALL | re.IGNORECASE)
    meta_desc = meta_m.group(1) if meta_m else ""
    meta_len = len(meta_desc)

    # 3. Check Canonical
    canon_m = re.search(r'<link rel="canonical" href="(.*?)">', html, re.DOTALL | re.IGNORECASE)
    canon_url = canon_m.group(1) if canon_m else ""

    file_issues = []
    if h1_count != 1:
        file_issues.append(f"H1 count != 1 (found {h1_count})")
    if meta_len > 155:
        file_issues.append(f"Meta desc > 155 chars ({meta_len} chars)")
    if not canon_url:
        file_issues.append("Missing canonical tag")
    if ".html" in canon_url:
        file_issues.append(f"Canonical has .html ({canon_url})")

    if file_issues:
        issues.append((rel_path, file_issues))
        print(f"[FAIL] {rel_path}: {', '.join(file_issues)}")
    else:
        h1_text = re.sub(r'<[^>]+>', '', h1_matches[0]).strip() if h1_matches else ""
        h1_clean = h1_text.replace('\n', ' ').strip()
        print(f"[OK] {rel_path} | H1 (1): '{h1_clean[:35]}' | Desc: {meta_len} chars | Canonical: {canon_url}")

print(f"\nAudit complete. Total files: {len(html_files)}, Total Issues: {len(issues)}")
