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

    # Escape h1-h4 tags in JSON strings to prevent HTML scanners/crawlers from reading raw duplicate headings inside script blocks
    articles_json = json.dumps(posts_data, ensure_ascii=False).replace("</script", "<\\/script").replace("</Script", "<\\/Script")
    for h in ["h1", "h2", "h3", "h4"]:
        articles_json = articles_json.replace(f"<{h}", f"\\u003c{h}").replace(f"</{h}>", f"\\u003c/{h}\\u003e")

    with open(os.path.join(SCRATCH_DIR, "theme.css"), "r", encoding="utf-8") as f:
        theme_css = f.read()

    # Concise description: 147 characters (under 155 chars limit)
    head_part = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GeneralPedia | The Digital Knowledge Hub & Magazine</title>
  <meta name="description" content="GeneralPedia is a premier digital knowledge magazine delivering fact-checked guides, personal finance data, health insights, and expert tutorials.">
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

    with open(os.path.join(SCRATCH_DIR, "template_body.html"), "r", encoding="utf-8") as f:
        body_part = f.read()

    # Pre-render categories into HTML for homepage showcase
    cat_previews_html = []
    categories = [
        ("how-to", "How-To Guides"),
        ("finance", "Personal Finance"),
        ("health", "Health & Wellness"),
        ("tools", "Tools & Calculators"),
        ("automotive", "Automotive"),
        ("tech", "Tech & Software"),
        ("lifestyle", "Lifestyle & Home"),
        ("culture", "Culture & Society")
    ]
    for cat_slug, cat_name in categories:
        cat_posts = [p for p in posts_data if p.get("category_slug") == cat_slug]
        if not cat_posts:
            continue
        
        cards = []
        for p in cat_posts[:3]:
            img_url = p.get('featured_image', '')
            if not img_url and p.get('content_html'):
                m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', p.get('content_html'))
                if m:
                    img_url = m.group(1)
            
            img_tag = f'<div class="mag-card-thumb" style="background-image: url(\'{img_url}\');"></div>' if img_url else ''
            cards.append(f"""
              <a href="/{p['id']}" class="mag-card" onclick="handleCardClick(event, '{p['id']}')">
                {img_tag}
                <div class="mag-card-body">
                  <span class="category-badge">{cat_name}</span>
                  <div class="mag-card-title">{p['title']}</div>
                  <div class="mag-card-meta">
                    <span>{p.get('read_time', '5 min read')}</span>
                    <span>•</span>
                    <span>{p.get('display_date', 'Recent')}</span>
                  </div>
                </div>
              </a>
            """)
        
        cat_previews_html.append(f"""
          <section class="mag-category-showcase" style="margin-top: 48px;">
            <div class="mag-section-bar">
              <h2 class="mag-section-title">{cat_name}</h2>
              <a href="/category/{cat_slug}" onclick="handleNavClick(event, () => filterCategory('{cat_slug}'))" class="mag-section-more">View All ({len(cat_posts)}) →</a>
            </div>
            <div class="mag-feed-grid">
              {'\n'.join(cards)}
            </div>
          </section>
        """)

    with open(os.path.join(SCRATCH_DIR, "app.js"), "r", encoding="utf-8") as f:
        app_js = f.read()

    try:
        from static_pages_data import STATIC_PAGES
    except Exception as e:
        print(f"Error loading static pages: {e}")
        STATIC_PAGES = {}

    static_json = json.dumps(STATIC_PAGES, ensure_ascii=False)
    for h in ["h1", "h2", "h3", "h4"]:
        static_json = static_json.replace(f"<{h}", f"\\u003c{h}").replace(f"</{h}>", f"\\u003c/{h}\\u003e")

    # Template for subpages (removes STATIC_CATEGORIES_PLACEHOLDER completely)
    body_clean = body_part.replace("<!-- STATIC_CATEGORIES_PLACEHOLDER -->", "")
    page_base_html = f"""{head_part}
  <style>
{theme_css}
  </style>
{body_clean}
  <script>
    const ARTICLES_DATA = {articles_json};
    const STATIC_PAGES = {static_json};

{app_js}
  </script>
</body>
</html>
"""

    # Template for Homepage
    home_body = body_part.replace("<!-- STATIC_CATEGORIES_PLACEHOLDER -->", "\n".join(cat_previews_html))
    home_full_html = f"""{head_part}
  <style>
{theme_css}
  </style>
{home_body}
  <script>
    const ARTICLES_DATA = {articles_json};
    const STATIC_PAGES = {static_json};

{app_js}
  </script>
</body>
</html>
"""

    # For Homepage (index.html), wrap the site logo in <h1> so homepage has exactly 1 H1
    home_logo_search = '<a href="/" onclick="handleNavClick(event, () => showHomeView())" class="site-logo" aria-label="GeneralPedia Magazine Home">'
    home_logo_replace = '<h1 class="site-logo" style="display:inline-flex;margin:0;padding:0;font-size:inherit;line-height:inherit;"><a href="/" onclick="handleNavClick(event, () => showHomeView())" class="site-logo" aria-label="GeneralPedia Magazine Home">'
    
    home_logo_end_search = '</div>\n        </a>'
    home_logo_end_replace = '</div>\n        </a></h1>'

    index_html = home_full_html.replace(home_logo_search, home_logo_replace, 1).replace(home_logo_end_search, home_logo_end_replace, 1).replace('<div class="mag-section-title" id="mag-feed-heading">Latest Published Reports</div>', '<h2 class="mag-section-title" id="mag-feed-heading">Latest Published Reports</h2>', 1)

    index_file = os.path.join(SCRATCH_DIR, "index.html")
    site_index_file = os.path.join(SCRATCH_DIR, "site", "index.html")

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_html)

    if os.path.exists(os.path.dirname(site_index_file)):
        with open(site_index_file, "w", encoding="utf-8") as f:
            f.write(index_html)

    def write_prerendered_page(rel_path, page_title, page_desc, page_url, page_type="article", extra_data=None):
        escaped_title = page_title.replace('&', '&amp;')
        escaped_desc = page_desc.replace('"', '&quot;').replace('&', '&amp;')
        
        page_html = page_base_html
        page_html = re.sub(r'<title>.*?</title>', f'<title>{escaped_title}</title>', page_html, count=1)
        page_html = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{escaped_desc}">', page_html, count=1)
        page_html = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{page_url}">', page_html, count=1)
        page_html = re.sub(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="{page_url}">', page_html, count=1)
        page_html = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{escaped_title}">', page_html, count=1)
        page_html = re.sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{escaped_desc}">', page_html, count=1)

        # Enforce exactly 1 H1 per page:
        if page_type == "article":
            p_data = extra_data or {}
            clean_art_title = escaped_title.split(" | ")[0]
            # Convert article title div to h1
            page_html = page_html.replace(
                '<div id="art-title" class="art-title-text">Article Title</div>',
                f'<h1 id="art-title" class="art-title-text">{clean_art_title}</h1>',
                1
            )
            # Make article-view visible and home-view hidden
            page_html = page_html.replace('<div id="article-view" class="hidden">', '<div id="article-view">', 1)
            page_html = page_html.replace('<div id="home-view">', '<div id="home-view" class="hidden">', 1)
            # Pre-render content
            page_html = page_html.replace('<!-- Article HTML inserted here -->', p_data.get('content_html', ''), 1)
            page_html = page_html.replace('<p id="art-meta" class="art-excerpt-lead">Article Excerpt</p>', f'<p id="art-meta" class="art-excerpt-lead">{p_data.get("meta_description", "")}</p>', 1)
            page_html = page_html.replace('<span id="art-category-badge" class="category-badge">Category</span>', f'<span id="art-category-badge" class="category-badge">{p_data.get("category_name", "Knowledge Guide")}</span>', 1)

        elif page_type == "category":
            cat_info = extra_data or {}
            cat_slug = cat_info.get('slug', '')
            cat_display_name = escaped_title.split(" | ")[0]
            # Convert category title to H1
            page_html = page_html.replace(
                '<div class="category-header-title" id="category-banner-title">Category Title</div>',
                f'<h1 class="category-header-title" id="category-banner-title">{cat_display_name}</h1>',
                1
            )
            # Update feed heading to H2 for category page (Hierarchy: H1 banner -> H2 feed title)
            page_html = page_html.replace(
                '<div class="mag-section-title" id="mag-feed-heading">Latest Published Reports</div>',
                f'<h2 class="mag-section-title" id="mag-feed-heading">{cat_display_name} Published Guides</h2>',
                1
            )
            # Show category banner, hide hero & trending
            page_html = page_html.replace('<section id="category-header-banner" class="category-header-banner hidden"', '<section id="category-header-banner" class="category-header-banner"', 1)
            page_html = page_html.replace('<section class="magazine-hero-section" id="home-hero-section"', '<section class="magazine-hero-section hidden" id="home-hero-section"', 1)
            page_html = page_html.replace('<section class="trending-banner-row" id="home-trending-section"', '<section class="trending-banner-row hidden" id="home-trending-section"', 1)
            page_html = page_html.replace('<p class="category-header-desc" id="category-banner-desc">Curated editorial manuals, in-depth breakdowns, and interactive references.</p>', f'<p class="category-header-desc" id="category-banner-desc">{escaped_desc}</p>', 1)
            page_html = page_html.replace('<span id="category-crumb-current" style="font-weight: 700; color: var(--text-main);">Calculators</span>', f'<span id="category-crumb-current" style="font-weight: 700; color: var(--text-main);">{cat_display_name}</span>', 1)

            # Pre-render category cards:
            cat_posts = [p for p in posts_data if p.get("category_slug") == cat_slug]
            cat_cards = []
            for p in cat_posts:
                img = p.get('featured_image', '')
                img_tag = f'<div class="mag-card-thumb"><img src="{img}" alt="{p["title"]}" width="600" height="338" loading="lazy"></div>' if img else ''
                cat_cards.append(f'''
                  <a href="/{p["id"]}" class="mag-article-card">
                    {img_tag}
                    <div class="mag-card-body">
                      <div class="mag-card-title">{p["title"]}</div>
                      <p class="mag-card-excerpt">{p.get("meta_description","")}</p>
                    </div>
                  </a>
                ''')
            cat_cards_html = '\n'.join(cat_cards)
            page_html = page_html.replace('<div class="mag-feed-grid" id="articles-feed">\n            <!-- Populated via JS -->\n          </div>', f'<div class="mag-feed-grid" id="articles-feed">{cat_cards_html}</div>', 1)

        elif page_type == "static":
            sp_data = extra_data or {}
            sp_content = sp_data.get('content', '')
            # Convert first h2 of sp_content (page headline) into h1
            sp_content = re.sub(r'<h2([^>]*)>(.*?)</h2>', r'<h1\1>\2</h1>', sp_content, count=1, flags=re.DOTALL)
            # Inject into static-content container
            page_html = page_html.replace('<!-- Static page HTML populated here -->', sp_content, 1)
            # Update breadcrumb
            clean_title = sp_data.get('title', '').replace('&', '&amp;')
            page_html = page_html.replace(
                '<li id="static-crumb" aria-current="page" style="color: var(--text-main); font-weight: 600;">Information Page</li>',
                f'<li id="static-crumb" aria-current="page" style="color: var(--text-main); font-weight: 600;">{clean_title}</li>',
                1
            )
            # Make static-view visible and home-view hidden for crawlers:
            page_html = page_html.replace('<div id="static-view" class="hidden">', '<div id="static-view">', 1)
            page_html = page_html.replace('<div id="home-view">', '<div id="home-view" class="hidden">', 1)

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
            write_prerendered_page(f"{slug}.html", p_title, p_desc, p_url, page_type="article", extra_data=p)

    # 2. Prerender static pages
    for sp_slug, sp_data in STATIC_PAGES.items():
        clean_title = sp_data.get('title', '').replace('&', '&amp;')
        sp_title = f"{clean_title} | GeneralPedia"
        sp_desc = sp_data.get('description', '')
        sp_url = f"https://www.generalpedia.com/{sp_slug}"
        write_prerendered_page(f"{sp_slug}.html", sp_title, sp_desc, sp_url, page_type="static", extra_data=sp_data)

    # 3. Prerender categories
    categories_full = [
        ("how-to", "How-To & Practical Guides"),
        ("finance", "Personal Finance & Tax Analysis"),
        ("health", "Health, Medicine & Wellness Insights"),
        ("tools", "Calculators & Interactive Reference"),
        ("automotive", "Automotive Reviews & Diagnostics"),
        ("tech", "Technology & Digital Tools"),
        ("lifestyle", "Home, Pet Care & Living"),
        ("culture", "Culture, Sports & Entertainment")
    ]
    for cat_slug, cat_name in categories_full:
        cat_title = f"{cat_name} | GeneralPedia"
        cat_desc = f"Explore curated, research-backed guides, articles, and analyses in {cat_name} on GeneralPedia."
        cat_url = f"https://www.generalpedia.com/category/{cat_slug}"
        write_prerendered_page(os.path.join("category", f"{cat_slug}.html"), cat_title, cat_desc, cat_url, page_type="category", extra_data={"slug": cat_slug, "name": cat_name})

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

    sitemap_lines.append('</urlset>\n')
    sitemap_content = '\n'.join(sitemap_lines)

    sitemap_path = os.path.join(SCRATCH_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap_content)

    print(f"Successfully rebuilt index.html, sitemap.xml, and static pages with {len(posts_data)} posts.")

if __name__ == "__main__":
    rebuild_site()
