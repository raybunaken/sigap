/* ── STATE ─────────────────────────────────────────────────────────────── */
let cvText = '';
let cvName = '';
let activeResultData = null; // current result shown in view-result
let activeJobData = null;    // job info (title, description) for cover letter

const API_URL = 'http://localhost:8000';

/* ── HELPERS ────────────────────────────────────────────────────────────── */
function showView(id) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  const el = document.getElementById(id);
  if (el) el.classList.add('active');
}

function setNavActive(tab) {
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const btn = document.querySelector(`.nav-btn[data-nav="${tab}"]`);
  if (btn) btn.classList.add('active');
}

function formatDate(isoStr) {
  const d = new Date(isoStr);
  return d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
}

function scoreColor(s) {
  if (s >= 70) return 'score-high';
  if (s >= 45) return 'score-mid';
  return 'score-low';
}

function scoreBarColor(s) {
  if (s >= 70) return '#22c55e';
  if (s >= 45) return '#f59e0b';
  return '#ef4444';
}

function scoreLabel(s) {
  if (s >= 70) return '<span class="status-indicator met"></span> Siap Apply!';
  if (s >= 45) return '<span class="status-indicator partial"></span> Hampir Siap';
  return '<span class="status-indicator missing"></span> Perlu Persiapan';
}

/* ── THEME ──────────────────────────────────────────────────────────────── */
// Theme is now permanently dark neon, no toggle logic needed.
/* ── HISTORY STORAGE ────────────────────────────────────────────────────── */
async function getAnalyses() {
  return new Promise(res => {
    chrome.storage.local.get(['analyses'], r => res(r.analyses || []));
  });
}

async function saveAnalysis(result, jobData) {
  const analyses = await getAnalyses();
  const entry = {
    id: Date.now(),
    analyzed_at: new Date().toISOString(),
    job_title: jobData.title,
    company: jobData.company || '',
    readiness_score: result.readiness_score,
    seniority_fit: result.seniority_fit || '',
    matched_skills: result.matched_skills || [],
    missing_skills: result.missing_skills || [],
    ats_keywords: result.ats_keywords || [],
    advice: result.advice || '',
    // store job desc for cover letter replay
    job_description: jobData.description
  };
  analyses.unshift(entry); // newest first
  // keep max 50 entries
  const trimmed = analyses.slice(0, 50);
  chrome.storage.local.set({ analyses: trimmed });
  return entry;
}

/* ── RENDER RESULT ──────────────────────────────────────────────────────── */
function renderResult(data, jobData) {
  document.getElementById('result-job-title').textContent = jobData.title;
  const companyEl = document.getElementById('result-company');
  if (companyEl) companyEl.textContent = jobData.company || '';

  // Score
  const score = data.readiness_score || 0;
  document.getElementById('result-score').textContent = score + '%';
  setTimeout(() => {
    const bar = document.getElementById('score-bar');
    bar.style.width = score + '%';
    bar.style.background = scoreBarColor(score);
  }, 100);

  document.getElementById('result-seniority').textContent = data.seniority_level || 'Semua Level';
  document.getElementById('result-level').innerHTML = scoreLabel(score);

  // Advice
  const adviceEl = document.getElementById('result-advice');
  // ── Build Structured Advice Card ──
  let statusTitle = '';
  let statusColorClass = '';
  let statusIcon = '';
  
  if (score >= 80) {
    statusTitle = 'Siap Apply!';
    statusColorClass = 'status-green';
    statusIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>';
  } else if (score >= 50) {
    statusTitle = 'Peluang Menengah.';
    statusColorClass = 'status-yellow';
    statusIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
  } else {
    statusTitle = 'Sulit Tembus.';
    statusColorClass = 'status-red';
    statusIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>';
  }

  let html = `
    <div class="advice-header ${statusColorClass}">
      <div class="advice-icon-ring">${statusIcon}</div>
      <h4>${statusTitle}</h4>
    </div>
  `;

  if (data.seniority_fit) {
    let cleanSummary = data.seniority_fit.replace(/Kesimpulan Pengalaman:\s*/i, '');
    html += `
      <div class="advice-section advice-summary">
        <div class="advice-section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          Ringkasan Profil
        </div>
        <p>${cleanSummary}</p>
      </div>
    `;
  }

  if (data.advice) {
    let cleanAdvice = data.advice.replace(/Saran:\s*/i, '');
    html += `
      <div class="advice-section advice-action">
        <div class="advice-section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
          Saran & Langkah Selanjutnya
        </div>
        <div class="advice-content">${cleanAdvice}</div>
      </div>
    `;
  }

  adviceEl.innerHTML = html;

  // Requirements Check
  const reqListEl = document.getElementById('requirements-list');
  reqListEl.innerHTML = '';
  if (data.requirements_check && data.requirements_check.length) {
    const reqListContainer = document.createElement('div');
    reqListContainer.className = 'req-list';
    
    // Sort requirements: missing -> met -> partial
    const sortedReqs = [...data.requirements_check].sort((a, b) => {
      const order = { 'missing': 1, 'met': 2, 'partial': 3 };
      return (order[a.status] || 99) - (order[b.status] || 99);
    });
    
    sortedReqs.forEach(req => {
      const item = document.createElement('div');
      item.className = 'req-item';
      
      const header = document.createElement('div');
      header.className = 'req-header';
      
      const icon = document.createElement('div');
      icon.className = `req-status-icon ${req.status}`;
      
      if (req.status === 'met') {
        icon.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>';
      } else if (req.status === 'partial') {
        icon.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>';
      } else {
        icon.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
      }
      
      const title = document.createElement('div');
      title.className = 'req-title';
      title.textContent = req.req;
      
      header.appendChild(icon);
      header.appendChild(title);
      item.appendChild(header);
      
      if (req.detail) {
        const detail = document.createElement('div');
        detail.className = 'req-detail';
        detail.textContent = req.detail;
        item.appendChild(detail);
      }
      
      reqListContainer.appendChild(item);
    });
    reqListEl.appendChild(reqListContainer);
  } else {
    reqListEl.innerHTML = '<span class="empty-chips">Tidak ada data requirements.</span>';
  }

  // Matched skills
  const matchedEl = document.getElementById('result-matched');
  if (matchedEl) {
    matchedEl.innerHTML = '';
    if (data.matched_skills && data.matched_skills.length) {
      data.matched_skills.forEach(s => {
        const chip = document.createElement('span');
        chip.className = 'chip green';
        chip.textContent = s;
        matchedEl.appendChild(chip);
      });
    } else {
      matchedEl.innerHTML = '<span class="empty-chips">Belum ada skill spesifik yang relevan.</span>';
    }
  }

  // Missing skills
  const missingEl = document.getElementById('result-missing');
  if (missingEl) {
    missingEl.innerHTML = '';
    if (data.missing_skills && data.missing_skills.length) {
      data.missing_skills.forEach(s => {
        const chip = document.createElement('span');
        chip.className = 'chip red';
        chip.textContent = s;
        missingEl.appendChild(chip);
      });
    } else {
      missingEl.innerHTML = '<span class="empty-chips">Hebat! Semua skill teknis utama sudah ada 🎉</span>';
    }
  }

  // ATS keywords — click to copy
  const atsEl = document.getElementById('result-ats');
  atsEl.innerHTML = '';
  if (data.ats_keywords && data.ats_keywords.length) {
    data.ats_keywords.forEach(kw => {
      const chip = document.createElement('span');
      chip.className = 'ats-chip';
      chip.textContent = kw;
      chip.title = 'Klik untuk salin';
      chip.addEventListener('click', () => {
        navigator.clipboard.writeText(kw).then(() => {
          chip.classList.add('copied');
          chip.textContent = '✓ ' + kw;
          setTimeout(() => { chip.classList.remove('copied'); chip.textContent = kw; }, 1500);
        });
      });
      atsEl.appendChild(chip);
    });
  } else {
    atsEl.innerHTML = '<span class="hint-text">Tidak ada keyword spesifik ditemukan.</span>';
  }

  showView('view-result');
}

/* ── RENDER HISTORY ─────────────────────────────────────────────────────── */
async function renderHistory() {
  const analyses = await getAnalyses();
  const historyList = document.getElementById('history-list');
  const insightWrap = document.getElementById('history-insight-wrap');
  const listLabel = document.getElementById('history-list-label');

  insightWrap.innerHTML = '';
  historyList.innerHTML = '';

  if (analyses.length === 0) {
    historyList.innerHTML = `
      <div class="empty-state">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
        </svg>
        <p>Belum ada riwayat analisis.<br>Mulai dari tab <strong>Beranda</strong>!</p>
      </div>`;
    return;
  }

  // Insight: count missing skill frequency
  const missingCount = {};
  analyses.forEach(a => {
    (a.missing_skills || []).forEach(s => {
      missingCount[s] = (missingCount[s] || 0) + 1;
    });
  });
  const topGaps = Object.entries(missingCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  const maxCount = topGaps[0]?.[1] || 1;
  const avgScore = Math.round(analyses.reduce((s, a) => s + a.readiness_score, 0) / analyses.length);

  // Insight card
  if (topGaps.length > 0) {
    const insightHtml = `
      <div class="insight-card">
        <div class="insight-title">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          Insight dari ${analyses.length} Lowongan · Avg Score ${avgScore}%
        </div>
        <p class="hint-text" style="margin-bottom: 10px;">Skill yang paling sering kurang dari CV-mu:</p>
        ${topGaps.map(([skill, count]) => `
          <div class="insight-stat">
            <span>${skill}</span>
            <div class="gap-bar"><div class="gap-bar-fill" style="width:${Math.round(count/maxCount*100)}%"></div></div>
            <span class="gap-count">${count}x</span>
          </div>
        `).join('')}
      </div>`;
    insightWrap.innerHTML = insightHtml;
  }

  listLabel.textContent = `${analyses.length} Lowongan Dianalisis`;

  // Job cards
  analyses.forEach(entry => {
    const colorClass = scoreColor(entry.readiness_score);
    const barColor = scoreBarColor(entry.readiness_score);
    const card = document.createElement('div');
    card.className = 'history-job-card';
    card.innerHTML = `
      <div class="history-job-info">
        <div class="history-job-title">${entry.job_title}</div>
        <div class="history-job-company">${entry.company || '—'}</div>
        <div class="history-job-bar">
          <div class="history-job-bar-fill" style="width:${entry.readiness_score}%; background:${barColor};"></div>
        </div>
        <div class="history-job-date">${formatDate(entry.analyzed_at)}</div>
      </div>
      <div class="history-job-score ${colorClass}">${entry.readiness_score}%</div>`;

    card.addEventListener('click', () => {
      // Re-render the result from history
      activeResultData = entry;
      activeJobData = { title: entry.job_title, company: entry.company, description: entry.job_description };
      renderResult(entry, activeJobData);
    });

    historyList.appendChild(card);
  });
}

/* ── MAIN INIT ──────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', async () => {

  // Setup pdf.js worker
  if (typeof window.pdfjsLib !== 'undefined') {
    window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'pdf.worker.min.js';
  }

  // Load saved CV
  chrome.storage.local.get(['cvText', 'cvName'], r => {
    if (r.cvText) {
      cvText = r.cvText;
      cvName = r.cvName || 'CV.pdf';
      activateMain();
    }
  });

  function activateMain() {
    document.getElementById('cv-name-home').textContent = cvName;
    document.getElementById('bottom-nav').style.display = 'flex';
    showView('view-home');
    setNavActive('home');
    loadLastCard();
  }

  async function loadLastCard() {
    const analyses = await getAnalyses();
    if (analyses.length === 0) return;
    const last = analyses[0];
    const wrap = document.getElementById('last-analysis-wrap');
    const card = document.getElementById('last-analysis-card');
    const colorClass = scoreColor(last.readiness_score);
    const barColor = scoreBarColor(last.readiness_score);
    card.innerHTML = `
      <div class="history-job-info">
        <div class="history-job-title">${last.job_title}</div>
        <div class="history-job-company">${last.company || '—'}</div>
        <div class="history-job-bar">
          <div class="history-job-bar-fill" style="width:${last.readiness_score}%; background:${barColor};"></div>
        </div>
        <div class="history-job-date">${formatDate(last.analyzed_at)}</div>
      </div>
      <div class="history-job-score ${colorClass}">${last.readiness_score}%</div>`;
    card.addEventListener('click', () => {
      activeResultData = last;
      activeJobData = { title: last.job_title, company: last.company, description: last.job_description };
      renderResult(last, activeJobData);
    });
    wrap.style.display = 'block';
  }

  // ── CV Upload
  const cvUploadInput = document.getElementById('cv-upload');
  const saveCvBtn = document.getElementById('save-cv-btn');
  const setupFilename = document.getElementById('setup-filename');
  const setupStatus = document.getElementById('setup-status');

  cvUploadInput.addEventListener('change', () => {
    if (cvUploadInput.files.length > 0) {
      setupFilename.textContent = '📎 ' + cvUploadInput.files[0].name;
      saveCvBtn.disabled = false;
    }
  });

  saveCvBtn.addEventListener('click', async () => {
    const file = cvUploadInput.files[0];
    if (!file) return;
    saveCvBtn.disabled = true;
    setupStatus.textContent = 'Mengekstrak teks dari CV...';

    try {
      let text = '';
      if (file.name.endsWith('.txt')) {
        text = await file.text();
      } else if (file.name.endsWith('.pdf')) {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          text += content.items.map(item => item.str).join(' ') + '\n';
        }
      } else {
        throw new Error('Format tidak didukung');
      }

      if (text.trim().length < 50) throw new Error('Teks CV terlalu pendek. Pastikan PDF bukan gambar scan.');

      chrome.storage.local.set({ cvText: text, cvName: file.name }, () => {
        cvText = text;
        cvName = file.name;
        activateMain();
      });
    } catch (err) {
      setupStatus.textContent = '⚠ ' + err.message;
      saveCvBtn.disabled = false;
    }
  });

  // Change CV
  document.getElementById('change-cv-btn').addEventListener('click', () => {
    chrome.storage.local.remove(['cvText', 'cvName'], () => {
      cvText = ''; cvName = '';
      document.getElementById('bottom-nav').style.display = 'none';
      setupFilename.textContent = '';
      setupStatus.textContent = '';
      saveCvBtn.disabled = true;
      cvUploadInput.value = '';
      showView('view-setup');
    });
  });

  // ── Bottom Nav
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.nav;
      setNavActive(tab);
      if (tab === 'home') showView('view-home');
      if (tab === 'history') { renderHistory(); showView('view-history'); }
    });
  });

  // ── Analyze Button
  document.getElementById('analyze-btn').addEventListener('click', async () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const analyzeStatus = document.getElementById('analyze-status');

    analyzeBtn.disabled = true;
    analyzeStatus.textContent = '';

    showView('view-loading');
    document.getElementById('loading-step').textContent = 'Menyedot data lowongan...';
    document.getElementById('loading-sub').textContent = 'Membaca halaman lowongan';

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // Allow LinkedIn, Glints, JobStreet, Kalibrr, TechInAsia, Kintsugi, etc.
    const validDomains = ['linkedin.com', 'glints.com', 'jobstreet', 'kalibrr', 'techinasia', 'kintsugi', 'mycareersfuture'];
    const isValid = validDomains.some(d => tab.url.includes(d));
    
    if (!isValid) {
      showView('view-home');
      analyzeStatus.textContent = '⚠ Buka halaman lowongan kerja (LinkedIn/Glints/JobStreet dll).';
      analyzeBtn.disabled = false;
      return;
    }

    chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ['content.js'] }, async (results) => {
      const scraped = results?.[0]?.result || {};
      const jobData = {
        title: scraped.title || '',
        company: scraped.company || '',
        description: scraped.description || ''
      };

      // Block if no description at all AND no title
      const GARBAGE_TITLES = ['0 notifications', 'notifications', 'messaging'];
      const titleIsGarbage = !jobData.title || 
        jobData.title.length < 3 || 
        GARBAGE_TITLES.some(g => jobData.title.toLowerCase().includes(g));

      if (titleIsGarbage && !jobData.description) {
        showView('view-home');
        analyzeStatus.textContent = '⚠ Klik langsung pada salah satu lowongan di sebelah kiri dulu.';
        analyzeBtn.disabled = false;
        return;
      }

      // If title is garbage but we have description, use fallback title
      if (titleIsGarbage) jobData.title = 'Lowongan yang Dianalisis';

      // Warn but continue if description is short
      if (jobData.description.length < 100) {
        document.getElementById('loading-sub').textContent = 'Deskripsi singkat, AI akan berusaha semaksimal mungkin...';
      }

      document.getElementById('loading-step').textContent = 'Menganalisis dengan AI...';
      document.getElementById('loading-sub').textContent = 'Membandingkan CV dengan Job Description';

      try {
        const res = await fetch(`${API_URL}/api/analyze-job`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            cv_text: cvText,
            job_title: jobData.title,
            job_description: jobData.description
          })
        });
        const data = await res.json();

        if (data.error) throw new Error(data.error);

        activeResultData = data;
        activeJobData = jobData;

        // Only save if title is meaningful
        if (jobData.title !== 'Lowongan yang Dianalisis') {
          await saveAnalysis(data, jobData);
        }

        renderResult(data, jobData);
        analyzeBtn.disabled = false;
      } catch (err) {
        showView('view-home');
        analyzeStatus.textContent = '⚠ Error: ' + err.message;
        analyzeBtn.disabled = false;
      }
    });
  });

  // ── Tabs in Result View
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tabId = btn.dataset.tab;
      document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
      document.getElementById('tab-' + tabId).classList.remove('hidden');
    });
  });

  // ── Back buttons
  document.getElementById('back-to-home-btn').addEventListener('click', () => {
    showView('view-home');
    setNavActive('home');
  });
  document.getElementById('back-to-result-btn').addEventListener('click', () => {
    showView('view-result');
  });

  // ── Cover Letter
  document.getElementById('cover-letter-btn').addEventListener('click', async () => {
    if (!activeResultData || !activeJobData) return;
    showView('view-cover-letter');
    document.getElementById('cl-loading').style.display = 'flex';
    document.getElementById('cl-content').style.display = 'none';

    try {
      const res = await fetch(`${API_URL}/api/generate-cover-letter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cv_text: cvText,
          job_title: activeJobData.title,
          job_description: activeJobData.description || '',
          company_name: activeJobData.company || ''
        })
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      document.getElementById('cl-text').value = data.cover_letter;
      document.getElementById('cl-loading').style.display = 'none';
      document.getElementById('cl-content').style.display = 'flex';
    } catch (err) {
      document.getElementById('cl-loading').innerHTML = `<p style="color:#ef4444">⚠ ${err.message}</p><button class="btn-ghost" id="cl-retry">Coba Lagi</button>`;
      document.getElementById('cl-retry')?.addEventListener('click', () => document.getElementById('cover-letter-btn').click());
    }
  });

  // ── Copy Cover Letter
  document.getElementById('copy-cl-btn').addEventListener('click', () => {
    const text = document.getElementById('cl-text').value;
    navigator.clipboard.writeText(text).then(() => {
      const btn = document.getElementById('copy-cl-btn');
      const orig = btn.innerHTML;
      btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Tersalin!';
      setTimeout(() => { btn.innerHTML = orig; }, 2000);
    });
  });

});
