    function handleCardClick(e, id) {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey || (e.button && e.button !== 0)) {
        return; // Allow native browser behavior for new tab / window / middle click
      }
      e.preventDefault();
      openArticle(id);
    }

    function renderHeroGrid() {
      const heroContainer = document.getElementById('hero-grid-container');
      if (!heroContainer || typeof ARTICLES_DATA === 'undefined' || ARTICLES_DATA.length === 0) return;
      const p1 = ARTICLES_DATA[0];
      const p2 = ARTICLES_DATA[1] || p1;
      const p3 = ARTICLES_DATA[2] || p1;

      function getImg(art) {
        if (!art) return '';
        if (art.featured_image) return art.featured_image;
        if (art.content_html) {
          const m = art.content_html.match(/<img[^>]+src=["']([^"']+)["']/);
          if (m) return m[1];
        }
        return '';
      }

      heroContainer.innerHTML = `
        <a href="/${p1.id}" class="hero-main-card" onclick="handleCardClick(event, '${p1.id}')" style="${getImg(p1) ? `background-image: url('${getImg(p1)}');` : ''}">
          <div class="hero-card-content">
            <span class="category-badge">${escapeHtml(p1.category_name || 'Featured')}</span>
            <h2 class="hero-main-title">${escapeHtml(p1.title)}</h2>
            <div class="hero-meta">
              <span>By <span class="art-author-link" style="color:#ffffff;font-weight:700;" onclick="event.preventDefault();event.stopPropagation();showAuthorProfile('${p1.category_slug||''}')">${escapeHtml(p1.author_name || 'Editorial Staff')}</span></span>
              <span>•</span>
              <span>${p1.display_date || 'Recent'}</span>
              <span>•</span>
              <span>${p1.read_time || '6 min read'}</span>
            </div>
          </div>
        </a>
        <a href="/${p2.id}" class="hero-sub-card" onclick="handleCardClick(event, '${p2.id}')" style="${getImg(p2) ? `background-image: url('${getImg(p2)}');` : ''}">
          <div class="hero-card-content">
            <span class="category-badge blue">${escapeHtml(p2.category_name || 'Guide')}</span>
            <h3 class="hero-sub-title">${escapeHtml(p2.title)}</h3>
            <div class="hero-meta">
              <span>${p2.display_date || 'Recent'}</span>
              <span>•</span>
              <span>${p2.read_time || '5 min'}</span>
            </div>
          </div>
        </a>
        <a href="/${p3.id}" class="hero-sub-card" onclick="handleCardClick(event, '${p3.id}')" style="${getImg(p3) ? `background-image: url('${getImg(p3)}');` : ''}">
          <div class="hero-card-content">
            <span class="category-badge green">${escapeHtml(p3.category_name || 'Analysis')}</span>
            <h3 class="hero-sub-title">${escapeHtml(p3.title)}</h3>
            <div class="hero-meta">
              <span>${p3.display_date || 'Recent'}</span>
              <span>•</span>
              <span>${p3.read_time || '5 min'}</span>
            </div>
          </div>
        </a>
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
    const authorView = document.getElementById('author-view');

    const homeHeroSection = document.getElementById('home-hero-section');
    const homeTrendingSection = document.getElementById('home-trending-section');

    const categoryHeaderBanner = document.getElementById('category-header-banner');

    function hideAllViews() {
      homeView.classList.add('hidden');
      articleView.classList.add('hidden');
      staticView.classList.add('hidden');
      searchView.classList.add('hidden');
      if (authorView) authorView.classList.add('hidden');
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
      renderFeed(ARTICLES_DATA.length > 3 ? ARTICLES_DATA.slice(3) : ARTICLES_DATA);
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
        const card = document.createElement('a');
        card.href = `/${art.id}`;
        card.className = 'mag-article-card';
        card.onclick = (e) => handleCardClick(e, art.id);

        function extractThumb(article) {
          if (article.featured_image) return article.featured_image;
          if (article.content_html) {
            const m = article.content_html.match(/<img[^>]+src=["']([^"']+)["']/);
            if (m) return m[1];
          }
          return 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?auto=format&fit=crop&w=800&q=80';
        }

        const thumbUrl = extractThumb(art);

        card.innerHTML = `
          <div class="mag-card-thumb">
            <span class="category-badge" style="font-size: 0.6875rem; padding: 3px 8px;">${escapeHtml(art.category_name || 'Guide')}</span>
            <img src="${thumbUrl}" alt="${escapeHtml(art.title)}" loading="lazy">
          </div>
          <div class="mag-card-body">
            <div class="mag-card-meta">
              <span>${art.display_date || 'Recent'}</span>
              <span>•</span>
              <span>${art.read_time || '5 min read'}</span>
            </div>
            <h3 class="mag-card-title">${escapeHtml(art.title)}</h3>
            <p class="mag-card-excerpt">${escapeHtml(art.meta_description || '')}</p>
            <div class="mag-card-footer">
              <span>Read Full Story →</span>
              <span style="color: var(--text-subtle); font-weight: 500;">Editorial Report</span>
            </div>
          </div>
        `;
        articlesFeed.appendChild(card);
      });
    }

    function renderTrendingMini() {
      if (!trendingMiniContainer) return;
      trendingMiniContainer.innerHTML = '';
      
      const sample = ARTICLES_DATA.length > 3 ? ARTICLES_DATA.slice(3, 7) : ARTICLES_DATA.slice(0, 4);
      sample.forEach(art => {
        const card = document.createElement('a');
        card.href = `/${art.id}`;
        card.className = 'mini-card';
        card.onclick = (e) => handleCardClick(e, art.id);
        card.innerHTML = `
          <div>
            <div class="mini-card-tag">${escapeHtml(art.category_name || 'Trending')}</div>
            <h4 class="mini-card-title">${escapeHtml(art.title)}</h4>
          </div>
          <div class="mini-card-date">${art.display_date || 'Updated'} • ${art.read_time || '4 min'}</div>
        `;
        trendingMiniContainer.appendChild(card);
      });
    }

    function renderPopularSidebar() {
      if (!popularPostsList) return;
      popularPostsList.innerHTML = '';
      
      // Select 5 varied stories
      const top5 = ARTICLES_DATA.slice(0, 5);
      top5.forEach((art, idx) => {
        const card = document.createElement('a');
        card.href = `/${art.id}`;
        card.className = 'popular-item';
        card.onclick = (e) => handleCardClick(e, art.id);
        card.innerHTML = `
          <div class="popular-num">0${idx + 1}</div>
          <div class="popular-content">
            <div class="popular-title">${escapeHtml(art.title)}</div>
            <span>${art.display_date || 'Recent'} • ${escapeHtml(art.category_name || 'Guide')}</span>
          </div>
        `;
        popularPostsList.appendChild(card);
      });

      // Also render in article view sidebar
      const artSidebarTrending = document.getElementById('art-sidebar-trending');
      if (artSidebarTrending) {
        artSidebarTrending.innerHTML = popularPostsList.innerHTML;
        // reattach click handlers
        Array.from(artSidebarTrending.children).forEach((child, idx) => {
          child.onclick = (e) => handleCardClick(e, top5[idx].id);
        });
      }
    }

    function findArticle(idOrSlug) {
      if (!idOrSlug || typeof ARTICLES_DATA === 'undefined') return null;
      const clean = String(idOrSlug).toLowerCase().trim().replace(/^\/+|\/+$/g, '');
      
      // 1. Direct match on id or slug
      let match = ARTICLES_DATA.find(a => (a.id && a.id.toLowerCase() === clean) || (a.slug && a.slug.toLowerCase() === clean));
      if (match) return match;

      // 2. Prefix match (e.g. honda-crv-2026 matches honda-crv-2026-price-specs-features-trim)
      match = ARTICLES_DATA.find(a => a.id && a.id.toLowerCase().startsWith(clean + '-'));
      if (match) return match;

      // 3. Match against primary keyword slugified
      match = ARTICLES_DATA.find(a => {
        if (!a.primary_keyword) return false;
        const kwSlug = a.primary_keyword.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
        return kwSlug === clean || clean.startsWith(kwSlug) || kwSlug.startsWith(clean);
      });
      if (match) return match;

      // 4. Substring containment match
      match = ARTICLES_DATA.find(a => a.id && (a.id.toLowerCase().includes(clean) || clean.includes(a.id.toLowerCase())));
      return match || null;
    }

    async function openArticle(id, push = true) {
      let post = findArticle(id);
      if (!post || !post.content_html) {
        try {
          const res = await fetch(`/api/post/${id}`);
          if (res.ok) {
            post = await res.json();
          }
        } catch(e) {}
      }
      if (!post) {
        console.warn('Post not found for id/slug:', id);
        return;
      }

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
      // Set author info
      const authorNameEl = document.getElementById('art-author-name');
      const authorSlug = getAuthorSlug(post.author_name);
      const authorCatSlug = post.category_slug || '';
      if (authorNameEl) {
        authorNameEl.innerHTML = `<a href="/author/${authorSlug}" class="art-author-link" onclick="event.preventDefault(); showAuthorProfile('${authorCatSlug}')">${escapeHtml(post.author_name || 'Editorial Staff')}</a>`;
      }
      const avatarImg = document.getElementById('art-avatar-img');
      if (avatarImg && post.author_avatar) {
        avatarImg.src = post.author_avatar;
        avatarImg.alt = post.author_name || 'Author';
        avatarImg.style.cursor = 'pointer';
        avatarImg.onclick = function(e) { e.preventDefault(); showAuthorProfile(authorCatSlug); };
      }
      const contentEl = document.getElementById('art-content');
      contentEl.innerHTML = post.content_html || '<p>Content preview available shortly.</p>';
      // Execute any interactive script tags embedded inside the article content (e.g. calculators)
      const scripts = contentEl.querySelectorAll('script');
      scripts.forEach(oldScript => {
        const newScript = document.createElement('script');
        Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
        newScript.appendChild(document.createTextNode(oldScript.innerHTML));
        oldScript.parentNode.replaceChild(newScript, oldScript);
      });

      updateSeoMetadata(
        `${post.title} | GeneralPedia`,
        post.meta_description || 'Comprehensive factual reference guide and breakdown on GeneralPedia.',
        `/${id}`
      );

      // Dynamically inject or remove FAQ Schema JSON-LD for rich snippets
      let faqSchemaTag = document.getElementById('article-faq-schema');
      if (post.faq_schema) {
        if (!faqSchemaTag) {
          faqSchemaTag = document.createElement('script');
          faqSchemaTag.id = 'article-faq-schema';
          faqSchemaTag.type = 'application/ld+json';
          document.head.appendChild(faqSchemaTag);
        }
        faqSchemaTag.textContent = typeof post.faq_schema === 'string' ? post.faq_schema : JSON.stringify(post.faq_schema);
      } else if (faqSchemaTag) {
        faqSchemaTag.remove();
      }

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
        const card = document.createElement('a');
        card.href = `/${art.id}`;
        card.className = 'mag-article-card';
        card.onclick = (e) => handleCardClick(e, art.id);
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

    // Author data for profile pages
    const AUTHORS_DATA = {
      'how-to': { name: 'Marcus Reid', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=120&h=120&q=80', bio: 'Senior technical writer specializing in step-by-step troubleshooting guides and practical DIY solutions.', category: 'How-To & Guides' },
      'finance': { name: 'Sarah Mitchell', avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=120&h=120&q=80', bio: 'Certified financial analyst covering tax strategy, retirement planning, and personal budgeting insights.', category: 'Finance & Money' },
      'health': { name: 'Elena Torres', avatar: 'https://images.unsplash.com/photo-1594824476967-48c8b964ac31?auto=format&fit=crop&w=120&h=120&q=80', bio: 'Health science researcher and medical journalist writing evidence-based wellness and symptom guides.', category: 'Health & Wellness' },
      'tools': { name: 'James Carter', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=120&h=120&q=80', bio: 'Data engineer and calculator developer building interactive financial and measurement reference tools.', category: 'Calculators & Tools' },
      'automotive': { name: 'David Chen', avatar: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=120&h=120&q=80', bio: 'Automotive journalist with ten years of experience in vehicle diagnostics, specs, and market reviews.', category: 'Automotive' },
      'tech': { name: 'Ryan Kowalski', avatar: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=120&h=120&q=80', bio: 'Software engineer and cybersecurity specialist explaining digital tools and emerging tech trends.', category: 'Tech & Digital' },
      'lifestyle': { name: 'Nora Jacobs', avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=120&h=120&q=80', bio: 'Home living editor covering pet nutrition, cleaning hacks, recipes, and everyday household advice.', category: 'Home & Lifestyle' },
      'culture': { name: 'Amir Hassan', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=120&h=120&q=80', bio: 'Culture and entertainment critic reviewing global events, sports milestones, and film analysis.', category: 'Entertainment & Culture' }
    };

    function getAuthorSlug(authorName) {
      return (authorName || '').toLowerCase().replace(/\s+/g, '-');
    }

    function findAuthorBySlug(slug) {
      for (const cat in AUTHORS_DATA) {
        if (getAuthorSlug(AUTHORS_DATA[cat].name) === slug) return { ...AUTHORS_DATA[cat], catSlug: cat };
      }
      return null;
    }

    function showAuthorProfile(catSlug, push) {
      const author = AUTHORS_DATA[catSlug];
      if (!author) { showHomeView(); return; }
      hideAllViews();
      if (authorView) authorView.classList.remove('hidden');

      document.getElementById('author-profile-avatar').src = author.avatar;
      document.getElementById('author-profile-avatar').alt = author.name;
      document.getElementById('author-profile-name').innerText = author.name;
      document.getElementById('author-profile-role').innerText = author.category + ' Writer';
      document.getElementById('author-profile-bio').innerText = author.bio;

      const authorArticles = ARTICLES_DATA.filter(a => a.category_slug === catSlug);
      document.getElementById('author-articles-heading').innerText = 'Articles by ' + author.name;
      document.getElementById('author-articles-count').innerText = authorArticles.length + ' article' + (authorArticles.length !== 1 ? 's' : '');

      const grid = document.getElementById('author-articles-grid');
      if (authorArticles.length === 0) {
        grid.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px 0;">No published articles yet.</p>';
      } else {
        grid.innerHTML = authorArticles.map(art => `
          <a href="/${art.id}" class="feed-card" onclick="handleCardClick(event, '${art.id}')">
            ${art.featured_image ? `<img class="feed-card-img" src="${art.featured_image}" alt="${escapeHtml(art.title)}" loading="lazy" />` : ''}
            <div class="feed-card-body">
              <span class="category-badge small">${escapeHtml(art.category_name || '')}</span>
              <h3 class="feed-card-title">${escapeHtml(art.title)}</h3>
              <div class="feed-card-meta"><span>${art.display_date || 'Recent'}</span><span>•</span><span>${art.read_time || '5 min read'}</span></div>
            </div>
          </a>`).join('');
      }

      const slug = getAuthorSlug(author.name);
      updateSeoMetadata(author.name + ' | GeneralPedia Author', author.bio, 'author/' + slug);
      if (push !== false) history.pushState({}, '', '/author/' + slug);
      window.scrollTo({ top: 0, behavior: 'smooth' });
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

      if (path.startsWith('author/')) {
        const authorSlug = path.replace('author/', '');
        const authorMatch = findAuthorBySlug(authorSlug);
        if (authorMatch) { showAuthorProfile(authorMatch.catSlug, false); return; }
      }

      if (path.startsWith('category/')) {
        const catSlug = path.replace('category/', '');
        filterCategory(catSlug, false);
        return;
      }

      if (typeof STATIC_PAGES !== 'undefined' && STATIC_PAGES[path]) {
        showStaticPage(path, false);
        return;
      }

      const foundArticle = findArticle(path);
      if (foundArticle) {
        openArticle(foundArticle.id, false);
        return;
      }

      // Fallback
      showHomeView(false);
    }

    window.addEventListener('popstate', (e) => {
      handleRoute();
    });

    function updateLiveDate() {
      const dateEl = document.getElementById('current-date-display');
      if (!dateEl) return;
      try {
        const now = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        dateEl.innerText = now.toLocaleDateString('en-US', options);
      } catch (e) {}
    }

    // Init
    updateLiveDate();
    renderHeroGrid();
    renderTrendingMini();
    renderPopularSidebar();
    handleRoute();
