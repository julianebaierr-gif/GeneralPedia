import os
import json

SCRATCH_DIR = r"C:\Users\Admin\.gemini\antigravity\scratch\generalpedia"
DB_PATH = os.path.join(SCRATCH_DIR, "data", "posts_database.json")

def rebuild_site():
    if not os.path.exists(DB_PATH):
        return
    with open(DB_PATH, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    # Sort newest first
    posts_data.sort(key=lambda x: x.get("published_at", "") or x.get("created_at", ""), reverse=True)
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
  <link rel="canonical" href="https://generalpedia.com">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://generalpedia.com">
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

    with open(r"C:\Users\Admin\.gemini\antigravity\brain\d1a13a74-d277-49d6-ac40-02b2abedbf3c\scratch\extracted_html_body.html", "r", encoding="utf-8") as f:
        body_part = f.read()

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

    os.makedirs(os.path.join(SCRATCH_DIR, "site"), exist_ok=True)
    with open(site_index_file, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Successfully rebuilt index.html with {len(posts_data)} posts.")

if __name__ == "__main__":
    rebuild_site()
