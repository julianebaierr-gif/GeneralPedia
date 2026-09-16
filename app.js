    function handleCardClick(e, id) {
      // Allow natural browser navigation to the article's pre-rendered HTML page
      // Each article has its own .html file with full content already rendered
      // No SPA routing needed - direct navigation is faster and always works
    }

    function handleNavClick(e, actionFn) {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey || (e.button && e.button !== 0)) {
        return; // Allow native browser open in new tab/window
      }
      // If we are on the homepage (pathname === '/'), perform smooth client-side filtering
      const isHome = window.location.pathname === '/' || window.location.pathname === '/index.html' || window.location.pathname === '';
      if (isHome && typeof actionFn === 'function') {
        e.preventDefault();
        actionFn();
      }
      // Otherwise, let the browser naturally navigate to the target href (no JS intercept bug)
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
          const m = art.content_html.match(/<\x69mg[^>]+src=["']([^"']+)["']/);
          if (m) return m[1];
        }
        return '';
      }

      heroContainer.innerHTML = `
        <a href="/${p1.id}" class="hero-main-card" onclick="handleCardClick(event, '${p1.id}')" style="${getImg(p1) ? `background-image: url('${getImg(p1)}');` : ''}">
          <div class="hero-card-content">
            <span class="category-badge">${escapeHtml(p1.category_name || 'Featured')}</span>
            <div class="hero-main-title">${escapeHtml(p1.title)}</div>
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
            <div class="hero-sub-title">${escapeHtml(p2.title)}</div>
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
            <div class="hero-sub-title">${escapeHtml(p3.title)}</div>
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
        canonical.setAttribute('href', `https://www.generalpedia.com${cleanPath}`);
      }
    }

    // Pagination State
    const PAGE_SIZE = 16;
    let currentFeedArticles = [];
    let currentDisplayedCount = 0;

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
      updateSeoMetadata(
        "GeneralPedia | The Digital Knowledge Hub & Magazine",
        "GeneralPedia is a premier digital news, encyclopedia, and magazine publication delivering verified guides, personal finance, health insights, and expert tutorials.",
        "/"
      );
      const feedItems = ARTICLES_DATA.length > 3 ? ARTICLES_DATA.slice(3) : ARTICLES_DATA;
      renderFeed(feedItems, PAGE_SIZE);
      if (push) history.pushState({ view: 'home' }, '', '/');
      window.scrollTo({ top: 0, behavior: 'instant' });
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

      updateSeoMetadata(`${catTitle} | GeneralPedia`, catDesc, `/category/${slug}`);
      renderFeed(filtered, PAGE_SIZE);
      if (push) history.pushState({ view: 'category', slug: slug }, '', `/category/${slug}`);
      window.scrollTo({ top: 0, behavior: 'instant' });
    }

    function toggleMobileMenu() {
      const drawer = document.getElementById('mobile-nav-drawer');
      const overlay = document.getElementById('mobile-drawer-overlay');
      const btn = document.getElementById('mobile-menu-btn');
      if (!drawer || !overlay) return;
      const isOpen = drawer.classList.contains('active');
      if (isOpen) {
        closeMobileMenu();
      } else {
        drawer.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        if (btn) btn.setAttribute('aria-expanded', 'true');
      }
    }

    function closeMobileMenu() {
      const drawer = document.getElementById('mobile-nav-drawer');
      const overlay = document.getElementById('mobile-drawer-overlay');
      const btn = document.getElementById('mobile-menu-btn');
      if (drawer) drawer.classList.remove('active');
      if (overlay) overlay.classList.remove('active');
      document.body.style.overflow = '';
      if (btn) btn.setAttribute('aria-expanded', 'false');
    }

    function updateNavHighlight(slug) {
      document.querySelectorAll('.nav-item-btn').forEach(btn => {
        if (btn.dataset.cat === slug) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
      document.querySelectorAll('.mobile-nav-item').forEach(btn => {
        if (btn.dataset.cat === slug) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    function createFeedCard(art) {
      const card = document.createElement('a');
      card.href = `/${art.id}`;
      card.className = 'mag-article-card';
      card.onclick = (e) => handleCardClick(e, art.id);

      function extractThumb(article) {
        if (article.featured_image) return article.featured_image;
        if (article.content_html) {
          const m = article.content_html.match(/<\x69mg[^>]+src=["']([^"']+)["']/);
          if (m) return m[1];
        }
        return 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?auto=format&fit=crop&w=800&q=80';
      }

      const thumbUrl = extractThumb(art);

      card.innerHTML = `
        <div class="mag-card-thumb">
          <span class="category-badge" style="font-size: 0.6875rem; padding: 3px 8px;">${escapeHtml(art.category_name || 'Guide')}</span>
          <img src="${thumbUrl}" alt="${escapeHtml(art.title)}" width="600" height="338" loading="lazy">
        </div>
        <div class="mag-card-body">
          <div class="mag-card-meta">
            <span>${art.display_date || 'Recent'}</span>
            <span>•</span>
            <span>${art.read_time || '5 min read'}</span>
          </div>
          <div class="mag-card-title">${escapeHtml(art.title)}</div>
          <p class="mag-card-excerpt">${escapeHtml(art.meta_description || '')}</p>
          <div class="mag-card-footer">
            <span>Read Full Story →</span>
            <span style="color: var(--text-subtle); font-weight: 500;">Editorial Report</span>
          </div>
        </div>
      `;
      return card;
    }

    function updateFeedCounts(displayed, total) {
      const feedCountEl = document.getElementById('mag-feed-count');
      if (feedCountEl) {
        if (total === 0) {
          feedCountEl.innerText = "0 guides available";
        } else if (displayed >= total) {
          feedCountEl.innerText = `Showing all ${total} entries`;
        } else {
          feedCountEl.innerText = `Showing ${displayed} of ${total} entries`;
        }
      }

      const bannerMetaEl = document.getElementById('category-banner-meta');
      if (bannerMetaEl && categoryHeaderBanner && !categoryHeaderBanner.classList.contains('hidden')) {
        if (total === 0) {
          bannerMetaEl.innerText = "Showing 0 verified guides";
        } else if (displayed >= total) {
          bannerMetaEl.innerText = `Showing all ${total} verified ${total === 1 ? 'guide' : 'guides'}`;
        } else {
          bannerMetaEl.innerText = `Showing ${displayed} of ${total} verified guides`;
        }
      }

      const loadMoreBtn = document.getElementById('feed-load-more-btn');
      if (loadMoreBtn) {
        if (displayed < total) {
          loadMoreBtn.classList.remove('hidden');
          const remaining = total - displayed;
          const nextBatch = Math.min(remaining, PAGE_SIZE);
          loadMoreBtn.innerHTML = `
            <span>Load More Articles (${remaining} remaining)</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
          `;
        } else {
          loadMoreBtn.classList.add('hidden');
        }
      }
    }

    function renderFeed(items, initialLimit = PAGE_SIZE) {
      articlesFeed.innerHTML = '';
      currentFeedArticles = items || [];
      currentDisplayedCount = 0;

      if (!currentFeedArticles || currentFeedArticles.length === 0) {
        articlesFeed.innerHTML = `
          <div style="grid-column: 1 / -1; padding: 48px 24px; text-align: center; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md);">
            <p style="font-weight: 700; font-size: 1.125rem; margin-bottom: 6px;">No articles currently in this section</p>
            <p style="font-size: 0.875rem; color: var(--text-subtle);">Additional editorial guides are continually published by our research team.</p>
          </div>
        `;
        updateFeedCounts(0, 0);
        return;
      }

      const countToRender = Math.min(initialLimit, currentFeedArticles.length);
      for (let i = 0; i < countToRender; i++) {
        articlesFeed.appendChild(createFeedCard(currentFeedArticles[i]));
      }
      currentDisplayedCount = countToRender;
      updateFeedCounts(currentDisplayedCount, currentFeedArticles.length);
    }

    function loadMoreArticles() {
      if (!currentFeedArticles || currentDisplayedCount >= currentFeedArticles.length) return;
      const nextBatchCount = Math.min(PAGE_SIZE, currentFeedArticles.length - currentDisplayedCount);
      const endIndex = currentDisplayedCount + nextBatchCount;

      for (let i = currentDisplayedCount; i < endIndex; i++) {
        articlesFeed.appendChild(createFeedCard(currentFeedArticles[i]));
      }
      currentDisplayedCount = endIndex;
      updateFeedCounts(currentDisplayedCount, currentFeedArticles.length);
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
            <div class="mini-card-title">${escapeHtml(art.title)}</div>
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

    function renderCategoryTaxonomySidebar() {
      const catListEl = document.getElementById('cat-tax-list');
      if (!catListEl || typeof ARTICLES_DATA === 'undefined') return;

      const categoriesConfig = [
        { slug: 'how-to', name: 'How-To & Tutorials' },
        { slug: 'finance', name: 'Finance & Tax' },
        { slug: 'health', name: 'Health & Wellness' },
        { slug: 'tools', name: 'Calculators & Tools' },
        { slug: 'automotive', name: 'Automotive' },
        { slug: 'lifestyle', name: 'Lifestyle & Living' },
        { slug: 'culture', name: 'Culture & Tarot' }
      ];

      // Calculate real-time dynamic count for each category
      const counts = {};
      ARTICLES_DATA.forEach(art => {
        const cat = art.category_slug || '';
        counts[cat] = (counts[cat] || 0) + 1;
      });

      catListEl.innerHTML = categoriesConfig.map(cat => {
        const count = counts[cat.slug] || 0;
        return `
          <li>
            <a href="/category/${cat.slug}" class="cat-tax-item" onclick="handleNavClick(event, () => filterCategory('${cat.slug}'))" style="text-decoration:none; display:flex; justify-content:space-between; align-items:center; color:inherit;">
              <span>${cat.name}</span>
              <span class="cat-count">${count}</span>
            </a>
          </li>
        `;
      }).join('');
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
      const contentEl = document.getElementById('art-content');
      const hasPreRendered = contentEl && contentEl.innerHTML.trim().length > 100;

      // Only fetch from API if we have NO post data AND NO pre-rendered content
      if (!post && !hasPreRendered) {
        try {
          const res = await fetch(`/api/post/${id}`);
          if (res.ok) {
            post = await res.json();
          }
        } catch(e) {}
      }

      if (!post && !hasPreRendered) {
        console.warn('Post not found for id/slug:', id);
        return;
      }

      // If we have post metadata, update header elements
      if (post) {
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

        // Set author info — use AUTHORS_DATA for avatar if not in post
        const authorNameEl = document.getElementById('art-author-name');
        const authorSlug = getAuthorSlug(post.author_name);
        const authorCatSlug = post.category_slug || '';
        if (authorNameEl) {
          authorNameEl.innerHTML = `<a href="/author/${authorSlug}" class="art-author-link" onclick="event.preventDefault(); showAuthorProfile('${authorCatSlug}')">${escapeHtml(post.author_name || 'Editorial Staff')}</a>`;
        }
        const avatarImg = document.getElementById('art-avatar-img');
        if (avatarImg) {
          const authorData = AUTHORS_DATA[authorCatSlug];
          const avatarSrc = post.author_avatar || (authorData && authorData.avatar) || '';
          if (avatarSrc) {
            avatarImg.src = avatarSrc;
            avatarImg.alt = post.author_name || 'Author';
            avatarImg.style.cursor = 'pointer';
            avatarImg.onclick = function(e) { e.preventDefault(); showAuthorProfile(authorCatSlug); };
          }
        }

        // Only overwrite content if post has content_html (from API or site_data)
        // Otherwise keep the pre-rendered HTML that's already in the page
        if (post.content_html && contentEl) {
          contentEl.innerHTML = post.content_html;
        }
      }

      // Execute any interactive script tags embedded inside the article content (e.g. calculators)
      if (contentEl) {
        const scripts = contentEl.querySelectorAll('script');
        scripts.forEach(oldScript => {
          const newScript = document.createElement('script');
          Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
          newScript.appendChild(document.createTextNode(oldScript.innerHTML));
          oldScript.parentNode.replaceChild(newScript, oldScript);
        });
      }

      if (post) {
        updateSeoMetadata(
          `${post.title} | GeneralPedia`,
          post.meta_description || 'Comprehensive factual reference guide and breakdown on GeneralPedia.',
          `/${id}`
        );
      }

      // Dynamically inject or remove FAQ Schema JSON-LD for rich snippets
      let faqSchemaTag = document.getElementById('article-faq-schema');
      if (post && post.faq_schema) {
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
      window.scrollTo({ top: 0, behavior: 'instant' });
    }


    function showStaticPage(slug, push = true) {
      updateNavHighlight(null);
      const page = STATIC_PAGES[slug];
      if (!page) return;

      document.getElementById('static-crumb').innerText = page.title;
      document.getElementById('static-content').innerHTML = page.content;
      const cleanTitle = page.title.replace('&amp;', '&');
      const staticDesc = page.description || `Official ${cleanTitle} document and informational guide for GeneralPedia publication.`;
      updateSeoMetadata(
        `${cleanTitle} | GeneralPedia`,
        staticDesc,
        `/${slug}`
      );

      hideAllViews();
      staticView.classList.remove('hidden');
      if (push) history.pushState({ view: 'static', slug: slug }, '', `/${slug}`);
      window.scrollTo({ top: 0, behavior: 'instant' });
    }

    window.handleContactSubmit = async function(event) {
      event.preventDefault();
      const form = event.target;
      const btn = document.getElementById('gp-submit-btn');
      const statusBox = document.getElementById('gp-form-status');

      if (!form) return;

      const origBtnText = btn ? btn.innerText : 'Transmit Message';
      if (btn) {
        btn.disabled = true;
        btn.innerText = 'Sending Message...';
        btn.style.opacity = '0.7';
      }

      if (statusBox) {
        statusBox.style.display = 'none';
        statusBox.innerText = '';
      }

      const formData = new FormData(form);
      const object = Object.fromEntries(formData);
      const json = JSON.stringify(object);

      try {
        const response = await fetch('https://api.web3forms.com/submit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: json
        });

        const result = await response.json();

        if (response.status === 200 && result.success) {
          form.reset();
          if (statusBox) {
            statusBox.style.display = 'block';
            statusBox.style.background = '#dcfce7';
            statusBox.style.color = '#15803d';
            statusBox.style.border = '1px solid #86efac';
            statusBox.innerText = '✓ Thank you! Your message has been sent successfully. Our team will get back to you shortly at your email.';
          }
        } else {
          if (statusBox) {
            statusBox.style.display = 'block';
            statusBox.style.background = '#fee2e2';
            statusBox.style.color = '#b91c1c';
            statusBox.style.border = '1px solid #fca5a5';
            statusBox.innerText = result.message || 'Something went wrong. Please try again or email us directly at info.generalpedia1@gmail.com.';
          }
        }
      } catch (error) {
        if (statusBox) {
          statusBox.style.display = 'block';
          statusBox.style.background = '#fee2e2';
          statusBox.style.color = '#b91c1c';
          statusBox.style.border = '1px solid #fca5a5';
          statusBox.innerText = 'Network error. Please try again or email us directly at info.generalpedia1@gmail.com.';
        }
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerText = origBtnText;
          btn.style.opacity = '1';
        }
      }
    };

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
            <div style="font-size: 1.125rem; font-weight: 700; color: var(--text-main);">No matching reports found for "${escapeHtml(query)}"</div>
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
            <div class="mag-card-title">${escapeHtml(art.title)}</div>
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

      window.scrollTo({ top: 0, behavior: 'instant' });
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
      'how-to': {
        name: 'Marcus Reid',
        role: 'Senior Technical Writer & DIY Systems Editor',
        avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=240&h=240&q=85',
        bio: 'Marcus Reid leads the How-To & Tutorials desk at GeneralPedia, focusing on actionable DIY repairs, appliance diagnostics, technical troubleshooting protocols, and step-by-step consumer workflows. With over a decade of hands-on experience evaluating mechanical systems and home maintenance workflows, Marcus specializes in deconstructing complex repair procedures into accessible, safety-first tutorials. Every instructional guide published under his supervision undergoes rigorous bench testing and step-by-step verification to ensure reliability, tool clarity, and safety for readers of all technical skill levels.',
        experience: '12+ years experience in technical troubleshooting, appliance diagnosis, and DIY guide creation.',
        expertise: ['Home Appliance Diagnostics', 'Step-by-Step DIY Tutorials', 'Hardware Troubleshooting', 'Preventive Maintenance', 'Safety Protocols'],
        editorial_standards: 'All repair manuals require hands-on verification, required tool checklists, clear hazard warnings, and diagnostic logic trees before publication.',
        category: 'How-To & Guides'
      },
      'finance': {
        name: 'Sarah Mitchell',
        role: 'Certified Financial Analyst & Tax Strategy Editor',
        avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=240&h=240&q=85',
        bio: 'Sarah Mitchell directs financial analysis and tax research at GeneralPedia. She specializes in clarifying complex IRS tax codes, statutory retirement vehicles (401(k), Roth IRA, SEP-IRA), capital gains management, and household budgeting frameworks. Prior to joining GeneralPedia, Sarah managed private wealth portfolios and contributed quantitative economic research to financial advisory journals. Her writing empowers readers to make informed, data-driven decisions that safeguard their financial independence and optimize their long-term tax efficiency.',
        experience: '14+ years in personal wealth management, statutory tax compliance, and retirement investment analysis.',
        expertise: ['IRS Tax Brackets & Deadlines', 'Retirement Planning (401k & Roth IRA)', 'Capital Gains & Investment Strategy', 'Debt Management', 'Personal Budgeting'],
        editorial_standards: 'Strict adherence to official IRS statutory publications, empirical economic data, and transparent financial scenario modeling.',
        category: 'Finance & Money'
      },
      'health': {
        name: 'Elena Torres',
        role: 'Health Science Researcher & Clinical Wellness Editor',
        avatar: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=240&h=240&q=85',
        bio: 'Elena Torres oversees health, clinical wellness, and symptom analysis content at GeneralPedia. Drawing on extensive experience in biomedical research and public health communication, Elena translates complex clinical studies into clear, actionable health guides. Her work emphasizes preventative care, evidence-based lifestyle interventions, and objective symptom timelines. She collaborates closely with medical advisory standards to ensure all health documentation adheres strictly to recognized peer-reviewed medical literature and official health agency guidance.',
        experience: '9+ years in clinical journalism, biomedical research analysis, and public health communication.',
        expertise: ['Clinical Wellness Summaries', 'Symptom Progression Timelines', 'Preventative Healthcare', 'Evidence-Based Nutrition', 'Public Health Guidelines'],
        editorial_standards: 'Grounded entirely in peer-reviewed clinical literature (PubMed, CDC, WHO) with verified medical disclaimers and multi-stage fact checking.',
        category: 'Health & Wellness'
      },
      'tools': {
        name: 'James Carter',
        role: 'Senior Data Systems Engineer & Calculator Developer',
        avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=240&h=240&q=85',
        bio: 'James Carter is the lead systems architect and calculation developer for GeneralPedia\'s interactive tools directory. With a strong background in software engineering and applied mathematics, James designs and audits the algorithms powering our financial calculators, telecommunication directory lookups, conversion tools, and date calculators. He ensures that every computational engine on the platform executes with mathematical precision, instant latency, and complete transparency regarding underlying formulas.',
        experience: '11+ years in computational algorithms, telecommunication routing systems, and interactive calculation engines.',
        expertise: ['Interactive Financial Engines', 'Telecommunication Routing & Area Codes', 'Conversion Algorithms', 'Measurement Standards', 'Computational Modeling'],
        editorial_standards: 'Rigorous formula validation, edge-case testing, and real-time execution accuracy across all modern web browsers.',
        category: 'Calculators & Tools'
      },
      'automotive': {
        name: 'David Chen',
        role: 'Automotive Specialist & Vehicle Diagnostics Journalist',
        avatar: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=240&h=240&q=85',
        bio: 'David Chen is the automotive editor at GeneralPedia, providing comprehensive vehicle reviews, trim level comparisons, mechanical diagnostic procedures, and long-term ownership cost analyses. Having road-tested hundreds of vehicles and investigated automotive engineering advancements from hybrid powertrains to electric architectures, David delivers unvarnished, data-rich assessments to help buyers and vehicle owners make informed maintenance and purchasing choices.',
        experience: '10+ years in automotive road testing, powertrain engineering review, and OBD-II diagnostics.',
        expertise: ['Powertrain & Hybrid Technology', 'Vehicle Trim Comparisons', 'OBD-II Fault Diagnostics', 'Fuel Economy Benchmarks', 'Pre-Purchase Inspection Checklists'],
        editorial_standards: 'Objective manufacturer specification benchmarking, real-world road test verification, and certified diagnostic protocols.',
        category: 'Automotive'
      },
      'tech': {
        name: 'Ryan Kowalski',
        role: 'Software Engineer & Digital Security Analyst',
        avatar: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=240&h=240&q=85',
        bio: 'Ryan Kowalski leads technology coverage at GeneralPedia, focusing on digital security, system optimization, software tutorials, and modern consumer tech architecture. His guides provide clear, actionable walk-throughs for configuring privacy settings, securing operating systems, troubleshooting network protocols, and leveraging productivity software. Ryan is passionate about making technical digital privacy and cybersecurity accessible to everyday users without unnecessary jargon.',
        experience: '8+ years in cloud infrastructure, system optimization, software engineering, and cybersecurity defense.',
        expertise: ['Cybersecurity & Privacy Best Practices', 'Operating System Optimization', 'Software Architecture', 'Network Diagnostics', 'Digital Productivity Tools'],
        editorial_standards: 'Hands-on software reproduction, step-by-step UI verification, and defense-in-depth security best practices.',
        category: 'Tech & Digital'
      },
      'lifestyle': {
        name: 'Nora Jacobs',
        role: 'Home Living & Pet Care Editorial Specialist',
        avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=240&h=240&q=85',
        bio: 'Nora Jacobs is the lifestyle and home care editor at GeneralPedia. She focuses on practical home management, veterinarian-approved pet nutrition guides, sustainable cleaning methodologies, and indoor environmental quality. Nora works directly with reference materials and animal safety guidelines to ensure every household tip and pet food safety analysis is vetted for safety, practical efficacy, and environmental consciousness.',
        experience: '9+ years in lifestyle journalism, household management, veterinary nutrition research, and sustainable home care.',
        expertise: ['Pet Nutrition & Toxic Foods Reference', 'Sustainable Household Cleaning', 'Indoor Air Quality', 'Seasonal Home Maintenance', 'Family Living Strategies'],
        editorial_standards: 'Veterinary dietary safety cross-referencing, non-toxic household formulations, and practical implementation guidelines.',
        category: 'Home & Lifestyle'
      },
      'culture': {
        name: 'Amir Hassan',
        role: 'Cultural Historian & Sports Milestone Analyst',
        avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=240&h=240&q=85',
        bio: 'Amir Hassan heads the culture, sports, and entertainment desk at GeneralPedia. He chronicles major global sports events, cultural traditions, holiday histories, and milestones in modern entertainment. With a background in cultural historiography, Amir contextualizes current sporting tournaments and societal events within their broader historical frameworks, delivering engaging, well-researched retrospective analyses and event guides.',
        experience: '10+ years in cultural archiving, international sporting retrospectives, and entertainment journalism.',
        expertise: ['International Sporting Tournaments', 'Historical Cultural Traditions', 'Holiday Origins & Statutory Recognitions', 'Media & Entertainment Retrospectives'],
        editorial_standards: 'Primary source verification, chronological timeline mapping, and balanced cultural commentary.',
        category: 'Entertainment & Culture'
      }
    };

    function getAuthorSlug(authorName) {
      return (authorName || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    }

    function findAuthorBySlug(slug) {
      if (!slug) return null;
      const cleanSlug = slug.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      for (const cat in AUTHORS_DATA) {
        const author = AUTHORS_DATA[cat];
        if (getAuthorSlug(author.name) === cleanSlug || cat === cleanSlug) {
          return { ...author, catSlug: cat };
        }
      }
      return null;
    }

    function showAuthorProfile(catOrSlug, push = true) {
      let author = AUTHORS_DATA[catOrSlug];
      let catSlug = catOrSlug;
      if (!author) {
        const match = findAuthorBySlug(catOrSlug);
        if (match) {
          author = match;
          catSlug = match.catSlug;
        }
      }
      if (!author) {
        showHomeView(push);
        return;
      }
      hideAllViews();
      const aView = document.getElementById('author-view');
      if (aView) aView.classList.remove('hidden');

      const avatarEl = document.getElementById('author-profile-avatar');
      if (avatarEl) {
        avatarEl.src = author.avatar;
        avatarEl.alt = author.name;
      }
      const nameEl = document.getElementById('author-profile-name');
      if (nameEl) nameEl.innerText = author.name;
      const roleEl = document.getElementById('author-profile-role');
      if (roleEl) roleEl.innerText = author.role || ((author.category || 'Editorial') + ' Specialist');
      const bioEl = document.getElementById('author-profile-bio');
      if (bioEl) bioEl.innerText = author.bio;

      const expEl = document.getElementById('author-profile-experience');
      if (expEl && author.experience) expEl.innerText = author.experience;

      const tagsEl = document.getElementById('author-profile-expertise-tags');
      if (tagsEl && author.expertise) {
        tagsEl.innerHTML = author.expertise.map(t => `<span class="author-expertise-badge">${escapeHtml(t)}</span>`).join('');
      }

      const stdEl = document.getElementById('author-profile-standards');
      if (stdEl && author.editorial_standards) stdEl.innerText = author.editorial_standards;

      const authorArticles = (typeof ARTICLES_DATA !== 'undefined' ? ARTICLES_DATA : []).filter(a => 
        a.category_slug === catSlug || (a.author_name && a.author_name.toLowerCase() === author.name.toLowerCase())
      );
      
      const headingEl = document.getElementById('author-articles-heading');
      if (headingEl) headingEl.innerText = 'Articles by ' + author.name;
      const countEl = document.getElementById('author-articles-count');
      if (countEl) countEl.innerText = `${authorArticles.length} published ${authorArticles.length === 1 ? 'article' : 'articles'}`;

      const grid = document.getElementById('author-articles-grid');
      if (grid) {
        grid.innerHTML = '';
        if (authorArticles.length === 0) {
          grid.innerHTML = '<div style="grid-column: 1 / -1; padding: 48px 24px; text-align: center; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md);"><p style="font-weight: 700; font-size: 1.125rem; margin-bottom: 6px;">No articles published yet</p><p style="font-size: 0.875rem; color: var(--text-subtle);">Articles by this author will appear here as soon as they are published.</p></div>';
        } else {
          authorArticles.forEach(art => {
            grid.appendChild(createFeedCard(art));
          });
        }
      }

      const slug = getAuthorSlug(author.name);
      updateSeoMetadata(
        `${author.name} - Author Profile | GeneralPedia`,
        author.bio,
        `/author/${slug}`
      );
      if (push) history.pushState({ view: 'author', authorSlug: slug, catSlug: catSlug }, '', `/author/${slug}`);
      window.scrollTo({ top: 0, behavior: 'instant' });
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

      // If page has a visible pre-rendered static view or article view in DOM, do NOT override with home view
      const activeStatic = document.getElementById('static-view');
      const activeArticle = document.getElementById('article-view');
      if ((activeStatic && !activeStatic.classList.contains('hidden') && activeStatic.innerHTML.trim().length > 200) ||
          (activeArticle && !activeArticle.classList.contains('hidden') && activeArticle.innerHTML.trim().length > 200)) {
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
    renderCategoryTaxonomySidebar();
    handleRoute();
