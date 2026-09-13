
    function renderHeroGrid() {
      const heroContainer = document.getElementById('hero-grid-container');
      if (!heroContainer || typeof ARTICLES_DATA === 'undefined' || ARTICLES_DATA.length === 0) return;
      const p1 = ARTICLES_DATA[0];
      const p2 = ARTICLES_DATA[1] || p1;
      const p3 = ARTICLES_DATA[2] || p1;

      function getImg(art) {
        if (!art || !art.content_html) return '';
        const m = art.content_html.match(/<img[^>]+src=["']([^"']+)["']/);
        return m ? m[1] : '';
      }

      heroContainer.innerHTML = `
        <div class="hero-main-card" onclick="openArticle('${p1.id}')" style="${getImg(p1) ? `background-image: linear-gradient(to top, rgba(15,23,42,0.95) 0%, rgba(15,23,42,0.4) 60%, rgba(15,23,42,0.2) 100%), url('${getImg(p1)}');` : ''}">
          <div class="hero-card-content">
            <span class="category-badge">${escapeHtml(p1.category_name || 'Featured')}</span>
            <h2 class="hero-main-title">${escapeHtml(p1.title)}</h2>
            <div class="hero-meta">
              <span>By Editorial Staff</span><span>•</span>
              <span>${p1.display_date || 'Recent'}</span><span>•</span>
              <span>${p1.read_time || '6 min read'}</span>
            </div>
          </div>
        </div>
        <div class="hero-sub-card" onclick="openArticle('${p2.id}')" style="${getImg(p2) ? `background-image: linear-gradient(to top, rgba(15,23,42,0.95) 0%, rgba(15,23,42,0.4) 60%, rgba(15,23,42,0.2) 100%), url('${getImg(p2)}');` : ''}">
          <div class="hero-card-content">
            <span class="category-badge blue">${escapeHtml(p2.category_name || 'Guide')}</span>
            <h3 class="hero-sub-title">${escapeHtml(p2.title)}</h3>
            <div class="hero-meta"><span>${p2.display_date || 'Recent'}</span><span>•</span><span>${p2.read_time || '5 min'}</span></div>
          </div>
        </div>
        <div class="hero-sub-card" onclick="openArticle('${p3.id}')" style="${getImg(p3) ? `background-image: linear-gradient(to top, rgba(15,23,42,0.95) 0%, rgba(15,23,42,0.4) 60%, rgba(15,23,42,0.2) 100%), url('${getImg(p3)}');` : ''}">
          <div class="hero-card-content">
            <span class="category-badge green">${escapeHtml(p3.category_name || 'Analysis')}</span>
            <h3 class="hero-sub-title">${escapeHtml(p3.title)}</h3>
            <div class="hero-meta"><span>${p3.display_date || 'Recent'}</span><span>•</span><span>${p3.read_time || '5 min'}</span></div>
          </div>
        </div>
      `;
    }

    let currentCategorySlug = 'all';

    // Views
    const homeView = document.getElementById('home-view');
    const articleView = document.getElementById('article-view');
    const staticView = document.getElementById('static-view');
    const searchView = document.getElementById('search-view');
    const articlesFeed = document.getElementById('articles-feed');
    const trendingMiniContainer = document.getElementById('trending-mini-container');
    const popularPostsList = document.getElementById('popular-posts-list');

    const homeHeroSection = document.getElementById('home-hero-section');
    const homeTrendingSection = document.getElementById('home-trending-section');

    const categoryHeaderBanner = document.getElementById('category-header-banner');

    function hideAllViews() {
      homeView.classList.add('hidden');
      articleView.classList.add('hidden');
      staticView.classList.add('hidden');
      searchView.classList.add('hidden');
    }

    function updateSeoMetadata(title, description, path) {
      document.title = title;
      const metaDesc = document.querySelector('meta[name="description"]');
      if (metaDesc && description) metaDesc.setAttribute('content', description);
      const canonical = document.querySelector('link[rel="canonical"]');
      if (canonical) {
        const cleanPath = path ? (path.startsWith('/') ? path : '/' + path) : '/';
        canonical.setAttribute('href', `https://general-pedia.vercel.app${cleanPath}`);
      }
    }

    function showHomeView(push = true) {
      renderHeroGrid();
      hideAllViews();
      homeView.classList.remove('hidden');
      if (homeHeroSection) homeHeroSection.classList.remove('hidden');
      if (homeTrendingSection) homeTrendingSection.classList.remove('hidden');
      if (categoryHeaderBanner) categoryHeaderBanner.classList.add('hidden');
      currentCategorySlug = 'all';
      updateNavHighlight('all');
      document.getElementById('mag-feed-heading').innerText = "Latest Published Reports";
      document.getElementById('mag-feed-count').innerText = `Showing all ${ARTICLES_DATA.length} entries`;
      updateSeoMetadata(
        "GeneralPedia | The Digital Knowledge Hub & Magazine",
        "GeneralPedia is a premier digital news, encyclopedia, and magazine publication delivering verified guides, personal finance, health insights, and expert tutorials.",
        "/"
      );
      renderFeed(ARTICLES_DATA);
      if (push) history.pushState({ view: 'home' }, '', '/');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function filterCategory(slug, push = true) {
      if (slug === 'all' || !slug) {
        showHomeView(push);
        return;
      }

      hideAllViews();
      homeView.classList.remove('hidden');
      
      const titleMap = {
        'how-to': 'How-To & Practical Guides',
        'finance': 'Personal Finance & Tax Analysis',
        'health': 'Health, Medicine & Wellness Insights',
        'tools': 'Calculators & Interactive Reference',
        'automotive': 'Automotive Reviews & Diagnostics',
        'lifestyle': 'Home, Pet Care & Living',
        'culture': 'Culture, Sports & Entertainment'
      };

      const descMap = {
        'how-to': 'Step-by-step verified procedures, expert DIY walk-throughs, troubleshooting playbooks, and procedural solutions.',
        'finance': 'Fact-checked tax guidance, banking rates, business analysis, retirement planning, and monetary calculations.',
        'health': 'Evidence-based health information, nutritional summaries, medical reference charts, and wellness guides.',
        'tools': 'Interactive mathematical utilities, date/age calculators, unit converters, and decision-support algorithms.',
        'automotive': 'Diagnostic codes, vehicle care schedules, specifications, mechanics guides, and buying advice.',
        'lifestyle': 'Home organization, gardening advice, pet nutrition, living essentials, and daily lifestyle improvements.',
        'culture': 'Historical retrospectives, global traditions, literature reviews, athletic milestones, and media insights.'
      };

      const catTitle = titleMap[slug] || (slug.charAt(0).toUpperCase() + slug.slice(1));
      const catDesc = descMap[slug] || 'Curated editorial manuals, in-depth breakdowns, and interactive references.';

      if (homeHeroSection) homeHeroSection.classList.add('hidden');
      if (homeTrendingSection) homeTrendingSection.classList.add('hidden');
      if (categoryHeaderBanner) {
        categoryHeaderBanner.classList.remove('hidden');
        document.getElementById('category-crumb-current').innerText = catTitle;
        document.getElementById('category-banner-title').innerText = catTitle;
        document.getElementById('category-banner-desc').innerText = catDesc;
      }
      document.getElementById('mag-feed-heading').innerText = `${catTitle} Feed`;

      currentCategorySlug = slug;
      updateNavHighlight(slug);

      const filtered = ARTICLES_DATA.filter(a => a.category_slug === slug);

      if (categoryHeaderBanner) {
        document.getElementById('category-banner-meta').innerText = `Showing ${filtered.length} verified ${filtered.length === 1 ? 'guide' : 'guides'}`;
      }
      document.getElementById('mag-feed-count').innerText = `Showing ${filtered.length} articles in this topic`;
      updateSeoMetadata(`${catTitle} | GeneralPedia`, catDesc, `/category/${slug}`);
      renderFeed(filtered);
      if (push) history.pushState({ view: 'category', slug: slug }, '', `/category/${slug}`);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function updateNavHighlight(slug) {
      document.querySelectorAll('.nav-item-btn').forEach(btn => {
        if (btn.dataset.cat === slug) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    function renderFeed(items) {
      articlesFeed.innerHTML = '';
      if (!items || items.length === 0) {
        articlesFeed.innerHTML = `
          <div style="grid-column: 1 / -1; padding: 48px 24px; text-align: center; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md);">
            <p style="font-weight: 700; font-size: 1.125rem; margin-bottom: 6px;">No articles currently in this section</p>
            <p style="font-size: 0.875rem; color: var(--text-subtle);">Additional editorial guides are continually published by our research team.</p>
          </div>
        `;
        return;
      }

      items.forEach(art => {
        const card = document.createElement('article');
        card.className = 'mag-article-card';
        card.tabIndex = 0;
        card.onclick = () => openArticle(art.id);
        card.onkeydown = (e) => { if (e.key === 'Enter') openArticle(art.id); };

        card.innerHTML = `
          <div class="mag-card-header">
            <div class="mag-card-meta">
              <span class="category-badge" style="font-size: 0.6875rem; padding: 2px 6px;">${escapeHtml(art.category_name || 'Guide')}</span>
              <span>•</span>
              <span>${art.display_date || 'Recent'}</span>
            </div>
            <h3 class="mag-card-title">${escapeHtml(art.title)}</h3>
          </div>
          <div class="mag-card-body">
            <p class="mag-card-excerpt">${escapeHtml(art.meta_description || '')}</p>
            <div class="mag-card-footer">
              <span>Read Full Story →</span>
              <span style="color: var(--text-subtle); font-weight: 500;">${art.read_time || '5 min read'}</span>
            </div>
          </div>
        `;
        articlesFeed.appendChild(card);
      });
    }

    function renderTrendingMini() {
      if (!trendingMiniContainer) return;
      trendingMiniContainer.innerHTML = '';
      
      const sample = ARTICLES_DATA.slice(0, 4);
      sample.forEach(art => {
        const div = document.createElement('div');
        div.className = 'mini-card';
        div.tabIndex = 0;
        div.onclick = () => openArticle(art.id);
        div.onkeydown = (e) => { if (e.key === 'Enter') openArticle(art.id); };
        div.innerHTML = `
          <div>
            <div class="mini-card-tag">${escapeHtml(art.category_name || 'Trending')}</div>
            <h4 class="mini-card-title">${escapeHtml(art.title)}</h4>
          </div>
          <div class="mini-card-date">${art.display_date || 'Updated'} • ${art.read_time || '4 min'}</div>
        `;
        trendingMiniContainer.appendChild(div);
      });
    }

    function renderPopularSidebar() {
      if (!popularPostsList) return;
      popularPostsList.innerHTML = '';
      
      // Select 5 varied stories
      const top5 = ARTICLES_DATA.slice(0, 5);
      top5.forEach((art, idx) => {
        const div = document.createElement('div');
        div.className = 'popular-item';
        div.tabIndex = 0;
        div.onclick = () => openArticle(art.id);
        div.onkeydown = (e) => { if (e.key === 'Enter') openArticle(art.id); };
        div.innerHTML = `
          <div class="popular-num">0${idx + 1}</div>
          <div class="popular-content">
            <div class="popular-title">${escapeHtml(art.title)}</div>
            <span>${art.display_date || 'Recent'} • ${escapeHtml(art.category_name || 'Guide')}</span>
          </div>
        `;
        popularPostsList.appendChild(div);
      });

      // Also render in article view sidebar
      const artSidebarTrending = document.getElementById('art-sidebar-trending');
      if (artSidebarTrending) {
        artSidebarTrending.innerHTML = popularPostsList.innerHTML;
        // reattach click handlers
        Array.from(artSidebarTrending.children).forEach((child, idx) => {
          child.onclick = () => openArticle(top5[idx].id);
        });
      }
    }

    async function openArticle(id, push = true) {
      let post = ARTICLES_DATA.find(a => a.id === id);
      if (!post || !post.content_html) {
        try {
          const res = await fetch(`/api/post/${id}`);
          if (res.ok) post = await res.json();
        } catch(e) {}
      }
      if (!post) return;

      document.getElementById('art-title').innerText = post.title;
      document.getElementById('art-meta').innerText = post.meta_description || '';
      document.getElementById('art-category-badge').innerText = post.category_name || 'Knowledge Guide';
      document.getElementById('art-category-crumb').innerText = post.category_name || 'Category';
      if (post.category_slug) {
        currentCategorySlug = post.category_slug;
        updateNavHighlight(post.category_slug);
        const catCrumb = document.getElementById('art-category-crumb');
        if (catCrumb) {
          catCrumb.onclick = () => filterCategory(post.category_slug);
        }
      }
      document.getElementById('art-title-crumb').innerText = post.primary_keyword || post.title;
      document.getElementById('art-date').innerText = post.display_date || 'Recently Published';
      document.getElementById('art-read-time').innerText = post.read_time || '5 min read';
      document.getElementById('art-content').innerHTML = post.content_html || '<p>Content preview available shortly.</p>';
      updateSeoMetadata(
        `${post.title} | GeneralPedia`,
        post.meta_description || 'Comprehensive factual reference guide and breakdown on GeneralPedia.',
        `/${id}`
      );

      hideAllViews();
      articleView.classList.remove('hidden');
      if (push) history.pushState({ view: 'article', id: id }, '', `/${id}`);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function showStaticPage(slug, push = true) {
      updateNavHighlight(null);
      const page = STATIC_PAGES[slug];
      if (!page) return;

      document.getElementById('static-crumb').innerText = page.title;
      document.getElementById('static-content').innerHTML = page.content;
      const cleanTitle = page.title.replace('&amp;', '&');
      updateSeoMetadata(
        `${cleanTitle} | GeneralPedia`,
        `Official ${cleanTitle} document and informational guide for GeneralPedia publication.`,
        `/${slug}`
      );

      hideAllViews();
      staticView.classList.remove('hidden');
      if (push) history.pushState({ view: 'static', slug: slug }, '', `/${slug}`);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function triggerSearchFocus() {
      const searchInput = document.getElementById('nav-search-input');
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    }

    function executeSearch(query, push = true) {
      if (!query || !query.trim()) return;
      updateNavHighlight(null);
      const q = query.trim().toLowerCase();
      const results = ARTICLES_DATA.filter(a => 
        a.title.toLowerCase().includes(q) ||
        (a.primary_keyword && a.primary_keyword.toLowerCase().includes(q)) ||
        (a.semantic_keywords && a.semantic_keywords.some(sk => sk.toLowerCase().includes(q))) ||
        (a.category_name && a.category_name.toLowerCase().includes(q))
      );

      hideAllViews();
      searchView.classList.remove('hidden');
      document.getElementById('search-query-title').innerText = `Search: "${query.trim()}"`;
      document.getElementById('search-count-meta').innerText = `${results.length} result${results.length === 1 ? '' : 's'} identified`;
      updateSeoMetadata(
        `Search: "${query.trim()}" | GeneralPedia`,
        `Explore verified search results for "${query.trim()}" across GeneralPedia knowledge hub.`,
        `/?q=${encodeURIComponent(query.trim())}`
      );
      if (push) history.pushState({ view: 'search', q: query.trim() }, '', `/?q=${encodeURIComponent(query.trim())}`);

      const grid = document.getElementById('search-results-grid');
      grid.innerHTML = '';
      if (results.length === 0) {
        grid.innerHTML = `
          <div style="grid-column: 1 / -1; padding: 48px; text-align: center; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md);">
            <h3>No matching reports found for "${escapeHtml(query)}"</h3>
            <p style="color: var(--text-muted); margin-top: 8px;">Try broader terms such as "tax", "camry", "symptoms", or explore our category directory.</p>
          </div>
        `;
        return;
      }

      results.forEach(art => {
        const card = document.createElement('article');
        card.className = 'mag-article-card';
        card.tabIndex = 0;
        card.onclick = () => openArticle(art.id);
        card.innerHTML = `
          <div class="mag-card-header">
            <div class="mag-card-meta">
              <span class="category-badge" style="font-size: 0.6875rem; padding: 2px 6px;">${escapeHtml(art.category_name || 'Guide')}</span>
              <span>•</span>
              <span>${art.display_date || 'Recent'}</span>
            </div>
            <h3 class="mag-card-title">${escapeHtml(art.title)}</h3>
          </div>
          <div class="mag-card-body">
            <p class="mag-card-excerpt">${escapeHtml(art.meta_description || '')}</p>
            <div class="mag-card-footer">
              <span>Read Full Story →</span>
              <span style="color: var(--text-subtle);">${art.read_time || '5 min read'}</span>
            </div>
          </div>
        `;
        grid.appendChild(card);
      });

      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function toggleTheme() {
      const htmlEl = document.documentElement;
      const isDark = htmlEl.getAttribute('data-theme') === 'dark';
      const newTheme = isDark ? 'light' : 'dark';
      htmlEl.setAttribute('data-theme', newTheme);
      document.getElementById('theme-icon').innerText = isDark ? '🌙' : '☀️';
      document.getElementById('theme-label').innerText = isDark ? 'Dark' : 'Light';
      localStorage.setItem('gp_theme', newTheme);
    }

    // Check saved theme
    (function() {
      const saved = localStorage.getItem('gp_theme');
      if (saved) {
        document.documentElement.setAttribute('data-theme', saved);
        const btnIcon = document.getElementById('theme-icon');
        const btnLabel = document.getElementById('theme-label');
        if (btnIcon && btnLabel) {
          btnIcon.innerText = saved === 'dark' ? '☀️' : '🌙';
          btnLabel.innerText = saved === 'dark' ? 'Light' : 'Dark';
        }
      }
    })();

    function escapeHtml(str) {
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    // Handle URL routing on load and history navigation
    function handleRoute() {
      const path = window.location.pathname.replace(/^\/+|\/+$/g, '');
      const searchParams = new URLSearchParams(window.location.search);
      const query = searchParams.get('q');

      if (query) {
        executeSearch(query, false);
        return;
      }

      if (!path) {
        showHomeView(false);
        return;
      }

      if (path.startsWith('category/')) {
        const catSlug = path.replace('category/', '');
        filterCategory(catSlug, false);
        return;
      }

      if (STATIC_PAGES[path]) {
        showStaticPage(path, false);
        return;
      }

      const foundArticle = ARTICLES_DATA.find(a => a.id === path);
      if (foundArticle) {
        openArticle(path, false);
        return;
      }

      // Fallback
      showHomeView(false);
    }

    window.addEventListener('popstate', (e) => {
      handleRoute();
    });

    // Init
    renderHeroGrid();
    renderTrendingMini();
    renderPopularSidebar();
    handleRoute();
