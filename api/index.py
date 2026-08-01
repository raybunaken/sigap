"""
SIGAP — AI Advisor Skill Gap untuk Fresh Grad Indonesia
Backend: FastAPI + Groq (Llama 3.3)
Jalankan: python api.py
"""

import os, json, logging, asyncio, re, pathlib
from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import httpx

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sigap")

# ── LOAD SCRAPED DATA (dari scraper.py) ───────────────────────────────────
def load_scraped_data() -> dict:
    """
    Load hasil scraping Jobstreet kalau ada.
    Dipakai untuk enrich knowledge base dengan data real.
    """
    scraped_file = pathlib.Path(__file__).parent / "knowledge_base_scraped.json"
    if scraped_file.exists():
        try:
            with open(scraped_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"✓ Loaded scraped data: {len(data.get('jobs', {}))} jobs")
            return data.get("jobs", {})
        except Exception as e:
            logger.warning(f"Gagal load scraped data: {e}")
    return {}

SCRAPED_JOBS = load_scraped_data()

from api.knowledge_base import (
    PEKERJAAN_DATABASE, KURSUS_GRATIS, ROADMAP,
    STATISTIK, get_system_prompt,
    get_kursus_for_skill, get_gaji_by_experience,
    SKILL_SYNONYMS, normalize_skill, skills_match,
)

# ── CONFIG ────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = "llama-3.3-70b-versatile"
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"

# ── SKILL PATTERNS (satu sumber, untuk regex fallback CV parsing) ─────────
SKILL_PATTERNS = [
    "Python", "JavaScript", "TypeScript", "Java", "Go", "PHP", "Kotlin", "Dart", "SQL", "R",
    "React", "Vue", "Angular", "Flutter", "Node.js", "FastAPI", "Django", "Laravel",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas",
    "Tableau", "Power BI", "Google Analytics", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Git", "Linux", "Figma", "Excel",
    "REST API", "Microservices", "Agile", "Scrum", "Spark", "Kafka", "Airflow",
    "SPSS", "Market Research", "Data Storytelling", "Financial Modeling", "Akuntansi",
    "SEO", "Google Ads", "Meta Ads", "Copywriting", "Content Planning", "WordPress",
    "Adobe Illustrator", "Adobe Photoshop", "Premiere Pro", "CapCut", "Canva",
    "Microsoft Office", "Google Workspace", "Hootsuite", "Hubspot",
    "Problem Solving", "Komunikasi", "Presentasi", "Public Speaking", "Negosiasi",
    "Teamwork", "Manajemen Waktu", "Kepemimpinan", "Analitis", "Berpikir Kritis",
    "Adaptif", "Kreatif", "Kolaborasi", "Detail-oriented", "Manajemen Proyek",
]

# ── APP SETUP ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    if GROQ_API_KEY:
        logger.info(f"✓ SIGAP ready! Model: {GROQ_MODEL}")
    else:
        logger.warning("⚠ GROQ_API_KEY tidak ditemukan! Set di file .env")
    yield

app = FastAPI(
    title="SIGAP — AI Advisor Skill Gap",
    description="Sistem Identifikasi GAP Skill untuk Karir fresh grad Indonesia",
    version="1.0.0",
    lifespan=lifespan,
)

# ── VERCEL PATH REWRITE FIX ──
@app.middleware("http")
async def fix_vercel_path(request: Request, call_next):
    vpath = request.query_params.get("vpath")
    if vpath:
        # Override path in ASGI scope
        request.scope["path"] = f"/api/{vpath}"
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# ── SCHEMAS ───────────────────────────────────────────────────────────────
class ProfilUser(BaseModel):
    pendidikan:   str
    jurusan:      str
    skill:        List[str] = []
    target_job:   str = ""
    pengalaman:   str = "Fresh grad / belum ada"
    lokasi:       str = "Jakarta"
    cv_summary:   str = ""
    # Fields dari frontend setelah /analyze — supaya /chat tidak perlu re-compute gap
    readiness:    Optional[float] = None
    skill_kurang: List[str] = []
    job_target:   str = ""

class ChatMessage(BaseModel):
    role:    str
    content: str

class ChatRequest(BaseModel):
    message:      str
    history:      List[ChatMessage] = []
    profil:       Optional[ProfilUser] = None

class CVTextRequest(BaseModel):
    text: str

# ── GROQ API (satu entry point untuk semua panggilan) ─────────────────────
async def groq_request(
    messages: list,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    timeout: int = 20,
    response_format: Optional[dict] = None
) -> Optional[str]:
    """
    Satu-satunya fungsi yang panggil Groq API.
    Return content string, atau None kalau gagal.
    Sudah include retry otomatis untuk 429 rate limit.
    """
    if not GROQ_API_KEY:
        return None
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if response_format:
        payload["response_format"] = response_format

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.post(GROQ_URL, headers=headers, json=payload)
                if res.status_code == 429:
                    wait = 2 ** attempt
                    logger.warning(f"Groq 429, retry {attempt+1} after {wait}s...")
                    await asyncio.sleep(wait)
                    continue
                data = res.json()
                if "choices" not in data:
                    logger.error(f"Groq no choices: {data}")
                    return None
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Groq error (attempt {attempt+1}): {e}")
            if attempt < 2:
                await asyncio.sleep(1)
    return None

# ── SKILL EXTRACTION HELPERS ─────────────────────────────────────────────
def regex_extract_skills(text: str) -> list:
    """Extract skills dari teks menggunakan word-boundary regex."""
    found = []
    for s in SKILL_PATTERNS:
        pattern = r"\b" + re.escape(s) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            found.append(s)
    return found

# ── TRANSFERABLE SKILL GROUPS ─────────────────────────────────────────────
# Skill yang paradigmanya sama walau nama/tech stack beda.
# User yang punya skill A mendapat 50% credit untuk skill B dalam grup yang sama.
TRANSFERABLE_GROUPS = [
    # Backend languages — PHP, Python, Node.js, Java semua paradigma sama
    {"backend language", "python", "node.js", "php", "laravel", "java", "go", "django",
     "fastapi", "express", "ruby", "spring", "asp.net", "kotlin"},
    # SQL databases
    {"sql", "mysql", "postgresql", "sqlite", "oracle", "microsoft sql server"},
    # NoSQL databases
    {"mongodb", "firestore", "dynamodb", "redis", "cassandra"},
    # Frontend frameworks — React, Vue, Angular paradigma sama
    {"react", "react.js", "vue", "vue.js", "angular", "svelte"},
    # Mobile — Flutter, React Native, Kotlin paradigma sama
    {"flutter", "react native", "kotlin", "swift", "android sdk"},
    # Cloud platforms
    {"aws", "gcp", "azure", "cloud computing", "google cloud"},
    # Design tools
    {"figma", "adobe xd", "sketch", "invision"},
    # Office/spreadsheet
    {"excel", "google sheets", "microsoft excel", "spreadsheet"},
    # Version control
    {"git", "github", "gitlab", "bitbucket", "version control"},
    # REST / API
    {"restful api", "rest api", "api development", "web service", "graphql",
     "laravel", "django", "fastapi", "express", "spring boot"},
    # Containers
    {"docker", "kubernetes", "podman", "container"},
    # CI/CD
    {"ci cd pipelines", "github actions", "jenkins", "gitlab ci", "travis ci"},
    # ML frameworks
    {"tensorflow", "pytorch", "scikit-learn", "keras", "machine learning"},
    # Data viz
    {"tableau", "power bi", "looker", "matplotlib", "seaborn", "data visualization"},
]

def is_transferable(user_skill: str, target_skill: str) -> bool:
    """Cek apakah user_skill dan target_skill ada di grup transferable yang sama."""
    u = normalize_skill(user_skill)
    t = normalize_skill(target_skill)
    for group in TRANSFERABLE_GROUPS:
        u_in = any(u == g or u in g or g in u for g in group)
        t_in = any(t == g or t in g or g in u for g in group)  # intentional: match broad
        t_in = any(t == g or t in g or g in t for g in group)
        if u_in and t_in:
            return True
    return False

async def extract_skills_from_text(text: str, include_summary: bool = False) -> dict:
    """
    Hybrid skill extraction: Groq AI + regex fallback.
    Prompt diperbaiki agar Groq infer skill implisit dari project & pengalaman.
    Dipakai oleh /parse-cv dan /parse-cv-text.
    """
    result = {"skills": [], "cv_summary": "", "method": "regex_fallback"}

    if not text or len(text.strip()) < 30:
        return result

    # Try Groq AI first
    if GROQ_API_KEY:
        summary_instruction = ""
        summary_example = ""
        if include_summary:
            summary_instruction = """\n2. "cv_summary": ringkasan singkat dalam 2-3 kalimat tentang:
   - Jabatan/posisi terakhir dan berapa lama
   - Industri/bidang pengalaman
   - Pencapaian atau hal menonjol dari CV"""
            summary_example = ',\n  "cv_summary": "Lulusan S1 Manajemen dengan pengalaman 2 tahun sebagai Admin E-Commerce..."'

        prompt = f"""Kamu adalah CV parser expert Indonesia. Baca CV berikut dan extract SEMUA skill.

ATURAN PENTING — Inference dari konteks project:
- Jika ada "Laravel" atau "Django" atau "FastAPI" → tambahkan "RESTful API" dan "Backend Development"
- Jika ada "React" atau "Vue" → tambahkan "Frontend Development"
- Jika ada project deploy ke server → tambahkan "Git"
- Jika ada "MySQL" atau "PostgreSQL" → tambahkan "SQL"
- Jika ada "monitoring sistem" / "dashboard" → tambahkan "Data Visualization"
- Jika ada magang/kerja nyata → tambahkan soft skill: "Teamwork", "Komunikasi"
- Jika ada "Laravel" → tambahkan "PHP"
- Jika ada "React" atau "Next.js" → tambahkan "JavaScript"
- Jika ada "Flutter" → tambahkan "Dart"
- Jika mengelola tim/proyek → tambahkan "Manajemen Proyek"
- Jangan inference yang tidak ada buktinya di CV — hanya inference yang logis dari tools yang disebutkan

Kembalikan dalam format JSON:
1. "skills": array SEMUA skill (eksplisit + inferensi logis dari context){summary_instruction}

Contoh output untuk developer yang pakai Laravel:
{{
  "skills": ["PHP", "Laravel", "MySQL", "RESTful API", "Git", "Backend Development", "Problem Solving"]{summary_example}
}}

Jawab HANYA JSON valid. Tidak ada teks lain, tidak ada markdown.

CV:
{text[:4000]}"""

        raw = await groq_request(
            messages=[
                {"role": "system", "content": "Kamu adalah CV parser expert Indonesia. Jawab HANYA JSON valid. Tidak ada teks lain."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600, temperature=0.1, timeout=20,
        )

        if raw:
            try:
                raw = raw.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(raw)
                ai_skills = parsed.get("skills", [])
                cv_summary = parsed.get("cv_summary", "")

                # Hybrid: gabung AI skills + regex skills, hilangkan duplikat
                regex_skills = regex_extract_skills(text)
                skills = list(dict.fromkeys(ai_skills + regex_skills))

                result = {"skills": skills, "cv_summary": cv_summary, "method": "groq_hybrid"}
                logger.info(f"extract_skills: {len(skills)} skills (hybrid), summary: {cv_summary[:80]}...")
                return result
            except Exception as e:
                logger.error(f"AI skill extraction parse error: {e}")

    # Fallback: regex only
    result["skills"] = regex_extract_skills(text)
    result["method"] = "regex_fallback"
    return result

# ── JOB MATCHING ──────────────────────────────────────────────────────────
JOB_KEYWORD_MAP = {
    "Social Media Specialist": ["social media", "sosial media", "sosmed", "social media specialist", "social media spesialis", "social media manager"],
    "Digital Marketing":       ["digital marketing", "digital marketer", "pemasaran digital", "marketing digital"],
    "Admin E-Commerce":        ["admin e-commerce", "admin ecommerce", "admin e commerce", "e-commerce admin", "admin tokopedia", "admin shopee", "admin lazada", "admin toko online", "admin toko", "admin online shop", "admin olshop", "olshop", "online shop", "toko online", "admin marketplace"],

    "Content Creator":         ["content creator", "konten kreator", "youtuber", "tiktoker", "kreator konten"],
    "Copywriter":              ["copywriter", "copy writer", "penulis konten", "content writer"],
    "SEO Specialist":          ["seo", "search engine", "seo specialist", "seo analyst"],
    "Public Relations":        ["public relations", "media relations", "humas", "hubungan masyarakat"],
    "UI/UX Designer":          ["ui ux", "ui/ux", "ux designer", "ui designer", "user experience", "product designer"],
    "Graphic Designer":        ["graphic designer", "desainer grafis", "graphic design", "designer"],
    "Data Analyst":            ["data analyst", "analis data", "data analysis", "data analytics"],
    "Data Scientist":          ["data scientist", "data science", "scientist"],
    "Data Engineer":           ["data engineer", "data engineering", "etl", "pipeline"],
    "Machine Learning Engineer":["machine learning", "ml engineer", "ai engineer", "artificial intelligence"],
    "Backend Developer":       ["backend", "back end", "back-end", "server side", "api developer"],
    "Frontend Developer":      ["frontend", "front end", "front-end", "web developer"],
    "Full Stack Developer":    ["full stack", "fullstack", "full-stack"],
    "Mobile Developer":        ["mobile developer", "android developer", "ios developer", "flutter developer", "react native"],
    "Cloud Engineer":          ["cloud engineer", "cloud architect", "aws engineer", "gcp engineer", "azure engineer"],
    "DevOps Engineer":         ["devops", "dev ops", "sre", "site reliability", "infrastructure"],
    "Cybersecurity Analyst":   ["cybersecurity", "cyber security", "keamanan siber", "security analyst", "ethical hacker"],
    "QA Engineer":             ["qa engineer", "quality assurance", "software tester", "tester"],
    "Business Analyst":        ["business analyst", "ba", "analis bisnis", "business analysis"],
    "System Analyst":          ["system analyst", "system analysis", "analis sistem", "systems analyst"],
    "Product Manager":         ["product manager", "pm", "product management", "manajer produk"],
    "Financial Analyst":       ["financial analyst", "finance analyst", "analis keuangan", "finance"],
    "IT Support":              ["it support", "helpdesk", "technical support", "it staff", "desktop support", "it helpdesk"],
}

def get_job_context(job: str, job_data_override: dict = None) -> tuple:
    """Cari data pekerjaan dari DB, scraped data, atau fuzzy match."""
    if job_data_override:
        return job, job_data_override

    job_lower = job.lower().strip()
    db = PEKERJAAN_DATABASE

    # Cek scraped data dulu
    for kw, scraped in SCRAPED_JOBS.items():
        if job_lower in kw.lower() or kw.lower() in job_lower:
            return kw, scraped

    # Exact match di DB
    for nama_job, data in db.items():
        if job_lower == nama_job.lower():
            return nama_job, data

    # Fuzzy match via keyword map
    for nama_job, keywords in JOB_KEYWORD_MAP.items():
        if any(kw in job_lower for kw in keywords):
            if nama_job in db:
                logger.info(f"Fuzzy match: '{job}' → '{nama_job}'")
                return nama_job, db[nama_job]

    # Word intersection match
    for nama_job, data in db.items():
        words_job = set(job_lower.split())
        words_db  = set(nama_job.lower().split())
        if words_job & words_db:
            logger.info(f"Word match: '{job}' → '{nama_job}'")
            return nama_job, data

    return job, None

async def auto_recommend_job(skill: list, pendidikan: str, pengalaman: str, cv_summary: str = "") -> str:
    """
    Rekomendasikan pekerjaan menggunakan Groq AI sebagai prioritas utama.
    Fallback ke Weighted Scoring kalau Groq gagal/limit.
    """
    job_list = list(PEKERJAAN_DATABASE.keys())
    
    # 1. Groq AI (Prioritas Utama — lebih pintar menebak konteks karir)
    if GROQ_API_KEY:
        skill_str = ", ".join(skill) if skill else "belum ada"
        cv_context = f"\nRingkasan CV: {cv_summary}" if cv_summary else ""
        prompt = f"""Pilih SATU pekerjaan PALING COCOK dari daftar untuk kandidat ini.
Skill user: {skill_str}
Pendidikan: {pendidikan}
Pengalaman: {pengalaman}{cv_context}

Daftar pekerjaan:
{json.dumps(job_list, ensure_ascii=False)}

Jawab HANYA dengan nama pekerjaan persis seperti di daftar. Tidak boleh ada kata lain."""

        result = await groq_request(
            messages=[
                {"role": "system", "content": "Jawab HANYA nama pekerjaan dari daftar. Tidak ada teks lain."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20, temperature=0.1, timeout=12,
        )

        if result:
            for job in job_list:
                if job.lower() == result.lower().strip() or job.lower() in result.lower():
                    logger.info(f"Groq recommend: {job}")
                    return job

    # 2. Weighted scoring (Fallback kalau Groq gagal)
    job_scores = {job: 0 for job in job_list}
    for job_name, data in PEKERJAAN_DATABASE.items():
        wajib = data.get("skill_wajib", [])
        plus  = data.get("skill_plus", [])
        tags  = data.get("skill_tags", [])
        for su in skill:
            if any(skills_match(su, w) for w in wajib):
                job_scores[job_name] += 3
            elif any(skills_match(su, p) for p in plus + tags):
                job_scores[job_name] += 1

    if job_scores:
        best_job = max(job_scores, key=job_scores.get)
        if job_scores[best_job] > 0:
            logger.info(f"Scoring fallback: {best_job} (skor: {job_scores[best_job]})")
            return best_job

    return "Business Analyst"

# ── SKILL MATCHING (AI + Rule-based) ──────────────────────────────────────
async def ai_skill_matching(
    skill_user: list,
    skill_wajib: list,
    skill_plus: list,
    job_title: str,
    cv_summary: str = ""
) -> dict:
    """
    Match skill user vs kebutuhan pekerjaan.
    Layer 1: Rule-based (skills_match dari knowledge_base)
    Layer 2: AI semantic matching via Groq (untuk sisa yang belum match)
    """
    if not skill_wajib:
        return {"matched_wajib": [], "matched_plus": [], "readiness": 0, "reasoning": {}}

    # Layer 1: Rule-based matching via unified skills_match (exact + synonym)
    exact_wajib = [s for s in skill_wajib if any(skills_match(u, s) for u in skill_user)]
    exact_plus  = [s for s in skill_plus  if any(skills_match(u, s) for u in skill_user)]
    sisa_wajib  = [s for s in skill_wajib if s not in exact_wajib]
    sisa_plus   = [s for s in skill_plus  if s not in exact_plus]

    # Layer 1b: Transferable skill scoring (partial credit 0.5x)
    # PHP→Python, Laravel→RESTful API, dll — paradigma sama, stack beda
    transferable_wajib = [s for s in sisa_wajib
                          if any(is_transferable(u, s) for u in skill_user)]
    transferable_plus  = [s for s in sisa_plus
                          if any(is_transferable(u, s) for u in skill_user)]

    # Kalau semua sudah match, atau tidak ada API key, langsung return
    if (not sisa_wajib and not sisa_plus) or not GROQ_API_KEY:
        # Transferable = 0.5 credit
        score_wajib = len(exact_wajib) + len(transferable_wajib) * 0.5
        score_plus  = len(exact_plus)  + len(transferable_plus)  * 0.5
        readiness = int(
            (score_wajib / max(len(skill_wajib), 1)) * 70 +
            (score_plus  / max(len(skill_plus), 1))  * 30
        )
        return {
            "matched_wajib": exact_wajib,
            "matched_plus":  exact_plus,
            "transferable_wajib": transferable_wajib,
            "readiness":     min(readiness, 100),
            "reasoning":     {},
        }

    # Layer 2: AI matching untuk sisa yang belum terdeteksi
    cv_context = f"\nKonteks CV: {cv_summary}\nGunakan konteks ini untuk menilai pengalaman nyata." if cv_summary else ""
    prompt = f"""Kamu adalah HR profesional senior Indonesia yang menilai kandidat secara holistik.
Posisi: "{job_title}"
{cv_context}
Skill kandidat: {json.dumps(skill_user, ensure_ascii=False)}

SISA Skill WAJIB yang belum terdeteksi: {json.dumps(sisa_wajib, ensure_ascii=False)}
SISA Skill PLUS yang belum terdeteksi: {json.dumps(sisa_plus, ensure_ascii=False)}

PANDUAN KESETARAAN — boleh dianggap setara:
- "PHP" / "Laravel" / "Django" / "Express" → memenuhi "Python" (sama-sama backend language) ✓
- "MySQL" / "PostgreSQL" / "SQLite" → memenuhi "SQL" ✓
- "SPSS" / "SPSS Dasar" → memenuhi "Statistik" ✓
- "Content Planning" → memenuhi "Content Creation" ✓
- "React" / "Vue" → memenuhi "Frontend Development" ✓
- "Docker" / "Kubernetes" → memenuhi "CI CD Pipelines" secara parsial ✓
- Project Laravel/Django yang sudah deploy → memenuhi "Git" ✓
- Project berbasis Laravel/Django/FastAPI → memenuhi "RESTful API" ✓

LARANGAN KERAS (ANTI-HALUSINASI):
- JANGAN PERNAH mengasumsikan skill teknis spesifik (seperti React, HTML, CSS, JavaScript, Node.js) HANYA DARI kata kunci umum seperti "Web Development", "Software Engineering", atau "Programming". Web dev bisa saja pakai WordPress, PHP, atau No-Code. Kalau tidak disebut spesifik, berarti TIDAK MATCH! ✗
- "JavaScript" TIDAK memenuhi "Node.js" — frontend JS dan Node.js server berbeda ✗
- "Python" TIDAK memenuhi "Machine Learning" tanpa bukti di CV ✗
- "Canva" TIDAK memenuhi "Adobe Illustrator" atau "Figma" ✗
- "Excel" TIDAK memenuhi "SQL" ✗
- WAJIB KETAT: Jika tidak ada bukti nama alat/framework secara eksplisit di CV/skill, JANGAN dianggap terpenuhi. Lebih baik gap-nya jujur.

Jawab HANYA JSON:
{{"ai_matched_wajib": ["skill dari sisa_wajib yang terpenuhi"],
  "ai_matched_plus": ["skill dari sisa_plus yang terpenuhi"],
  "reasoning": {{"skill": "alasan singkat berdasarkan bukti konkret"}}
}}"""


    raw = await groq_request(
        messages=[
            {"role": "system", "content": "Jawab HANYA JSON valid. Tidak ada teks lain."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500, temperature=0.1, timeout=15,
    )

    if raw:
        try:
            raw = raw.replace("```json", "").replace("```", "").strip()
            ai_data = json.loads(raw)
            final_wajib = list(set(exact_wajib + ai_data.get("ai_matched_wajib", [])))
            final_plus  = list(set(exact_plus  + ai_data.get("ai_matched_plus", [])))

            # Sisa setelah AI — hitung transferable partial credit
            sisa_after_ai_wajib = [s for s in skill_wajib if s not in final_wajib]
            sisa_after_ai_plus  = [s for s in skill_plus  if s not in final_plus]
            transferable_remain_wajib = [s for s in sisa_after_ai_wajib
                                         if any(is_transferable(u, s) for u in skill_user)]
            transferable_remain_plus  = [s for s in sisa_after_ai_plus
                                         if any(is_transferable(u, s) for u in skill_user)]

            score_wajib = len(final_wajib) + len(transferable_remain_wajib) * 0.5
            score_plus  = len(final_plus)  + len(transferable_remain_plus)  * 0.5
            readiness = int(
                (score_wajib / max(len(skill_wajib), 1)) * 70 +
                (score_plus  / max(len(skill_plus), 1))  * 30
            )
            return {
                "matched_wajib": final_wajib,
                "matched_plus":  final_plus,
                "transferable_wajib": transferable_remain_wajib,
                "readiness":     min(readiness, 100),
                "reasoning":     ai_data.get("reasoning", {}),
            }
        except Exception as e:
            logger.error(f"AI matching parse error: {e}")

    # Fallback ke rule-based + transferable
    score_wajib = len(exact_wajib) + len(transferable_wajib) * 0.5
    score_plus  = len(exact_plus)  + len(transferable_plus)  * 0.5
    readiness = int(
        (score_wajib / max(len(skill_wajib), 1)) * 70 +
        (score_plus  / max(len(skill_plus), 1))  * 30
    )
    return {
        "matched_wajib": exact_wajib,
        "matched_plus":  exact_plus,
        "transferable_wajib": transferable_wajib,
        "readiness":     min(readiness, 100),
        "reasoning":     {},
    }

# ── GAP ANALYSIS ──────────────────────────────────────────────────────────
async def hitung_gap(profil: ProfilUser, job_data_override: dict = None) -> dict:
    job, target_data = get_job_context(profil.target_job, job_data_override)

    if not target_data:
        target_data = {
            "skill_wajib": ["Komunikasi", "Problem Solving", "Microsoft Office"],
            "skill_plus": ["Bahasa Inggris", "Manajemen Waktu"],
            "estimasi_gaji_freshgrad": "Rp 4.000.000 – 8.000.000",
            "demand": "Bervariasi", "lokasi": ["Jakarta", "Remote"],
            "growth": "Tergantung industri", "sertifikasi": [],
            "soft_skill": ["Komunikasi", "Problem Solving"],
        }

    skill_wajib = target_data.get("skill_wajib", [])
    skill_plus  = target_data.get("skill_plus", [])
    soft_skill  = target_data.get("soft_skill", [])

    match_result = await ai_skill_matching(
        profil.skill, skill_wajib, skill_plus, profil.target_job,
        cv_summary=profil.cv_summary
    )

    matched_wajib = match_result["matched_wajib"]
    matched_plus  = match_result["matched_plus"]
    readiness     = match_result["readiness"]

    skill_kurang = [s for s in skill_wajib if s not in matched_wajib]
    plus_kurang  = [s for s in skill_plus  if s not in matched_plus]

    kursus_reko = []

    # ── STEP 1: Kursus untuk skill WAJIB yang kurang (prioritas utama) ──
    # Ini yang paling relevan — user harus tahu kursus untuk gap yang kritis dulu
    for sk in skill_kurang[:4]:
        matches = get_kursus_for_skill(sk)
        for k in matches[:2]:          # maks 2 kursus per skill
            if k not in kursus_reko and len(kursus_reko) < 4:
                kursus_reko.append(k)

    # ── STEP 2: Kursus untuk skill PLUS yang kurang (bonus, hanya kalau slot masih ada) ──
    # Hanya ditambahkan kalau slot kursus masih kosong setelah mandatory gap diisi
    if len(kursus_reko) < 3:
        for sk in plus_kurang[:3]:
            matches = get_kursus_for_skill(sk)
            for k in matches[:1]:      # maks 1 kursus per skill plus
                if k not in kursus_reko and len(kursus_reko) < 4:
                    kursus_reko.append(k)

    # ── STEP 3: Fallback / Pelengkap kalau kursus masih kurang ──
    if not kursus_reko:
        # Tidak ada kursus spesifik ditemukan
        if readiness >= 70:
            # Readiness tinggi → prioritas portofolio & apply
            kursus_reko = [
                {"nama": "Buat portofolio project nyata di GitHub", "platform": "GitHub", "url": "github.com", "biaya": "GRATIS", "skill_tags": []},
                {"nama": "Bergabung komunitas tech & mulai networking", "platform": "LinkedIn", "url": "linkedin.com", "biaya": "GRATIS", "skill_tags": []},
                {"nama": "Latihan soal interview teknis", "platform": "LeetCode", "url": "leetcode.com", "biaya": "GRATIS", "skill_tags": []},
            ]
        else:
            kursus_reko = [
                {"nama": "Pelatihan Skillhub Kemnaker — e-training resmi gratis", "platform": "Skillhub Kemnaker", "url": "skillhub.kemnaker.go.id", "biaya": "GRATIS", "skill_tags": []},
            ]
    elif len(kursus_reko) < 3 and readiness >= 50:
        # Sudah ada beberapa kursus, tapi slot masih ada → tambah aksi portofolio
        job_lower = job.lower()
        if any(k in job_lower for k in ["data", "analyst", "scientist", "engineer"]):
            extra = {"nama": "Kaggle Competitions — bangun portofolio data nyata", "platform": "Kaggle", "url": "kaggle.com/competitions", "biaya": "GRATIS", "skill_tags": []}
        elif any(k in job_lower for k in ["backend", "frontend", "full stack", "mobile", "devops"]):
            extra = {"nama": "Buat portofolio project di GitHub — bukti nyata untuk recruiter", "platform": "GitHub", "url": "github.com", "biaya": "GRATIS", "skill_tags": []}
        elif any(k in job_lower for k in ["ui", "ux", "design", "graphic"]):
            extra = {"nama": "Kumpulkan portfolio desain di Behance / Dribbble", "platform": "Behance", "url": "behance.net", "biaya": "GRATIS", "skill_tags": []}
        else:
            extra = {"nama": "Update profil LinkedIn dan mulai bangun koneksi industri", "platform": "LinkedIn", "url": "linkedin.com", "biaya": "GRATIS", "skill_tags": []}
        if extra not in kursus_reko:
            kursus_reko.append(extra)

    roadmap_full = ROADMAP.get(job, [])

    if not roadmap_full:
        roadmap_full = [
             {"fase": "Bulan 1-2", "nama": "Riset & Fondasi", "skill": ["Komunikasi", "Problem Solving"], "kursus": "Pelatihan Skillhub Kemnaker", "milestone": "Pahami fundamental industri ini"},
             {"fase": "Bulan 3-4", "nama": "Praktek Langsung", "skill": ["Praktek Lapangan"], "kursus": "Cari referensi di YouTube/LinkedIn", "milestone": "Mulai apply magang atau project kecil"}
        ]

    import copy
    roadmap = [copy.deepcopy(r) for r in roadmap_full]

    if readiness >= 100:
        roadmap = [
            {"fase": "Bulan 1-2", "nama": "Fokus Apply & Interview", "skill": ["CV Review", "Mock Interview", "Networking"], "kursus": "Maksimalkan platform seperti LinkedIn & Jobstreet", "milestone": "Apply ke 5-10 lowongan yang relevan per minggu"}
        ]
    else:
        if readiness >= 80 and len(roadmap) > 1:
            roadmap = roadmap[-2:] # Sisakan 2 fase terakhir (atau 1 jika arraynya cuma 2)
            if len(roadmap) > 1:
                 roadmap = roadmap[-1:] # Kalau udah 80% ke atas, sisakan 1 fase terakhir aja (Portofolio/Launch)
        elif readiness >= 50 and len(roadmap) > 2:
            roadmap = roadmap[1:] # Sisakan 2 fase terakhir (skip fase Fondasi)
        
        # Rapikan ulang penomoran bulannya biar nggak bolong/lompat
        label_bulan = ["Bulan 1-2", "Bulan 3-4", "Bulan 5-6"]
        for i, step in enumerate(roadmap):
            if i < len(label_bulan):
                step["fase"] = label_bulan[i]

    gaji = get_gaji_by_experience(target_data, profil.pengalaman)

    return {
        "job_target":     job,
        "job_data":       target_data,
        "readiness":      readiness,
        "match_method":   "ai_semantic",
        "level": (
            "Siap Apply!"      if readiness >= 70 else
            "Hampir Siap"      if readiness >= 45 else
            "Perlu Persiapan"
        ),
        "warna": (
            "green" if readiness >= 70 else
            "amber" if readiness >= 45 else
            "red"
        ),
        "skill_dimiliki":  matched_wajib,
        "skill_kurang":    skill_kurang,
        "skill_plus_match":matched_plus,
        "skill_plus_kurang":plus_kurang[:4],
        "soft_skill":      soft_skill,
        "kursus_rekomendasi": kursus_reko[:5],
        "roadmap":         roadmap,
        "gaji_range":      gaji,
        "demand":          target_data.get("demand", "-"),
        "lokasi":          target_data.get("lokasi", ["Jakarta"]),
        "growth":          target_data.get("growth", "-"),
        "sertifikasi":     target_data.get("sertifikasi", [])[:3],
        "ai_reasoning":    match_result.get("reasoning", {}),
    }

# ── RELEVANCE KEYWORDS (untuk deteksi career pivot di /analyze) ───────────
RELEVANCE_KEYWORDS = {
    "social media": ["social media", "instagram", "content", "konten", "publikasi", "sosmed"],
    "admin": ["admin", "administrasi", "e-commerce", "marketplace", "pesanan"],
    "data": ["data", "analisis", "statistik", "excel", "sql"],
    "design": ["desain", "design", "canva", "figma", "grafis"],
    "marketing": ["marketing", "pemasaran", "iklan", "campaign", "promosi"],
    "hr": ["hr", "rekrut", "sdm", "karyawan"],
    "finance": ["keuangan", "akuntansi", "finance", "laporan keuangan"],
}

# ── ENDPOINTS ─────────────────────────────────────────────────────────────
api_router = APIRouter(prefix="/api")
api_router_index = APIRouter(prefix="/api/index.py")

@app.get("/")
def serve_index():
    return FileResponse(pathlib.Path(__file__).parent.parent / "index.html")

@app.get("/health")
@api_router.get("/health")
@api_router_index.get("/health")
def health():
    return {"status": "ok", "groq": bool(GROQ_API_KEY), "jobs": len(PEKERJAAN_DATABASE)}

@app.get("/jobs")
@api_router.get("/jobs")
@api_router_index.get("/jobs")
def list_jobs():
    result = []
    for k, v in PEKERJAAN_DATABASE.items():
        gaji = v.get("gaji_junior", v.get("estimasi_gaji_freshgrad", "-"))
        result.append({
            "nama": k,
            "kategori": v.get("kategori", "-"),
            "gaji": gaji,
            "demand": v.get("demand", "-"),
        })
    return result

@app.post("/analyze")
@api_router.post("/analyze")
@api_router_index.post("/analyze")
async def analyze(profil: ProfilUser):
    is_recommended = False

    if not profil.target_job.strip() and not profil.skill:
        raise HTTPException(
            status_code=400,
            detail="SIGAP butuh minimal satu info: isi target pekerjaan, atau masukkan skill yang kamu punya (bisa juga upload CV dulu)."
        )

    if not profil.target_job.strip():
        logger.info(f"Target kosong — jalankan auto_recommend untuk skill: {profil.skill}")
        recommended_job = await auto_recommend_job(
            profil.skill, profil.pendidikan, profil.pengalaman, profil.cv_summary
        )
        profil = ProfilUser(
            pendidikan=profil.pendidikan,
            jurusan=profil.jurusan,
            skill=profil.skill,
            target_job=recommended_job,
            pengalaman=profil.pengalaman,
            lokasi=profil.lokasi,
            cv_summary=profil.cv_summary,
        )
        is_recommended = True
        logger.info(f"Job direkomendasikan: {recommended_job}")

    job_in_db = any(
        profil.target_job.lower() in k.lower() or k.lower() in profil.target_job.lower()
        for k in PEKERJAAN_DATABASE.keys()
    )

    result = await hitung_gap(profil)
    result["source"]         = "database" if job_in_db else "ai_generated"
    result["is_recommended"] = is_recommended
    result["cv_summary_used"] = profil.cv_summary

    profil_dict = {
        "pendidikan":  profil.pendidikan,
        "skill":       profil.skill,
        "target_job":  profil.target_job,
        "pengalaman":  profil.pengalaman,
        "lokasi":      profil.lokasi,
        "readiness":   result["readiness"],
        "skill_kurang": result.get("skill_kurang", []),
    }

    # Hitung relevansi CV untuk career pivot detection
    cv_sum = profil.cv_summary.lower() if profil.cv_summary else ""
    target_lower = result['job_target'].lower()

    is_cv_relevant = False
    for category, keywords in RELEVANCE_KEYWORDS.items():
        if category in target_lower or any(kw in target_lower for kw in keywords):
            if any(kw in cv_sum for kw in keywords):
                is_cv_relevant = True
                break

    is_career_pivot = result['readiness'] < 40 and not is_cv_relevant

    pivot_note = ""
    if is_career_pivot and not is_cv_relevant:
        pivot_note = f"""
PERINGATAN: Ini adalah career pivot yang cukup ekstrem. 
Pengalaman user berasal dari latar belakang yang berbeda dengan target {result['job_target']}.
Evaluasi dengan jujur — butuh waktu dan dedikasi panjang."""
    elif is_career_pivot and is_cv_relevant:
        pivot_note = f"""
CATATAN PENTING: Meski readiness rendah secara metrik, cv_summary menunjukkan 
user sudah punya pengalaman RELEVAN dengan {result['job_target']}.
Akui pengalaman yang sudah ada dan fokus pada gap yang perlu ditutup — 
jangan bilang pengalaman mereka tidak relevan!"""

    readiness_context = (
        "SANGAT RENDAH — career pivot berat, butuh waktu dan dedikasi panjang" if result['readiness'] < 30 else
        "RENDAH — masih jauh, tapi bisa dicapai dengan konsistensi 6-12 bulan" if result['readiness'] < 50 else
        "SEDANG — sudah ada fondasi, perlu 3-6 bulan fokus belajar" if result['readiness'] < 70 else
        "TINGGI — sudah hampir siap, fokus ke portofolio dan apply kerja"
    )

    cv_context_str = f"""

RIWAYAT PENGALAMAN (dari CV — WAJIB DIBACA sebelum evaluasi):
{profil.cv_summary}

PENTING: Evaluasi harus mempertimbangkan pengalaman nyata di atas. 
Jangan abaikan riwayat kerja/organisasi yang sudah ada.""" if profil.cv_summary else ""

    prompt = f"""User ini memiliki readiness {result['readiness']}% untuk menjadi {result['job_target']}.{cv_context_str}
Konteks readiness: {readiness_context}

Skill yang sudah dimiliki: {', '.join(result['skill_dimiliki']) or 'belum ada yang relevan dengan target karir ini'}
Skill wajib yang MASIH KURANG: {', '.join(result['skill_kurang']) or 'tidak ada — sudah siap!'}
Pengalaman: {profil.pengalaman}
{pivot_note}

TUGASMU: Berikan evaluasi JUJUR dan REALISTIS maksimal 3 kalimat.
LALU, berikan 1 kalimat deskripsi ringkas (maksimal 10 kata) untuk tiap "Skill wajib yang MASIH KURANG" di atas (mengapa skill tersebut penting untuk posisi ini).

ATURAN KETAT:
1. Readiness < 40%: Jujur bahwa ini perjalanan panjang, sebutkan 1 skill fundamental.
2. Readiness 40-70%: Akui gap yang ada, berikan estimasi waktu realistis.
3. Readiness > 70%: Apresiasi skill yang sudah ada, dorong segera mulai apply.
4. Jangan sebut skill di luar daftar skill kurang.
5. WAJIB return format JSON murni:
{{
  "summary": "evaluasi 3 kalimat kamu...",
  "gap_context": {{
    "Nama Skill 1": "Deskripsi singkat pentingnya skill ini...",
    "Nama Skill 2": "..."
  }}
}}"""

    messages = [
        {"role": "system", "content": get_system_prompt(profil_dict) + " Return strict JSON."},
        {"role": "user", "content": prompt}
    ]

    ai_resp = await groq_request(messages, response_format={"type": "json_object"})
    ai_summary = ""
    skill_kurang_detail = []

    if ai_resp:
        try:
            parsed = json.loads(ai_resp)
            ai_summary = parsed.get("summary", "")
            gap_context = parsed.get("gap_context", {})
            for sk in result.get("skill_kurang", []):
                skill_kurang_detail.append({
                    "skill": sk,
                    "desc": gap_context.get(sk, "Krusial untuk kompetensi inti di posisi ini.")
                })
        except Exception as e:
            logger.error(f"Failed to parse JSON ai_summary: {e}")
            ai_summary = ""

    if not ai_summary:
        r = result["readiness"]
        sk = result.get("skill_kurang", [])
        sd = result.get("skill_dimiliki", [])
        job = result.get("job_target", profil.target_job)
        if r >= 70:
            ai_summary = f"Kamu sudah punya fondasi yang kuat untuk {job} dengan {len(sd)} skill yang relevan. Sekarang fokus ke portofolio nyata — recruiter butuh bukti, bukan sekadar klaim di CV. Mulai apply ke perusahaan yang cocok!"
        elif r >= 40:
            gap_str = ", ".join(sk[:2]) if sk else "beberapa skill teknis"
            ai_summary = f"Kamu sudah punya fondasi, tapi masih ada gap di {gap_str}. Estimasi realistis: 3-6 bulan belajar konsisten sudah bisa apply. Prioritaskan kursus gratis di Dicoding atau Skillhub Kemnaker dulu."
        else:
            gap_str = sk[0] if sk else "skill fundamental"
            ai_summary = f"Gap-nya cukup besar untuk {job}, tapi bisa diatasi. Mulai dari {gap_str} sebagai fondasi utama — itu kunci untuk membuka akses ke skill berikutnya. Konsisten 2 jam per hari selama 6-12 bulan sudah cukup untuk berubah."
            
    if not skill_kurang_detail:
        for sk in result.get("skill_kurang", []):
            skill_kurang_detail.append({"skill": sk, "desc": "Diperlukan untuk peran ini."})

    result["ai_summary"] = ai_summary
    result["skill_kurang_detail"] = skill_kurang_detail

    result["ai_summary"] = ai_summary
    return result

@app.post("/chat")
@api_router.post("/chat")
@api_router_index.post("/chat")
async def chat(req: ChatRequest):
    profil_dict = None
    if req.profil:
        # Kalau frontend sudah kirim readiness dari /analyze, pakai langsung (skip re-compute)
        if req.profil.readiness is not None:
            readiness = req.profil.readiness
            skill_kurang = req.profil.skill_kurang
        else:
            # Fallback: hitung gap kalau readiness belum ada
            gap = await hitung_gap(req.profil)
            readiness = gap["readiness"]
            skill_kurang = gap.get("skill_kurang", [])

        profil_dict = {
            "pendidikan": req.profil.pendidikan,
            "skill": req.profil.skill,
            "target_job": req.profil.job_target or req.profil.target_job,
            "pengalaman": req.profil.pengalaman,
            "lokasi": req.profil.lokasi,
            "readiness": readiness,
            "skill_kurang": skill_kurang,
        }

    messages = [{"role": "system", "content": get_system_prompt(profil_dict)}]
    for msg in req.history[-10:]:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.message})

    reply = await groq_request(messages)
    if not reply:
        reply = "Maaf, SIGAP AI belum tersedia. Pastikan GROQ_API_KEY sudah diset di file .env (gratis di console.groq.com)."

    return {"reply": reply}

@app.post("/parse-cv-text", tags=["CV"])
@api_router.post("/parse-cv-text", tags=["CV"])
@api_router_index.post("/parse-cv-text", tags=["CV"])
async def parse_cv_text(req: CVTextRequest):
    result = await extract_skills_from_text(req.text, include_summary=True)
    return {
        "skills": result["skills"],
        "cv_summary": result["cv_summary"],
        "method": result["method"],
        "char_count": len(req.text),
    }

@app.post("/parse-cv", tags=["CV"])
@api_router.post("/parse-cv", tags=["CV"])
@api_router_index.post("/parse-cv", tags=["CV"])
async def parse_cv(file: UploadFile = File(...)):
    content_bytes = await file.read()

    text = ""
    
    if file.filename.endswith(".pdf"):
        try:
            from io import BytesIO
            from pdfminer.high_level import extract_text as pdf_extract
            text = pdf_extract(BytesIO(content_bytes))
        except Exception as e:
            return {"skills": [], "text": "", "message": f"Gagal membaca PDF: {str(e)}"}
    else:
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                text = content_bytes.decode(enc)
                break
            except:
                continue

    if not text.strip():
        return {"skills": [], "text": "", "message": "Format tidak terbaca. Pastikan PDF bisa di-copy teksnya (bukan gambar)."}

    result = await extract_skills_from_text(text, include_summary=False)
    return {
        "skills": result["skills"],
        "text": text[:500],
        "method": result["method"],
    }

# ── MAIN ──────────────────────────────────────────────────────────────────
app.include_router(api_router)
app.include_router(api_router_index)

# Catch-all route to debug Vercel path issues
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"])
async def catch_all(path_name: str):
    from fastapi import Request
    return {"detail": f"Not Found in catch_all. Path received: {path_name}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)