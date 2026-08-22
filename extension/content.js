(() => {
  const url = window.location.href;
  const isLinkedIn = url.includes('linkedin.com');
  const isJobStreet = url.includes('jobstreet') || url.includes('jobsdb') || url.includes('seek');
  const isGlints = url.includes('glints.com');

  let title = '';
  let company = '';
  let description = '';
  let panel = document;

  if (isLinkedIn) {
    // ── LINKEDIN ──────────────────────────────────────────────────────────
    const panelCandidates = [
      document.querySelector('.jobs-search__job-details--container'),
      document.querySelector('.scaffold-layout__detail'),
      document.querySelector('.jobs-details'),
      document.querySelector('[data-view-name="job-details"]'),
      document.querySelector('.job-view-layout'),
      document.querySelector('main'),
    ].filter(Boolean);
    panel = panelCandidates[0] || document;

    const titleTry = [
      '.job-details-jobs-unified-top-card__job-title h1',
      '.job-details-jobs-unified-top-card__job-title a',
      '.job-details-jobs-unified-top-card__job-title',
      '.jobs-unified-top-card__job-title h1',
      '.jobs-unified-top-card__job-title',
      '.topcard__title',
      '.top-card-layout__title',
      'h1.t-24',
      'h1',
    ];
    for (const s of titleTry) {
      const el = document.querySelector(s);
      if (!el) continue;
      const t = el.innerText.trim();
      if (t.length > 3 && t.length < 200 && !/^\d+$/.test(t) && !/notification|message/i.test(t)) {
        title = t; break;
      }
    }

    const companyTry = [
      '.job-details-jobs-unified-top-card__company-name a',
      '.job-details-jobs-unified-top-card__company-name',
      '.jobs-unified-top-card__company-name a',
      '.jobs-unified-top-card__company-name',
      '.jobs-details-top-card__company-info a',
      '.topcard__org-name-link',
      '.topcard__flavor--black-link',
      '.job-details-jobs-unified-top-card__primary-description-container a.app-aware-link',
      'a.app-aware-link[href*="/company/"]'
    ];
    for (const s of companyTry) {
      const el = (panel || document).querySelector(s);
      if (el) { const t = el.innerText.trim(); if (t.length > 1) { company = t; break; } }
    }
    if (!company) {
      const primaryDesc = (panel || document).querySelector('.job-details-jobs-unified-top-card__primary-description-container');
      if (primaryDesc) {
        const parts = (primaryDesc.innerText || '').split(/[·•|]/);
        if (parts.length > 0 && parts[0].trim().length > 1) company = parts[0].trim();
      }
    }
    if (!company) {
      const subtitle = (panel || document).querySelector('.jobs-unified-top-card__subtitle-primary-grouping');
      if (subtitle) {
        const parts = (subtitle.innerText || '').split(/[·•|]/);
        if (parts.length > 0 && parts[0].trim().length > 1) company = parts[0].trim();
      }
    }
    if (!company) {
      const companyLink = (panel || document).querySelector('a[href*="/company/"]');
      if (companyLink && companyLink.innerText.trim().length > 1) company = companyLink.innerText.trim();
    }

    const descTry = [
      '#job-details',
      'article',
      '.jobs-description-content__text',
      '.jobs-description__content',
      '.jobs-description',
      '.description__text',
      '.show-more-less-html__markup',
      '.core-section-container__content',
      '.jobs-box__html-content',
    ];
    for (const s of descTry) {
      const el = document.querySelector(s);
      if (el) { const t = el.innerText.trim(); if (t.length > 80) { description = t; break; } }
    }
    
    // Ultimate Fallback: Jika tidak ketemu div spesifik, ambil seluruh teks dari panel utama
    if (!description || description.length < 30) {
      if (panel) {
        description = panel.innerText.trim();
      } else {
        description = document.body.innerText.trim();
      }
      // Halaman utuh bisa 50rb+ karakter (nav, sidebar, rekomendasi).
      // Batasi agar payload ke API tetap ringan dan relevan.
      if (description.length > 20000) description = description.slice(0, 20000);
    }


  } else if (isJobStreet) {
    // ── JOBSTREET (SEEK) ──────────────────────────────────────────────────
    const titleEl = document.querySelector('[data-automation="job-detail-title"]');
    if (titleEl) title = titleEl.innerText.trim();
    
    const compEl = document.querySelector('[data-automation="advertiser-name"]');
    if (compEl) company = compEl.innerText.trim();
    
    const descEl = document.querySelector('[data-automation="jobAdDetails"]');
    if (descEl) description = descEl.innerText.trim();

  } else {
    // ── GENERIC PLATFORMS (GLINTS, KALIBRR, ETC) ───────────────
    // Title
    const h1s = Array.from(document.querySelectorAll('h1'));
    for (const h1 of h1s) {
      const t = h1.innerText.trim();
      if (t.length > 3 && t.length < 150) { title = t; break; }
    }

    // Company
    const compLinks = Array.from(document.querySelectorAll('a')).filter(a => {
      const h = a.href.toLowerCase();
      const txt = a.innerText.trim();
      // Avoid generic texts like "selengkapnya" or "more info"
      return (h.includes('/company/') || h.includes('/employer/') || h.includes('/companies/')) && 
             txt.length > 2 && txt.length < 50 && !txt.toLowerCase().includes('selengkapnya');
    });
    if (compLinks.length > 0) {
      company = compLinks[0].innerText.trim();
    } else {
      const h2s = Array.from(document.querySelectorAll('h2, h3, h4'));
      for (const h of h2s) {
        const t = h.innerText.trim();
        if (t.length > 2 && t.length < 60 && !t.match(/job|responsibilit|requirement|qualification|about/i)) {
          company = t; break;
        }
      }
    }
  }

  // ── FALLBACKS FOR ANY PLATFORM ─────────────────────────────────────────
  if (!title) {
    const pt = document.title.split(/[-|]/)[0].trim();
    if (pt && pt.length > 2) title = pt;
    if (!title) title = 'Posisi Pekerjaan';
  }

  // Nuclear fallback for Description (works on almost all sites)
  if (!description || description.length < 100) {
    const allEls = document.querySelectorAll('div, section, article, p, main');
    let best = '';
    for (const el of allEls) {
      if (el.children.length > 30) continue; // Skip huge wrapper elements
      const t = (el.innerText || '').trim();
      if (t.length > best.length && t.length > 150 &&
          /requirement|qualification|responsibilit|tanggung jawab|kualifikasi|syarat|skill|experience|about the (job|role)/i.test(t)) {
        best = t;
      }
    }
    if (best.length > description.length) description = best;
  }
  
  if (!description && panel && panel !== document) {
    description = panel.innerText.slice(0, 5000).trim();
  }
  if (!description) {
    description = document.body.innerText.slice(0, 5000).trim(); // Last ditch
  }

  return { title, company, description };
})();
