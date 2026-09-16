import os
import json

SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRATCH_DIR, "data", "posts_database.json")

def rebuild_site():
    if not os.path.exists(DB_PATH):
        return
    with open(DB_PATH, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    # In posts_database.json, newly published posts are always inserted at index 0 (newest first).
    # Safely escape any '</script' occurrences in the JSON string
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
  <link rel="canonical" href="https://generalpedia.com/">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://generalpedia.com/">
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
    "url": "https://generalpedia.com",
    "description": "Premier Digital Knowledge Magazine & Fact-Checked Encyclopedia",
    "potentialAction": {
      "@type": "SearchAction",
      "target": "https://generalpedia.com/?q={search_term_string}",
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

    # Update sitemap.xml
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
    except Exception:
        from datetime import datetime
        today_str = datetime.now().strftime("%Y-%m-%d")

    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <!-- Homepage -->',
        '  <url>',
        '    <loc>https://generalpedia.com/</loc>',
        f'    <lastmod>{today_str}</lastmod>',
        '    <changefreq>daily</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
        '  <!-- Categories -->',
        '  <url><loc>https://generalpedia.com/category/how-to</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://generalpedia.com/category/finance</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://generalpedia.com/category/health</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://generalpedia.com/category/tools</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://generalpedia.com/category/automotive</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://generalpedia.com/category/tech</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://generalpedia.com/category/lifestyle</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <url><loc>https://generalpedia.com/category/culture</loc><lastmod>' + today_str + '</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>',
        '  <!-- Articles -->'
    ]

    for p in posts_data:
        p_slug = p.get('slug') or p.get('id')
        p_date = (p.get('published_at') or today_str)[:10]
        if p_slug:
            sitemap_lines.append(f'  <url><loc>https://generalpedia.com/{p_slug}</loc><lastmod>{p_date}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>')

    sitemap_lines.append('</urlset>\n')
    sitemap_content = '\n'.join(sitemap_lines)

    sitemap_path = os.path.join(SCRATCH_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap_content)

    print(f"Successfully rebuilt index.html and sitemap.xml with {len(posts_data)} posts.")

if __name__ == "__main__":
    rebuild_site()
