import os
import glob
import re
import json

SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))

all_html_files = (
    glob.glob(os.path.join(SCRATCH_DIR, "*.html")) +
    glob.glob(os.path.join(SCRATCH_DIR, "category", "*.html")) +
    glob.glob(os.path.join(SCRATCH_DIR, "author", "*.html"))
)

total_checked = 0
issues = []

print(f"==================================================")
print(f"2026 ADVANCED SEO & SCHEMA VERIFICATION AUDIT")
print(f"Auditing {len(all_html_files)} HTML files...")
print(f"==================================================\n")

HEALTH_SLUGS = [
    "skin-cancer-on-face-common-causes-home",
    "fatty-liver-disease-common-causes-home-remedies",
    "ast-blood-test-main-causes-diagnosis-recovery",
    "sinus-infection-symptoms-main-causes-diagnosis-recovery",
    "thrush-in-mouth-common-causes-home-remedies",
    "how-to-stop-snoring-what-do-common"
]

for fpath in all_html_files:
    if fpath.endswith("template_body.html"):
        continue
    rel_path = os.path.relpath(fpath, SCRATCH_DIR).replace("\\", "/")
    total_checked += 1
    
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    file_issues = []

    # 1. H1 Count
    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
    h1_count = len(h1_matches)
    if h1_count != 1:
        file_issues.append(f"H1 count != 1 (found {h1_count})")

    # 2. Meta Description
    meta_m = re.search(r'<meta name="description" content="(.*?)">', html, re.DOTALL | re.IGNORECASE)
    meta_desc = meta_m.group(1) if meta_m else ""
    meta_len = len(meta_desc)
    if not meta_desc:
        file_issues.append("Missing meta description")
    elif meta_len > 155:
        file_issues.append(f"Meta desc > 155 chars ({meta_len} chars)")

    # 3. Canonical Tag
    canon_m = re.search(r'<link rel="canonical" href="(.*?)">', html, re.DOTALL | re.IGNORECASE)
    canon_url = canon_m.group(1) if canon_m else ""
    if not canon_url:
        file_issues.append("Missing canonical tag")
    if ".html" in canon_url:
        file_issues.append(f"Canonical contains .html ({canon_url})")

    # 4. Robots Meta Tag (Google Discover)
    robots_m = re.search(r'<meta name="robots" content="(.*?)">', html, re.DOTALL | re.IGNORECASE)
    robots_content = robots_m.group(1) if robots_m else ""
    if "max-image-preview:large" not in robots_content:
        file_issues.append(f"Missing max-image-preview:large in robots meta: '{robots_content}'")

    # 5. JSON-LD Schema Validation
    schema_matches = re.findall(r'<script type="application/ld\+json"[^>]*>([\s\S]*?)</script>', html, re.IGNORECASE)
    if not schema_matches:
        file_issues.append("Missing JSON-LD structured data script")
    else:
        for idx, s_raw in enumerate(schema_matches):
            try:
                s_json = json.loads(s_raw.strip())
                # Check for NewsMediaOrganization (must not be present)
                raw_lower = s_raw.lower()
                if "newsmediaorganization" in raw_lower:
                    file_issues.append("Found forbidden NewsMediaOrganization schema")
                
                # Check article-specific schema requirements
                is_article = (
                    not rel_path.startswith("category/") and
                    not rel_path.startswith("author/") and
                    rel_path not in ["index.html", "about.html", "contact.html", "editorial-guidelines.html", "privacy-policy.html", "terms.html", "write-for-us.html"]
                )
                if is_article:
                    graph = s_json.get("@graph", [])
                    types = [item.get("@type") for item in graph if isinstance(item, dict)]
                    if "Article" not in types:
                        file_issues.append(f"Article page missing @type 'Article' in schema graph (types: {types})")
                    if "BreadcrumbList" not in types:
                        file_issues.append(f"Article page missing @type 'BreadcrumbList' in schema graph (types: {types})")

            except json.JSONDecodeError as jde:
                file_issues.append(f"Invalid JSON in structured data block #{idx+1}: {jde}")

    # 6. Table of Contents & Anchor integrity (for articles)
    is_article = (
        not rel_path.startswith("category/") and
        not rel_path.startswith("author/") and
        rel_path not in ["index.html", "about.html", "contact.html", "editorial-guidelines.html", "privacy-policy.html", "terms.html", "write-for-us.html"]
    )
    if is_article:
        if "gp-toc-container" not in html:
            file_issues.append("Missing Table of Contents (.gp-toc-container)")
        else:
            # Check jump links match anchors specifically inside TOC container
            toc_block_m = re.search(r'<nav class="gp-toc-container"[^>]*>([\s\S]*?)</nav>', html)
            if toc_block_m:
                toc_links = re.findall(r'<a href="#([^"]+)"', toc_block_m.group(1))
                h2_ids = re.findall(r'<h2[^>]*id="([^"]+)"', html)
                missing_anchors = [tl for tl in toc_links if tl not in h2_ids]
                if missing_anchors:
                    file_issues.append(f"TOC links missing matching h2 anchor IDs: {missing_anchors[:3]}")

        # Check scraper citation defense
        if "gp-source-citation" not in html:
            file_issues.append("Missing scraper defense citation (.gp-source-citation)")

    # 7. Health YMYL Medical Disclaimer Check
    is_health = any(h_slug in rel_path for h_slug in HEALTH_SLUGS)
    if is_health:
        if "gp-medical-disclaimer" not in html:
            file_issues.append("Health article missing Medical Disclaimer (.gp-medical-disclaimer)")
        if "CDC" not in html or "PubMed" not in html:
            file_issues.append("Health article missing clinical authority citations (CDC / PubMed)")

    if file_issues:
        issues.append((rel_path, file_issues))
        print(f"[FAIL] {rel_path}:")
        for iss in file_issues:
            print(f"       - {iss}")
    else:
        h1_text = re.sub(r'<[^>]+>', '', h1_matches[0]).strip() if h1_matches else ""
        h1_clean = h1_text.replace('\n', ' ').strip()
        print(f"[PASS] {rel_path:52} | H1 (1) | Desc: {meta_len:3}ch | Discover: OK | Schema: OK")

print(f"\n==================================================")
print(f"AUDIT SUMMARY: Checked {total_checked} files.")
if issues:
    print(f"RESULT: [FAIL] {len(issues)} files failed validation.")
else:
    print(f"RESULT: [PASS] 100% PERFECT PASS! All {total_checked} files meet the 2026 SEO framework.")
print(f"==================================================")
