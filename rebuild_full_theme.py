import os
import json
import re
from datetime import datetime

SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRATCH_DIR, "data", "posts_database.json")

def rebuild_site():
    if not os.path.exists(DB_PATH):
        return
    with open(DB_PATH, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    articles_json = json.dumps(posts_data, ensure_ascii=False).replace("</script", "<\\/script").replace("</Script", "<\\/Script")

    with open(os.path.join(SCRATCH_DIR, "theme.css"), "r", encoding="utf-8") as f:
        theme_css = f.read()

    head_part = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GeneralPedia | The Digital Knowledge Hub & Magazine</title>
  <meta name="description" content="GeneralPedia is a premier digital news, encyclopedia, and magazine publication delivering verified guides, personal finance, health insights, and expert tutorials.">
  <meta name="keywords" content="generalpedia, knowledge hub, encyclopedia, digital magazine, personal finance, tutorials, tax guides, automotive reviews">
  <meta name="author" content="GeneralPedia Editorial Board">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://www.generalpedia.com/">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://www.generalpedia.com/">
  <meta property="og:title" content="GeneralPedia | Digital Knowledge Magazine">
  <meta property="og:description" content="Research-backed articles, trending news, and tools across finance, health, tech, automotive, and everyday living.">
  <meta property="og:site_name" content="GeneralPedia">

  <!-- Twitter / X -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="GeneralPedia | Digital Knowledge Magazine">
  <meta name="twitter:description" content="Research-backed articles, trending news, and tools across finance, health, tech, automotive, and everyday living.">

  <!-- Favicon / Brand Icon -->
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' rx='8' fill='%230f172a'/%3E%3Cpath d='M10 26V14h9.5c3.5 0 6 2 6 5.5s-2.5 5.5-6 5.5H15v-5h4.2c1.2 0 2-.6 2-1.8 0-1.1-.8-1.7-2-1.7h-5.2v9H10z' fill='%23ffffff'/%3E%3Cpath d='M25 14h5v12h-5z' fill='%23e63946'/%3E%3C/svg%3E">

  <!-- Structured Data (JSON-LD) -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "NewsMediaOrganization",
    "name": "GeneralPedia",
    "alternateName": "GeneralPedia.com",
    "url": "https://www.generalpedia.com",
    "description": "Premier Digital Knowledge Magazine & Fact-Checked Encyclopedia",
    "potentialAction": {
      "@type": "SearchAction",
      "target": "https://www.generalpedia.com/?q={search_term_string}",
      "query-input": "required name=search_term_string"
    }
  }
  </script>
"""

    body_template_path = os.path.join(SCRATCH_DIR, "template_body.html")
    if os.path.exists(body_template_path):
        with open(body_template_path, "r", encoding="utf-8") as f:
            body_part = f.read()
    else:
        body_part = "<body><div id='app'></div>"

    old_hero_markup = """        <div class="hero-grid">
          <!-- Main Hero Story -->
          <div class="hero-main-card" id="hero-feature-1" onclick="openArticle('queen-of-wands')">
            <div class="hero-card-content">
              <span class="category-badge">Featured Analysis</span>
              <h2 class="hero-main-title">Queen of Wands: Comprehensive Archetype Meaning, Career &amp; Relationships</h2>
              <div class="hero-meta">
                <span>By Editorial Staff</span>
                <span>•</span>
                <span>September 13, 2026</span>
                <span>•</span>
                <span>6 min read</span>
              </div>
            </div>
          </div>

          <!-- Secondary Hero Tile 1 -->
          <div class="hero-sub-card" id="hero-feature-2" onclick="openArticle('2025-toyota-camry')">
            <div class="hero-card-content">
              <span class="category-badge blue">Automotive</span>
              <h3 class="hero-sub-title">2025 Toyota Camry: Complete Specs, Hybrid Performance &amp; Resale Review</h3>
              <div class="hero-meta">
                <span>Automotive Desk</span>
                <span>•</span>
                <span>5 min read</span>
              </div>
            </div>
          </div>

          <!-- Secondary Hero Tile 2 -->
          <div class="hero-sub-card" id="hero-feature-3" onclick="openArticle('back-pain-when-bending-over')">
            <div class="hero-card-content">
              <span class="category-badge green">Health &amp; Medicine</span>
              <h3 class="hero-sub-title">Lower Back Pain When Bending Over: Clinical Causes, Ergonomics &amp; Relief</h3>
              <div class="hero-meta">
                <span>Health Desk</span>
                <span>•</span>
                <span>7 min read</span>
              </div>
            </div>
          </div>
        </div>"""

    new_hero_markup = """        <div class="hero-grid" id="hero-grid-container">
        </div>"""

    body_part = body_part.replace(old_hero_markup, new_hero_markup)

    with open(os.path.join(SCRATCH_DIR, "app.js"), "r", encoding="utf-8") as f:
        app_js = f.read()

    try:
        from static_pages_data import STATIC_PAGES
    except Exception as e:
        print(f"Error loading static pages: {e}")
        STATIC_PAGES = {}
    static_json = json.dumps(STATIC_PAGES, ensure_ascii=False)

    full_html = f"""{head_part}
  <style>
{theme_css}
  </style>
{body_part}
  <script>
    const ARTICLES_DATA = {articles_json};
    const STATIC_PAGES = {static_json};

{app_js}
  </script>
</body>
</html>
"""

    index_file = os.path.join(SCRATCH_DIR, "index.html")
    site_index_file = os.path.join(SCRATCH_DIR, "site", "index.html")

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(full_html)

    if os.path.exists(os.path.dirname(site_index_file)):
        with open(site_index_file, "w", encoding="utf-8") as f:
            f.write(full_html)

    def write_prerendered_page(rel_path, page_title, page_desc, page_url):
        escaped_title = page_title.replace('&', '&amp;')
        escaped_desc = page_desc.replace('"', '&quot;').replace('&', '&amp;')
        
        page_html = full_html
        page_html = re.sub(r'<title>.*?</title>', f'<title>{escaped_title}</title>', page_html, count=1)
        page_html = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{escaped_desc}">', page_html, count=1)
        page_html = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{page_url}">', page_html, count=1)
        page_html = re.sub(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="{page_url}">', page_html, count=1)
        page_html = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{escaped_title}">', page_html, count=1)
        page_html = re.sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{escaped_desc}">', page_html, count=1)

        target_file = os.path.join(SCRATCH_DIR, rel_path)
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as pf:
            pf.write(page_html)

    # 1. Prerender each article
    for p in posts_data:
        slug = p.get('slug') or p.get('id')
        if slug:
            p_title = f"{p.get('title', 'GeneralPedia')} | GeneralPedia"
            p_desc = p.get('meta_description', '')
            p_url = f"https://www.generalpedia.com/{slug}"
            write_prerendered_page(f"{slug}.html", p_title, p_desc, p_url)

    # 2. Prerender static pages
    for sp_slug, sp_data in STATIC_PAGES.items():
        clean_title = sp_data.get('title', '').replace('&amp;', '&')
        sp_title = f"{clean_title} | GeneralPedia"
        sp_desc = sp_data.get('description', '')
        sp_url = f"https://www.generalpedia.com/{sp_slug}"
        write_prerendered_page(f"{sp_slug}.html", sp_title, sp_desc, sp_url)

    # 3. Prerender categories
    categories = [
        ("how-to", "How-To & Practical Guides"),
        ("finance", "Personal Finance & Tax Analysis"),
        ("health", "Health, Medicine & Wellness Insights"),
        ("tools", "Calculators & Interactive Reference"),
        ("automotive", "Automotive Reviews & Diagnostics"),
        ("tech", "Technology & Digital Tools"),
        ("lifestyle", "Home, Pet Care & Living"),
        ("culture", "Culture, Sports & Entertainment")
    ]
    for cat_slug, cat_name in categories:
        cat_title = f"{cat_name} | GeneralPedia"
        cat_desc = f"Explore curated, research-backed guides, articles, and analyses in {cat_name} on GeneralPedia."
        cat_url = f"https://www.generalpedia.com/category/{cat_slug}"
        write_prerendered_page(os.path.join("category", f"{cat_slug}.html"), cat_title, cat_desc, cat_url)

    # Update sitemap.xml
    today_str = datetime.now().strftime("%Y-%m-%d")

    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <!-- Homepage -->',
        '  <url>',
        '    <loc>https://www.generalpedia.com/</loc>',
        f'    <lastmod>{today_str}</lastmod>',
        '    <changefreq>daily</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
        '  <!-- Categories -->',
        '  <url><loc>https://www.generalpedia.com/category/how-to</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://www.generalpedia.com/category/finance</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://www.generalpedia.com/category/health</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://www.generalpedia.com/category/tools</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://www.generalpedia.com/category/automotive</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://www.generalpedia.com/category/tech</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://www.generalpedia.com/category/lifestyle</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://www.generalpedia.com/category/culture</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <!-- Static Pages -->',
        '  <url><loc>https://www.generalpedia.com/about</loc><lastmod>' + today_str + '</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>',
        '  <url><loc>https://www.generalpedia.com/write-for-us</loc><lastmod>' + today_str + '</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>',
        '  <url><loc>https://www.generalpedia.com/editorial-guidelines</loc><lastmod>' + today_str + '</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>',
        '  <url><loc>https://www.generalpedia.com/privacy-policy</loc><lastmod>' + today_str + '</lastmod><changefreq>monthly</changefreq><priority>0.5</priority></url>',
        '  <url><loc>https://www.generalpedia.com/terms</loc><lastmod>' + today_str + '</lastmod><changefreq>monthly</changefreq><priority>0.5</priority></url>',
        '  <url><loc>https://www.generalpedia.com/contact</loc><lastmod>' + today_str + '</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>',
        '  <!-- Articles -->'
    ]

    for p in posts_data:
        p_slug = p.get('slug') or p.get('id')
        p_date = (p.get('published_at') or today_str)[:10]
        if p_slug:
            sitemap_lines.append(f'  <url><loc>https://www.generalpedia.com/{p_slug}</loc><lastmod>{p_date}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>')

    sitemap_lines.append('</urlset>\\n')
    sitemap_content = '\\n'.join(sitemap_lines)

    sitemap_path = os.path.join(SCRATCH_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap_content)

    print(f"Successfully rebuilt index.html, sitemap.xml, and static pages with {len(posts_data)} posts.")

if __name__ == "__main__":
    rebuild_site()
