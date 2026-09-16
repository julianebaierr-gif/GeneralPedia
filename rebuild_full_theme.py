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

    # Create minimal articles metadata for client-side search/feeds
    feed_keys = ['id', 'slug', 'title', 'category_slug', 'category_name', 'featured_image', 'display_date', 'read_time', 'meta_description', 'author_name', 'primary_keyword']
    light_posts = [{k: p.get(k, '') for k in feed_keys} for p in posts_data]

    articles_json = json.dumps(light_posts, ensure_ascii=False).replace("</script", "<\\/script").replace("</Script", "<\\/Script")
    for h in ["h1", "h2", "h3", "h4"]:
        articles_json = articles_json.replace(f"<{h}", f"\\u003c{h}").replace(f"</{h}>", f"\\u003c/{h}\\u003e")

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
    }
  }
  </script>
  <!-- External Stylesheet -->
  <link rel="stylesheet" href="/theme.css">
</head>
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

    site_data_content = f"const ARTICLES_DATA = {articles_json};\nconst STATIC_PAGES = {static_json};\n"
    with open(os.path.join(SCRATCH_DIR, "site_data.js"), "w", encoding="utf-8") as f:
        f.write(site_data_content)
    site_dir = os.path.join(SCRATCH_DIR, "site")
    if os.path.exists(site_dir):
        with open(os.path.join(site_dir, "site_data.js"), "w", encoding="utf-8") as f:
            f.write(site_data_content)

    # Build pre-rendered popular guides (top 5) for sidebar
    top5_posts = posts_data[:5]
    popular_cards = []
    for idx, art in enumerate(top5_posts):
        popular_cards.append(f'''
              <a href="/{art['id']}" class="popular-item">
                <div class="popular-num">0{idx + 1}</div>
                <div class="popular-content">
                  <div class="popular-title">{art['title']}</div>
                  <span>{art.get('display_date', 'Recent')} • {art.get('category_name', 'Guide')}</span>
                </div>
              </a>''')
    static_popular_html = '\n'.join(popular_cards)

    # Build pre-rendered category taxonomy with counts for sidebar
    cat_tax_configs = [
        {"slug": "how-to", "name": "How-To & Tutorials"},
        {"slug": "finance", "name": "Finance & Tax"},
        {"slug": "health", "name": "Health & Wellness"},
        {"slug": "tools", "name": "Calculators & Tools"},
        {"slug": "automotive", "name": "Automotive"},
        {"slug": "lifestyle", "name": "Lifestyle & Living"},
        {"slug": "culture", "name": "Culture & Society"}
    ]
    counts = {}
    for art in posts_data:
        c_slug = art.get("category_slug", "")
        counts[c_slug] = counts.get(c_slug, 0) + 1

    cat_tax_cards = []
    for cat in cat_tax_configs:
        cnt = counts.get(cat["slug"], 0)
        cat_tax_cards.append(f'''
              <li>
                <a href="/category/{cat['slug']}" class="cat-tax-item" style="text-decoration:none; display:flex; justify-content:space-between; align-items:center; color:inherit;">
                  <span>{cat['name']}</span>
                  <span class="cat-count">{cnt}</span>
                </a>
              </li>''')
    static_cat_tax_html = '\n'.join(cat_tax_cards)

    # Pre-render sidebar popular and taxonomy into body_part for all pages
    body_part = body_part.replace(
        '<div class="popular-list" id="popular-posts-list">\n              <!-- Populated via JS -->\n            </div>',
        f'<div class="popular-list" id="popular-posts-list">{static_popular_html}\n            </div>',
        1
    )
    body_part = body_part.replace(
        '<ul class="cat-tax-list" id="cat-tax-list">\n              <!-- Dynamically populated via JS with real-time article counts -->\n            </ul>',
        f'<ul class="cat-tax-list" id="cat-tax-list">{static_cat_tax_html}\n            </ul>',
        1
    )

    # Template for subpages (removes STATIC_CATEGORIES_PLACEHOLDER completely)
    body_clean = body_part.replace("<!-- STATIC_CATEGORIES_PLACEHOLDER -->", "")
    page_base_html = f"""{head_part}
{body_clean}
  <script src="/site_data.js" defer></script>
  <script src="/app.js" defer></script>
</body>
</html>
"""

    # Pre-render Homepage feed (first 13 articles after hero)
    home_feed_cards = []
    for p in posts_data:
        img_url = p.get('featured_image', '')
        img_tag = f'<div class="mag-card-thumb"><img src="{img_url}" alt="{p["title"]}" width="600" height="338" loading="lazy"></div>' if img_url else ''
        home_feed_cards.append(f'''
            <a href="/{p["id"]}" class="mag-article-card">
              {img_tag}
              <div class="mag-card-body">
                <div class="mag-card-title">{p["title"]}</div>
                <p class="mag-card-excerpt">{p.get("meta_description","")}</p>
              </div>
            </a>''')
    home_feed_html = '\n'.join(home_feed_cards)

    # Pre-render Homepage Hero Grid (p1, p2, p3)
    p1 = posts_data[0]
    p2 = posts_data[1] if len(posts_data) > 1 else p1
    p3 = posts_data[2] if len(posts_data) > 2 else p1
    hero_grid_html = f'''
          <a href="/{p1['id']}" class="hero-main-card" style="background-image: url('{p1.get('featured_image','')}');">
            <div class="hero-card-content">
              <span class="category-badge">{p1.get('category_name','Featured')}</span>
              <div class="hero-main-title">{p1['title']}</div>
              <div class="hero-meta">
                <span>By {p1.get('author_name','Editorial Staff')}</span> • <span>{p1.get('display_date','Recent')}</span> • <span>{p1.get('read_time','6 min read')}</span>
              </div>
            </div>
          </a>
          <a href="/{p2['id']}" class="hero-sub-card" style="background-image: url('{p2.get('featured_image','')}');">
            <div class="hero-card-content">
              <span class="category-badge blue">{p2.get('category_name','Guide')}</span>
              <div class="hero-sub-title">{p2['title']}</div>
              <div class="hero-meta">
                <span>{p2.get('display_date','Recent')}</span> • <span>{p2.get('read_time','5 min')}</span>
              </div>
            </div>
          </a>
          <a href="/{p3['id']}" class="hero-sub-card" style="background-image: url('{p3.get('featured_image','')}');">
            <div class="hero-card-content">
              <span class="category-badge green">{p3.get('category_name','Analysis')}</span>
              <div class="hero-sub-title">{p3['title']}</div>
              <div class="hero-meta">
                <span>{p3.get('display_date','Recent')}</span> • <span>{p3.get('read_time','5 min')}</span>
              </div>
            </div>
          </a>
    '''

    # Template for Homepage
    home_body = body_part.replace("<!-- STATIC_CATEGORIES_PLACEHOLDER -->", "\n".join(cat_previews_html))
    home_body = home_body.replace('<div class="hero-grid" id="hero-grid-container">\n        </div>', f'<div class="hero-grid" id="hero-grid-container">{hero_grid_html}\n        </div>')
    home_body = home_body.replace('<div class="mag-feed-grid" id="articles-feed">\n            <!-- Populated via JS -->\n          </div>', f'<div class="mag-feed-grid" id="articles-feed">{home_feed_html}\n          </div>')

    home_full_html = f"""{head_part}
{home_body}
  <script src="/site_data.js" defer></script>
  <script src="/app.js" defer></script>
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

    category_editorial_overviews = {
        "how-to": "Our How-To and Tutorials library delivers step-by-step instructions, proven DIY solutions, and comprehensive troubleshooting protocols. Whether tackling household repairs, mastering software configurations, or following technical procedures, every manual is systematically reviewed to ensure actionable accuracy, clear safety warnings, and reliable results for beginners and advanced practitioners alike. Browse our complete catalog of practical procedures, maintenance checkpoints, and instructional manuals below. Each guide features verified equipment checklists, timing estimates, common pitfalls to avoid, and systematic diagnosis charts to streamline your project.",
        "finance": "GeneralPedia Personal Finance & Tax Analysis hub provides clear breakdowns of tax brackets, insurance regulations, investment strategies, and retirement planning rules. Explore fact-checked financial analyses, deadline schedules, and actionable money management principles designed to help individuals and families make informed, prudent economic decisions. Review our latest financial guides, policy updates, and fiscal breakdowns below. Our contributors analyze IRS regulations, statutory contribution caps, inflation adjustments, and tax-saving structures to keep you compliant and financially secure.",
        "health": "The Health, Medicine & Wellness section offers evidence-based medical summaries, symptom breakdowns, preventative care overviews, and nutritional guidelines. All guides are compiled from peer-reviewed clinical research and health authority standards, empowering readers with clear insights to better understand medical conditions and wellness choices. Explore our latest clinical summaries, health advisories, and medical reviews below. Consult verified timelines for symptom progression, home management protocols, and criteria for professional medical evaluation.",
        "tools": "Explore our collection of interactive calculation tools, reference charts, area code directories, and conversion formulas. Built for fast, reliable lookup, each tool simplifies numerical computations, geographic verifications, and technical data analysis for everyday productivity and project planning. Access our full suite of lookup tables, calculators, and verified references below. Features include comprehensive telecommunications routing maps, regional telecommunication histories, and practical calculation templates.",
        "automotive": "Our Automotive hub offers in-depth vehicle reviews, mechanical diagnostic guides, maintenance schedules, and practical used car purchasing advice. From performance specifications and fuel economy analyses to troubleshooting engine trouble codes, our automotive manuals equip drivers with dependable knowledge to care for their vehicles. Consult our vehicle reviews, diagnostic playbooks, and inspection guides below. Discover road-tested trim comparisons, long-term ownership expense forecasts, and mechanic-certified pre-purchase checklists.",
        "tech": "The Technology and Digital Tools category covers software tutorials, system optimization techniques, consumer electronics comparisons, and emerging digital developments. Learn how to configure applications, enhance personal privacy, and navigate digital tools effectively with clear, jargon-free technical manuals. Examine our comprehensive software overviews, device benchmarks, and technical guides below. Stay informed with actionable cybersecurity best practices, operating system configuration steps, and digital productivity workflows.",
        "lifestyle": "The Home, Pet Care & Living archive delivers vetted home maintenance strategies, pet nutrition guides, indoor air quality practices, and sustainable lifestyle tips. Discover practical advice for everyday living, home safety precautions, and conscientious pet care rooted in expert recommendations and proven household methods. Explore our home management articles, care instructions, and lifestyle guides below. Access seasonal preventative maintenance checklists, veterinarian-reviewed dietary precautions, and energy efficiency upgrades.",
        "culture": "Our Culture, Sports & Entertainment repository chronicles historical milestones, international sporting traditions, holiday backgrounds, and societal events. Explore rich historical contexts, archival retrospectives, and cultural celebrations with verified timelines and engaging editorial perspectives. Delve into our cultural chronicles, holiday histories, and athletic retrospectives below. Learn the origins, statutory recognitions, and cultural significance behind prominent global commemorations and competitive athletic leagues."
    }

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
            clean_art_title = (p_data.get('title') or escaped_title.split(" | ")[0]).replace('&', '&amp;')
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

            # Insert Category Editorial Overview Box
            cat_overview = category_editorial_overviews.get(cat_slug, "")
            overview_html = f'''
        <div class="category-editorial-scope" style="margin-top: 18px; font-size: 0.95rem; line-height: 1.65; color: var(--text-muted); background: var(--bg-card); padding: 18px 22px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
          <p style="margin:0;">{cat_overview}</p>
        </div>'''
            page_html = page_html.replace('<!-- 6. 2-COLUMN MAGAZINE CONTENT + SIDEBAR -->', f'{overview_html}\n      <!-- 6. 2-COLUMN MAGAZINE CONTENT + SIDEBAR -->', 1)

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
            raw_title = p.get('title', 'GeneralPedia').strip()
            # Always add brand suffix so <title> never duplicates <h1>
            # Try progressively shorter suffixes to stay ≤60 chars
            with_brand = f"{raw_title} | GeneralPedia"
            with_brand_dash = f"{raw_title} - GeneralPedia"
            with_brand_short = f"{raw_title} | GP"
            if len(with_brand.replace('&', '&amp;')) <= 60:
                p_title = with_brand
            elif len(with_brand_short.replace('&', '&amp;')) <= 60:
                p_title = with_brand_short
            else:
                prefix = re.split(r'[:\-–—]', raw_title)[0].strip()
                cand = f"{prefix} | GeneralPedia"
                if len(cand.replace('&', '&amp;')) <= 60:
                    p_title = cand
                else:
                    p_title = f"{prefix[:53]} | GP"
            
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
