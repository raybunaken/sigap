# Skillsy Copilot — Project Summary

## Overview

**Skillsy Copilot** is an AI-powered Chrome Extension that acts as a career intelligence engine for job seekers. It automatically scrapes job postings from LinkedIn and JobStreet, compares them against the user's uploaded CV (PDF), and delivers an instant ATS (Applicant Tracking System) compatibility score along with a detailed skill gap analysis — all powered by a large language model running on a cloud backend.

**Tagline:** *Hack Your Career. Bypass HR Filters.*

| Detail | Value |
|---|---|
| **Product Type** | Chrome Extension + Landing Page + API Backend |
| **Domain** | [https://skillsy.my.id](https://skillsy.my.id) |
| **Repository** | [github.com/raybunaken/sigap](https://github.com/raybunaken/sigap) |
| **Founder** | Dzaky Rayssa Buntoro |
| **Stage** | MVP (Minimum Viable Product) — Functional & Deployed |

---

## Problem Statement

Fresh graduates and job seekers in Indonesia (and globally) face a critical challenge: **they have no way of knowing whether their CV actually matches what recruiters and ATS systems are looking for** before they hit "Apply." This leads to:

- Hundreds of rejected applications with zero feedback.
- Wasted time applying to jobs where their skills don't match.
- No visibility into which specific skills they are missing.
- Inability to tailor their CV to each job posting efficiently.

---

## Solution

Skillsy Copilot solves this by sitting directly inside the user's browser. While browsing job listings on LinkedIn or JobStreet, the user simply:

1. **Opens any job posting** on LinkedIn or JobStreet.
2. **Uploads their CV** (PDF) via the Skillsy side panel.
3. **Clicks "Scan"** — the AI instantly returns:
   - **Match Score (%)** — How well the CV aligns with the job requirements.
   - **Skill Level Assessment** (Entry / Mid / Senior Level).
   - **Skills Breakdown** — Which skills the user has vs. which are missing.
   - **ATS Keywords** — Critical keywords the CV must contain to pass automated filters.
   - **Actionable Advice** — Specific recommendations to improve the CV for that particular job.

---

## Tech Stack

### Frontend — Chrome Extension
| Component | Technology |
|---|---|
| UI Framework | Vanilla HTML/CSS/JS (Manifest V3) |
| PDF Parsing | pdf.js (Mozilla) — client-side CV text extraction |
| Job Scraping | Custom DOM scraper (`content.js`) for LinkedIn & JobStreet |
| Side Panel | Chrome Side Panel API for seamless UX |
| Design System | Neon Glassmorphism (dark theme, green accents) |

### Backend — API Server
| Component | Technology |
|---|---|
| Framework | Python FastAPI |
| AI Model | Llama 3.3 70B (via Groq API) |
| Hosting | Vercel (Serverless Functions) |
| Endpoints | 8 API routes (see below) |

### Landing Page
| Component | Technology |
|---|---|
| Framework | Static HTML/CSS/JS |
| Hosting | Vercel (via GitHub auto-deploy) |
| Domain | skillsy.my.id (custom domain) |
| Design | Dark Glassmorphism, responsive, bilingual (EN/ID) |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze` | General CV analysis |
| `POST` | `/analyze-job` | **Core feature** — Compare CV against a specific job posting |
| `POST` | `/parse-cv` | Extract structured data from uploaded CV (PDF) |
| `POST` | `/parse-cv-text` | Parse raw CV text into structured format |
| `POST` | `/chat` | General AI chat |
| `POST` | `/chat-advisory` | Career advisory chatbot |
| `POST` | `/generate-cover-letter` | Auto-generate a tailored cover letter |
| `POST` | `/waitlist` | Collect waitlist signups (email) |

---

## Key Features (Current — v1.0)

- **Instant ATS Score Analysis** — Real-time percentage match between CV and job posting.
- **Missing Skills Detection (Skill Gap)** — AI identifies exactly which skills the user lacks.
- **ATS Keyword Extraction** — Shows which keywords must appear in the CV to pass automated filters.
- **Direct Integration with LinkedIn & JobStreet** — Scrapes job data automatically from the page.
- **PDF CV Upload & Parsing** — Client-side PDF processing (no CV data stored on server).
- **Bilingual Landing Page** — English (primary, for sponsors) and Indonesian toggle.
- **Waitlist System** — Email collection modal with backend logging.
- **Cover Letter Generator** — AI-generated cover letter tailored to job + CV.

---

## Roadmap

### Phase 1 — Current (August 2026) ✅
- [x] Chrome Extension MVP (functional)
- [x] AI-powered job analysis (Llama 3.3 70B via Groq)
- [x] Landing page with waitlist ([skillsy.my.id](https://skillsy.my.id))
- [x] Production deployment on Vercel
- [x] LinkedIn & JobStreet scraping support

### Phase 2 — End of Year 2026 (Beta & Public Launch)
- [ ] Supabase integration for user accounts & waitlist database
- [ ] Multi-platform scraping (Glints, Kalibrr, Indeed)
- [ ] Auto-Tailor CV feature (AI rewrites CV sections to match job)
- [ ] User history & saved analyses
- [ ] Beta download distribution to waitlist subscribers


- [ ] Chrome Web Store publication
- [ ] Premium tier (unlimited scans, priority AI model)
- [ ] Dashboard for tracking application history
- [ ] AI Interview Preparation module

---

## Sponsor & Infrastructure Pipeline

| Provider | Status | Benefit |
|---|---|---|
| **Alibaba Cloud** | Catalyst application submitted; account verification pending | Free trial credits, potential incubator support |
| **AWS** | Applied for AWS Activate; manual verification call scheduled (Monday) | Up to $1,000 in credits |
| **Google Cloud** | Google for Startups application — billing domain mismatch (action required) | Up to $100K in credits |
| **Groq** | Active & in use | Free API access to Llama 3.3 70B (current AI engine) |

### Next Targets
- Microsoft for Startups Founders Hub
- GitHub Student Developer Pack
- Supabase (free database)
- 1000 Startup Digital (Kominfo)
- Indigo by Telkom Indonesia

---

## Business Model (Planned)

| Tier | Price | Features |
|---|---|---|
| **Free** | Rp 0 | 3 scans/day, basic skill gap report |
| **Pro** | ~Rp 49K/month | Unlimited scans, cover letter generator, ATS keyword optimizer |
| **Enterprise** | Custom | API access for recruitment platforms, bulk CV screening |

---

## Competitive Advantage

1. **Browser-native** — No need to copy-paste job descriptions. Skillsy reads the page directly.
2. **Real-time** — Analysis happens in seconds, not minutes.
3. **AI-first** — Powered by Llama 3.3 70B, one of the most capable open-source LLMs.
4. **Privacy-focused** — CV is parsed client-side; only extracted text is sent to the API.
5. **Localized** — Built with deep understanding of the Indonesian job market (JobStreet, LinkedIn Indonesia).

---

## Repository Structure

```
Sigap/
├── api/
│   └── index.py              # FastAPI backend (8 endpoints, Groq AI)
├── extension/
│   ├── manifest.json          # Chrome Extension config (Manifest V3)
│   ├── popup.html             # Side panel UI
│   ├── popup.css              # Neon glassmorphism styling
│   ├── popup.js               # Core logic (CV upload, API calls, UI state)
│   ├── content.js             # DOM scraper for LinkedIn & JobStreet
│   ├── background.js          # Service worker (side panel trigger)
│   ├── pdf.min.js             # PDF.js library
│   └── pdf.worker.min.js      # PDF.js web worker
├── index.html                 # Landing page (skillsy.my.id)
├── screenshot.png             # Extension screenshot for landing page
├── vercel.json                # Vercel deployment config
├── requirements.txt           # Python dependencies
└── .env                       # API keys (Groq)
```

---

## Contact

| | |
|---|---|
| **Founder** | Dzaky Rayssa Buntoro |
| **Phone** | +62 895-2027-6115 |
| **Email** | raybunaken@gmail.com |
| **GitHub** | [github.com/raybunaken](https://github.com/raybunaken) |
| **Website** | [skillsy.my.id](https://skillsy.my.id) |
