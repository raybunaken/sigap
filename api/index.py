"""
SkillSync - AI Advisor Skill Gap untuk Fresh Grad Indonesia
Backend: FastAPI + Groq (Llama 3.3)
Jalankan: python api.py
"""

import os, json, logging, asyncio, re, pathlib, time
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter, Request, Response
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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
GROQ_MODEL   = "openai/gpt-oss-120b"
# Kuota gratis Groq 8k token/menit PER MODEL. Satu scan membakar ~10-13k
# token, jadi pipeline dipecah ke beberapa model supaya tiap stage punya
# kuota sendiri. Semua gpt-oss: reasoning_effort low + retry content kosong.
# qwen3.6-27b DILARANG dipakai: json mode selalu 400, dan tanpa json mode
# thinking-nya memakan seluruh budget token tanpa bisa dimatikan.
MODEL_EXTRACT = "openai/gpt-oss-20b"
MODEL_JUDGE   = "openai/gpt-oss-120b"
MODEL_NARRATE = "openai/gpt-oss-20b"
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"

# ── SUPABASE (opsional: semua fitur degrade mulus kalau belum diset) ──────
# Dipakai untuk: waitlist persisten, log scan anonim (Skillsy Index),
# dan heartbeat harian biar project free-tier tidak di-pause.
SUPABASE_URL  = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY  = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_ON   = bool(SUPABASE_URL and SUPABASE_KEY)

async def supabase_insert(table: str, payload: dict, ignore_dupes: bool = False) -> bool:
    """Insert satu baris via PostgREST. False kalau tidak dikonfigurasi/gagal."""
    if not SUPABASE_ON:
        return False
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": ("resolution=ignore-duplicates," if ignore_dupes else "") + "return=minimal",
    }
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            res = await client.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=headers, json=payload)
            if res.status_code not in (200, 201):
                logger.error(f"Supabase insert {table}: HTTP {res.status_code} {res.text[:150]}")
                return False
            return True
    except Exception as e:
        logger.error(f"Supabase insert {table}: {e}")
        return False

async def supabase_ping() -> bool:
    """Query ringan untuk menjaga project free-tier tetap aktif."""
    if not SUPABASE_ON:
        return False
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            res = await client.get(f"{SUPABASE_URL}/rest/v1/waitlist?select=id&limit=1", headers=headers)
            return res.status_code == 200
    except Exception as e:
        logger.error(f"Supabase ping: {e}")
        return False

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
        logger.info(f"✓ SkillSync ready! Model: {GROQ_MODEL}")
    else:
        logger.warning("⚠ GROQ_API_KEY tidak ditemukan! Set di file .env")
    yield

app = FastAPI(
    title="SkillSync - AI Advisor Skill Gap",
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

# ── RATE LIMIT (best-effort, in-memory per serverless instance) ───────────
# Target: matikan penyalahgunaan murahan (skrip membakar kuota Groq), bukan
# mengalahkan penyerang deterministik. Counter konsisten antar instance
# menyusul begitu Supabase dipasang.
_RATE_BUCKETS: dict = {}
RATE_LIMIT_HOURLY = 40   # per IP / per install-ID per jam
RATE_LIMIT_MINUTE = 8    # burst limit

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    is_costly = any(
        p in path
        for p in ("/analyze-job", "/generate-cover-letter", "/parse-cv", "/chat")
    )
    if is_costly and request.method == "POST":
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )
        client_id = request.headers.get("x-skillsy-client", "")
        keys = [f"ip:{client_ip}"] + ([f"cid:{client_id}"] if client_id else [])

        now = time.time()
        allowed = True
        for k in keys:
            bucket = _RATE_BUCKETS.setdefault(k, [])
            bucket[:] = [t for t in bucket if now - t < 3600]
            recent = [t for t in bucket if now - t < 60]
            if len(bucket) >= RATE_LIMIT_HOURLY or len(recent) >= RATE_LIMIT_MINUTE:
                allowed = False

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Terlalu banyak permintaan. Tunggu sebentar lalu coba lagi."},
                headers={"Retry-After": "60"},
            )
        for k in keys:
            _RATE_BUCKETS[k].append(now)

        # prune sesekali biar memori tidak bocor
        if len(_RATE_BUCKETS) > 5000:
            for k in list(_RATE_BUCKETS.keys()):
                if not _RATE_BUCKETS[k] or now - _RATE_BUCKETS[k][-1] > 3600:
                    _RATE_BUCKETS.pop(k, None)

    response = await call_next(request)
    return response

# ── SCHEMAS ───────────────────────────────────────────────────────────────
class ProfilUser(BaseModel):
    language: Optional[str] = "id"
    pendidikan:   str
    jurusan:      str
    skill:        List[str] = []
    target_job:   str = ""
    pengalaman:   str = "Fresh grad / belum ada"
    lokasi:       str = "Jakarta"
    cv_summary:   str = ""
    # Fields dari frontend setelah /analyze - supaya /chat tidak perlu re-compute gap
    readiness:    Optional[float] = None
    skill_kurang: List[str] = []
    job_target:   str = ""

class ChatMessage(BaseModel):
    role:    str
    content: str

class ChatRequest(BaseModel):
    language: Optional[str] = "id"
    message:      str
    history:      List[ChatMessage] = []
    profil:       Optional[ProfilUser] = None

class CVTextRequest(BaseModel):
    text: str

class AdvisoryRequest(BaseModel):
    language: Optional[str] = "id"
    readiness_score: float
    skill_gap: List[str] = []
    user_reply: str
    target_job: str

class AnalyzeJobRequest(BaseModel):
    cv_text: str = Field(..., min_length=50, max_length=150000)
    job_title: str = Field(..., min_length=1, max_length=1000)
    job_description: str = Field(..., min_length=30, max_length=150000)


# ── GROQ API (satu entry point untuk semua panggilan) ─────────────────────
async def groq_request(
    messages: list,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    timeout: int = 20,
    response_format: Optional[dict] = None,
    model: Optional[str] = None,
) -> Optional[str]:
    """
    Satu-satunya fungsi yang panggil Groq API.
    Return content string, atau None kalau gagal.
    - Retry 429 dengan menunggu sesuai header x-ratelimit-reset-tokens
      (jendela kuota gratis cuma ~12-30 detik, jadi tunggu yang benar,
      bukan backoff 1-2 detik yang pasti gagal).
    - Model reasoning (gpt-oss) kadang menolak response_format json_object
      pada prompt kompleks: panggilan diulang tanpa json mode, parser
      _extract_json yang membersihkan sisanya.
    """
    if not GROQ_API_KEY:
        return None
    use_model = model or GROQ_MODEL
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    async def _post(payload: dict) -> httpx.Response:
        async with httpx.AsyncClient(timeout=timeout) as client:
            return await client.post(GROQ_URL, headers=headers, json=payload)

    base_payload = {
        "model": use_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    # Model reasoning (gpt-oss) memakan max_tokens untuk berpikir duluan;
    # reasoning_effort low menjaga token tetap untuk jawaban sebenarnya.
    if use_model.startswith("openai/gpt-oss"):
        base_payload["reasoning_effort"] = "low"
    use_json_mode = bool(response_format)

    for attempt in range(4):
        payload = dict(base_payload)
        if response_format and use_json_mode:
            payload["response_format"] = response_format
        try:
            res = await _post(payload)
            if res.status_code == 429:
                reset = res.headers.get("x-ratelimit-reset-tokens", "")
                wait_s = 2.0
                try:
                    # format "12.33s"
                    wait_s = min(float(str(reset).rstrip("s")) + 0.5, 20.0)
                except ValueError:
                    pass
                logger.warning(f"Groq 429 ({use_model}), tunggu {wait_s:.1f}s lalu retry...")
                await asyncio.sleep(wait_s)
                continue
            if res.status_code == 400 and use_json_mode:
                # model reasoning kadang gagal validasi json_object:
                # ulangi tanpa json mode (output tetap diparse _extract_json)
                logger.warning("Groq 400 dengan json_object, retry tanpa json mode...")
                use_json_mode = False
                continue
            data = res.json()
            if "choices" not in data:
                logger.error(f"Groq no choices: {data}")
                return None
            content = data["choices"][0]["message"]["content"]
            if content and content.strip():
                return content.strip()
            # content kosong = reasoning menghabiskan budget token;
            # ulangi dengan budget lebih besar
            logger.warning(
                f"Groq content kosong ({use_model}), retry dengan max_tokens lebih besar..."
            )
            base_payload["max_tokens"] = min(base_payload["max_tokens"] * 2, 6000)
            continue
        except Exception as e:
            logger.error(f"Groq error (attempt {attempt+1}): {e}")
            if attempt < 3:
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
    # Backend languages - PHP, Python, Node.js, Java semua paradigma sama
    {"backend language", "python", "node.js", "php", "laravel", "java", "go", "django",
     "fastapi", "express", "ruby", "spring", "asp.net", "kotlin"},
    # SQL databases
    {"sql", "mysql", "postgresql", "sqlite", "oracle", "microsoft sql server"},
    # NoSQL databases
    {"mongodb", "firestore", "dynamodb", "redis", "cassandra"},
    # Frontend frameworks - React, Vue, Angular paradigma sama
    {"react", "react.js", "vue", "vue.js", "angular", "svelte"},
    # Mobile - Flutter, React Native, Kotlin paradigma sama
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
        t_in = any(t == g or t in g or g in t for g in group)
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

ATURAN PENTING - Inference dari konteks project:
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
- Jangan inference yang tidak ada buktinya di CV - hanya inference yang logis dari tools yang disebutkan

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
    
    # 1. Groq AI (Prioritas Utama - lebih pintar menebak konteks karir)
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
    # PHP→Python, Laravel→RESTful API, dll - paradigma sama, stack beda
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

PANDUAN KESETARAAN - boleh dianggap setara:
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
- "JavaScript" TIDAK memenuhi "Node.js" - frontend JS dan Node.js server berbeda ✗
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

            # Sisa setelah AI - hitung transferable partial credit
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
    # Ini yang paling relevan - user harus tahu kursus untuk gap yang kritis dulu
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
            if profil.language == "en":
                kursus_reko = [
                    {"nama": "Build real portfolio projects on GitHub", "platform": "GitHub", "url": "github.com", "biaya": "FREE", "skill_tags": []},
                    {"nama": "Join tech communities & start networking", "platform": "LinkedIn", "url": "linkedin.com", "biaya": "FREE", "skill_tags": []},
                    {"nama": "Practice technical interview questions", "platform": "LeetCode", "url": "leetcode.com", "biaya": "FREE", "skill_tags": []},
                ]
            else:
                kursus_reko = [
                    {"nama": "Buat portofolio project nyata di GitHub", "platform": "GitHub", "url": "github.com", "biaya": "GRATIS", "skill_tags": []},
                    {"nama": "Bergabung komunitas tech & mulai networking", "platform": "LinkedIn", "url": "linkedin.com", "biaya": "GRATIS", "skill_tags": []},
                    {"nama": "Latihan soal interview teknis", "platform": "LeetCode", "url": "leetcode.com", "biaya": "GRATIS", "skill_tags": []},
                ]
        else:
            if profil.language == "en":
                kursus_reko = [
                    {"nama": "Skillhub Kemnaker Training - Official Free E-Training", "platform": "Skillhub Kemnaker", "url": "skillhub.kemnaker.go.id", "biaya": "FREE", "skill_tags": []},
                ]
            else:
                kursus_reko = [
                    {"nama": "Pelatihan Skillhub Kemnaker - e-training resmi gratis", "platform": "Skillhub Kemnaker", "url": "skillhub.kemnaker.go.id", "biaya": "GRATIS", "skill_tags": []},
                ]
    elif len(kursus_reko) < 3 and readiness >= 50:
        # Sudah ada beberapa kursus, tapi slot masih ada → tambah aksi portofolio
        job_lower = job.lower()
        if any(k in job_lower for k in ["data", "analyst", "scientist", "engineer"]):
            if profil.language == "en":
                extra = {"nama": "Kaggle Competitions - build real data portfolio", "platform": "Kaggle", "url": "kaggle.com/competitions", "biaya": "FREE", "skill_tags": []}
            else:
                extra = {"nama": "Kaggle Competitions - bangun portofolio data nyata", "platform": "Kaggle", "url": "kaggle.com/competitions", "biaya": "GRATIS", "skill_tags": []}
        elif any(k in job_lower for k in ["backend", "frontend", "full stack", "mobile", "devops"]):
            if profil.language == "en":
                extra = {"nama": "Build project portfolio on GitHub - real proof for recruiters", "platform": "GitHub", "url": "github.com", "biaya": "FREE", "skill_tags": []}
            else:
                extra = {"nama": "Buat portofolio project di GitHub - bukti nyata untuk recruiter", "platform": "GitHub", "url": "github.com", "biaya": "GRATIS", "skill_tags": []}
        elif any(k in job_lower for k in ["ui", "ux", "design", "graphic"]):
            if profil.language == "en":
                extra = {"nama": "Collect design portfolio on Behance / Dribbble", "platform": "Behance", "url": "behance.net", "biaya": "FREE", "skill_tags": []}
            else:
                extra = {"nama": "Kumpulkan portfolio desain di Behance / Dribbble", "platform": "Behance", "url": "behance.net", "biaya": "GRATIS", "skill_tags": []}
        else:
            if profil.language == "en":
                extra = {"nama": "Update LinkedIn profile and start building industry connections", "platform": "LinkedIn", "url": "linkedin.com", "biaya": "FREE", "skill_tags": []}
            else:
                extra = {"nama": "Update profil LinkedIn dan mulai bangun koneksi industri", "platform": "LinkedIn", "url": "linkedin.com", "biaya": "GRATIS", "skill_tags": []}
        if extra not in kursus_reko:
            kursus_reko.append(extra)

    roadmap_full = ROADMAP.get(job, [])

    if not roadmap_full:
        if profil.language == "en":
            roadmap_full = [
                 {"fase": "Month 1-2", "nama": "Research & Foundation", "skill": ["Communication", "Problem Solving"], "kursus": "Skillhub Kemnaker Training", "milestone": "Understand the fundamentals of this industry"},
                 {"fase": "Month 3-4", "nama": "Hands-on Practice", "skill": ["Field Practice"], "kursus": "Find references on YouTube/LinkedIn", "milestone": "Start applying for internships or small projects"}
            ]
        else:
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



@app.get("/health")
@api_router.get("/health")
@api_router_index.get("/health")
def health():
    return {"status": "ok", "groq": bool(GROQ_API_KEY), "supabase": SUPABASE_ON, "jobs": len(PEKERJAAN_DATABASE)}

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
            detail="SkillSync butuh minimal satu info: isi target pekerjaan, atau masukkan skill yang kamu punya (bisa juga upload CV dulu)."
        )

    if not profil.target_job.strip():
        logger.info(f"Target kosong - jalankan auto_recommend untuk skill: {profil.skill}")
        recommended_job = await auto_recommend_job(
            profil.skill, profil.pendidikan, profil.pengalaman, profil.cv_summary
        )
        profil = ProfilUser(
            language=profil.language,
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
Evaluasi dengan jujur - butuh waktu dan dedikasi panjang."""
    elif is_career_pivot and is_cv_relevant:
        pivot_note = f"""
CATATAN PENTING: Meski readiness rendah secara metrik, cv_summary menunjukkan 
user sudah punya pengalaman RELEVAN dengan {result['job_target']}.
Akui pengalaman yang sudah ada dan fokus pada gap yang perlu ditutup - 
jangan bilang pengalaman mereka tidak relevan!"""

    readiness_context = (
        "SANGAT RENDAH - career pivot berat, butuh waktu dan dedikasi panjang" if result['readiness'] < 30 else
        "RENDAH - masih jauh, tapi bisa dicapai dengan konsistensi 6-12 bulan" if result['readiness'] < 50 else
        "SEDANG - sudah ada fondasi, perlu 3-6 bulan fokus belajar" if result['readiness'] < 70 else
        "TINGGI - sudah hampir siap, fokus ke portofolio dan apply kerja"
    )

    cv_context_str = f"""

RIWAYAT PENGALAMAN (dari CV - WAJIB DIBACA sebelum evaluasi):
{profil.cv_summary}

PENTING: Evaluasi harus mempertimbangkan pengalaman nyata di atas. 
Jangan abaikan riwayat kerja/organisasi yang sudah ada.""" if profil.cv_summary else ""

    prompt = f"""User ini memiliki readiness {result['readiness']}% untuk menjadi {result['job_target']}.{cv_context_str}
Konteks readiness: {readiness_context}

Skill yang sudah dimiliki: {', '.join(result['skill_dimiliki']) or 'belum ada yang relevan dengan target karir ini'}
Skill wajib yang MASIH KURANG: {', '.join(result['skill_kurang']) or 'tidak ada - sudah siap!'}
Pengalaman: {profil.pengalaman}
{pivot_note}

TUGASMU: Berikan evaluasi JUJUR dan REALISTIS maksimal 3 kalimat.
LALU, berikan 1 kalimat deskripsi ringkas (maksimal 10 kata) untuk tiap "Skill wajib yang MASIH KURANG" di atas (mengapa skill tersebut penting untuk posisi ini).

ATURAN KETAT:
1. Readiness < 40%: Jujur bahwa ini perjalanan panjang, sebutkan 1 skill fundamental.
2. Readiness 40-70%: Akui gap yang ada, berikan estimasi waktu realistis.
3. Readiness > 70%: Apresiasi skill yang sudah ada, dorong segera mulai apply.
4. Jangan sebut skill di luar daftar skill kurang.
{"5. CRITICAL INSTRUCTION: TRANSLATE your 'summary' and the descriptions inside 'gap_context' into ENGLISH! The user wants the response in English." if profil.language == "en" else "5. WAJIB return format JSON murni:"}
6. WAJIB return format JSON murni:
{{
  "summary": "evaluasi 3 kalimat kamu...",
  "gap_context": {{
    "Nama Skill 1": "Deskripsi singkat pentingnya skill ini...",
    "Nama Skill 2": "..."
  }}
}}"""

    messages = [
        {"role": "system", "content": get_system_prompt(profil_dict, profil.language) + " Return strict JSON."},
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
            ai_summary = f"Kamu sudah punya fondasi yang kuat untuk {job} dengan {len(sd)} skill yang relevan. Sekarang fokus ke portofolio nyata - recruiter butuh bukti, bukan sekadar klaim di CV. Mulai apply ke perusahaan yang cocok!"
        elif r >= 40:
            gap_str = ", ".join(sk[:2]) if sk else "beberapa skill teknis"
            ai_summary = f"Kamu sudah punya fondasi, tapi masih ada gap di {gap_str}. Estimasi realistis: 3-6 bulan belajar konsisten sudah bisa apply. Prioritaskan kursus gratis di Dicoding atau Skillhub Kemnaker dulu."
        else:
            gap_str = sk[0] if sk else "skill fundamental"
            ai_summary = f"Gap-nya cukup besar untuk {job}, tapi bisa diatasi. Mulai dari {gap_str} sebagai fondasi utama - itu kunci untuk membuka akses ke skill berikutnya. Konsisten 2 jam per hari selama 6-12 bulan sudah cukup untuk berubah."
            
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

    messages = [{"role": "system", "content": get_system_prompt(profil_dict, req.language)}]
    for msg in req.history[-10:]:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.message})

    reply = await groq_request(messages)
    if not reply:
        reply = "Maaf, SkillSync AI belum tersedia. Pastikan GROQ_API_KEY sudah diset di file .env (gratis di console.groq.com)."

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

@app.post("/chat-advisory", tags=["Advisory"])
@api_router.post("/chat-advisory", tags=["Advisory"])
@api_router_index.post("/chat-advisory", tags=["Advisory"])
async def chat_advisory(req: AdvisoryRequest):
    lang_instruction = "CRITICAL: TRANSLATE YOUR ENTIRE RESPONSE TO ENGLISH. Keep the JSON keys exactly the same, but translate all the values to English." if req.language == "en" else ""
    fase_label = "Step 1" if req.language == "en" else "Langkah 1"
    prompt = f"""Kamu adalah AI Career Advisor...
{lang_instruction}
User Readiness Score: {req.readiness_score}%
Target Pekerjaan: {req.target_job}
Skill yang kurang: {', '.join(req.skill_gap) if req.skill_gap else 'Tidak ada, sudah memenuhi kriteria dasar.'}

Pesan dari user: "{req.user_reply}"

TUGASMU:
Berikan respons yang menyesuaikan dengan pesan user. 
PENTING: Roadmap yang kamu buat harus mencakup **semua skill yang kurang (skill_gap)** secara berurutan, kecuali jika user secara eksplisit HANYA ingin fokus pada 1 skill saja.
Jika user bilang "yang paling mudah dulu" atau sejenisnya, susun roadmap dari skill yang paling dasar/mudah hingga yang paling susah, tapi TETAP masukkan semua skill yang kurang ke dalam langkah-langkahnya.
Jika pesan user di luar konteks karir, tegur dengan sopan dan kembalikan flashcards kosong.

WAJIB return format JSON murni:
{{
  "ai_response": "Balasan hangat dan semangat dari kamu...",
  "flashcards": [
    {{"fase": "{fase_label}", "nama": "Judul Langkah", "skill": ["Skill Fokus"], "kursus": "Saran Kursus/Platform", "milestone": "Target hasil langkah ini"}},
    {{"fase": "{fase_label.replace('1', '2')}", "nama": "...", "skill": ["..."], "kursus": "...", "milestone": "..."}}
  ]
}}"""

    messages = [
        {"role": "system", "content": "Jawab HANYA JSON valid. Tidak ada teks markdown di luar blok JSON."},
        {"role": "user", "content": prompt}
    ]

    ai_resp = await groq_request(messages, response_format={"type": "json_object"})
    
    if not ai_resp:
        return {
            "ai_response": "Maaf, sistem AI sedang sibuk. Coba beberapa saat lagi.",
            "flashcards": []
        }
        
    try:
        parsed = json.loads(ai_resp)
        return parsed
    except Exception as e:
        logger.error(f"Failed to parse JSON chat_advisory: {e}")
        return {
            "ai_response": "Maaf, terjadi kesalahan pada pemrosesan AI.",
            "flashcards": []
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

# ── ANALYZE JOB v2: LLM menilai per-item, KODE yang menghitung skor ───────
# Filosofi: skor yang konsisten dan bisa dijelaskan tidak boleh lahir dari
# kreatifitas LLM. LLM hanya boleh: (A) ekstrak struktur lowongan,
# (B) nilai tiap requirement dengan bukti dari CV. Angka final dihitung
# formula deterministik di bawah, termasuk aturan hard filter.

def _extract_json(raw: Optional[str]) -> Optional[dict]:
    if not raw:
        return None
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    # qwen3.x "thinking mode" menyembur blok <think>...</think> sebelum jawaban
    cleaned = re.sub(r"<think(?:ing)?>.*?</think(?:ing)?>", "", cleaned, flags=re.DOTALL | re.IGNORECASE).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end + 1])
            except Exception:
                return None
    return None


async def _groq_json(messages: list, max_tokens: int = 1200, model: Optional[str] = None) -> Optional[dict]:
    """Groq call dengan response_format JSON + 1x retry parsing."""
    for _ in range(2):
        raw = await groq_request(
            messages,
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
            temperature=0.1,
            timeout=25,
            model=model,
        )
        parsed = _extract_json(raw)
        if parsed:
            return parsed
    return None


def _strict_skills_match(user_skill: str, target_skill: str) -> bool:
    """
    Match skill tanpa false positive substring pendek.
    skills_match() umum memakai substring dua arah, sehingga 'java' cocok dengan
    'javascript' dan 'go' cocok dengan 'mongodb'. Untuk penilaian skor yang
    dikredit ke user, kecocokan harus exact, sinonim, atau substring panjang.
    """
    u, t = normalize_skill(user_skill), normalize_skill(target_skill)
    if u == t:
        return True
    if min(len(u), len(t)) >= 5 and (u in t or t in u):
        return True
    for canon, synonyms in SKILL_SYNONYMS.items():
        all_terms = [canon] + synonyms

        def hit(s: str) -> bool:
            return any(
                x == s or (len(x) >= 5 and len(s) >= 5 and (x in s or s in x))
                for x in all_terms
            )

        if hit(u) and hit(t):
            return True
    return False


def _skill_in_text(skill: str, text: str) -> bool:
    """Cek kehadiran nama skill di teks CV mentah (word boundary, tanpa tanda kurung)."""
    s = normalize_skill(skill)
    s = re.sub(r"\(.*?\)", "", s).strip(" .:-")
    if len(s) < 3:
        return False
    return re.search(r"\b" + re.escape(s) + r"\b", text, re.IGNORECASE) is not None


def _machine_skill_status(skill: str, cv_skill_pool: list, cv_text: str = "") -> str:
    """
    Penilaian skill deterministik: sinonim -> met, transferable -> partial.
    Jaring pengaman non-IT: skill yang tidak dikenali daftar tapi TERTULIS
    di CV asli minimal partial (daftar skill Stage B bisa miss untuk
    kosakata di luar teknologi).
    """
    for cs in cv_skill_pool:
        if _strict_skills_match(cs, skill):
            return "met"
    for cs in cv_skill_pool:
        if is_transferable(cs, skill):
            return "partial"
    if cv_text and _skill_in_text(skill, cv_text):
        return "partial"
    return "missing"


# ── SANITIZER EKSTRAKSI (penjaga di kode, prompt boleh gagal tapi ini tidak) ──
# Work arrangement & logistik kerja bukan gap yang bisa user aksikan.
WORK_MODE_RE = re.compile(
    r"\b(on.?site|onsite|hybrid|remote|wfo|wfa|work from (office|home)|"
    r"full.?time|part.?time|kontrak|contract|freelance|magang|internship|"
    r"relokasi|relocat(e|ion)|kantor|office location|jakarta|bandung|surabaya|"
    r"gaji|salary|benefit|bpjs kesehatan|thr|bonus|jam kerja|working hours)\b",
    re.IGNORECASE,
)
# Kata sifat/kalimat pembuka yang membuat nama skill jadi verbose.
SKILL_ADJ_RE = re.compile(
    r"^(strong|good|excellent|proficient|solid|advanced|basic|deep|"
    r"familiar(ity)?( with)?|experience(d)? (with|in)?|knowledge of|"
    r"skills? (in|of|with)|menguasai|ahli (dalam|di)?|expert(ise)?( in)?|"
    r"pemahaman tentang|understanding of|pengalaman (dengan|di)|min\.?|minimal|"
    r"kemampuan|ability to)\s+",
    re.IGNORECASE,
)


def _clean_skill_name(s: str) -> str:
    out = s.strip()
    prev = None
    while prev != out:
        prev = out
        out = SKILL_ADJ_RE.sub("", out).strip(" .:-,")
    return out


def _sanitize_skill_list(skills: list, max_items: int) -> list:
    """Bersihkan nama skill: buang noise, kata sifat, duplikat, dan terlalu panjang."""
    seen = set()
    cleaned = []
    for raw in skills:
        if not isinstance(raw, str):
            continue
        s = _clean_skill_name(raw)
        if not s or len(s) < 2 or len(s) > 40 or WORK_MODE_RE.search(s):
            continue
        if re.match(r"^[a-z]/[a-z]$", s.lower()):  # fragment aneh spt "and/or"
            continue
        key = normalize_skill(s)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(s)
        if len(cleaned) >= max_items:
            break
    return cleaned


def _sanitize_other_requirements(others: list) -> list:
    """Hanya kondisi yang bisa user aksikan: bahasa, sertifikasi wajib, dsb."""
    kept = []
    for raw in others:
        if not isinstance(raw, str) or not raw.strip():
            continue
        if WORK_MODE_RE.search(raw):
            continue
        kept.append(raw.strip()[:120])
        if len(kept) >= 4:
            break
    return kept


def _years_ratio_score(years: Optional[float], min_years: Optional[float]) -> Optional[float]:
    """Band pengalaman: penuh / 0.6 / 0.3 / 0. None kalau tidak bisa dinilai."""
    if min_years is None or min_years <= 0:
        return 1.0   # tidak ada syarat pengalaman -> netral penuh
    if years is None:
        return None  # akan fallback ke penilaian LLM
    ratio = years / min_years
    if ratio >= 1.0:
        return 1.0
    if ratio >= 0.7:
        return 0.6
    if ratio >= 0.4:
        return 0.3
    return 0.0


def _items_pct(statuses: list) -> Optional[float]:
    """Persentase item: met=1.0, partial=0.5. None kalau kosong (netral)."""
    if not statuses:
        return None
    return sum(1.0 if s == "met" else 0.5 if s == "partial" else 0.0 for s in statuses) / len(statuses)


def _plain_dashes(s: Optional[str]) -> Optional[str]:
    """Ganti em-dash/en-dash/non-breaking hyphen dengan tanda hubung biasa.
    Output LLM tidak boleh mengandung karakter dash mewah."""
    if not isinstance(s, str):
        return s
    return (
        s.replace("\u2014", " - ")   # em dash
         .replace("\u2013", "-")     # en dash
         .replace("\u2012", "-")
         .replace("\u2011", "-")     # non-breaking hyphen
         .replace("\u2015", "-")
    )


async def analyze_job_v2(cv: str, job_title: str, job_desc: str) -> Optional[dict]:
    # ── STAGE A: ekstraksi struktur lowongan ───────────────────────────────
    stage_a_prompt = f"""You are a strict requirement extractor for job postings.
Extract ONLY what is explicitly stated. Never invent or infer.

Job title: {job_title}

Job description:
{job_desc}

Return ONLY valid JSON with this exact shape:
{{
  "seniority": "junior|mid|senior|lead|any",
  "min_years": 3,
  "must_skills": ["concrete technical/professional skills explicitly required, 3-8 items, each 1-3 words, canonical names only (e.g. 'Go', 'Kubernetes', 'PostgreSQL', 'SQL'), never sentences, never adjectives like 'strong/proficient'"],
  "plus_skills": ["nice-to-have skills, 0-8 items, same format"],
  "education_requirement": "ONE string quoting the education requirement, or null if none stated. If the posting lists alternatives (e.g. 'Statistics, Public Health, or related field'), keep them as ONE requirement with alternatives, NOT separate items.",
  "industry_requirement": "specific industry background if required, else null",
  "other_requirements": ["hard conditions the candidate must satisfy and can act on: language, mandatory certification, shift availability. 0-4 items. NEVER include work arrangement (on-site/hybrid/remote/WFO/WFA), work hours type (full-time/contract), office location, salary, or benefits - those are job metadata, not requirements."],
  "work_arrangement": "onsite, hybrid, remote, or null - informational only, never judged",
  "ats_keywords": ["5-8 exact searchable phrases appearing in the posting"]
}}
min_years must be a number or null (null if not stated)."""

    stage_a = await _groq_json([
        {"role": "system", "content": "Reply ONLY with valid JSON. No other text."},
        {"role": "user", "content": stage_a_prompt},
    ], max_tokens=700, model=MODEL_EXTRACT)
    if not stage_a:
        return None

    must_skills = _sanitize_skill_list(stage_a.get("must_skills", []), max_items=8)
    plus_skills = _sanitize_skill_list(stage_a.get("plus_skills", []) or [], max_items=6)
    # edukasi: satu syarat utuh (alternatif "atau" tidak dipecah jadi item terpisah)
    education_req = stage_a.get("education_requirement")
    if not isinstance(education_req, str) or not education_req.strip():
        # kompatibilitas kalau LLM masih balikin list
        legacy = [s for s in stage_a.get("education_requirements", []) if isinstance(s, str)]
        education_req = " atau ".join(legacy) if legacy else None
    other_reqs = _sanitize_other_requirements(stage_a.get("other_requirements", []))
    industry_req = stage_a.get("industry_requirement") or None
    min_years = stage_a.get("min_years")
    if not isinstance(min_years, (int, float)) or min_years < 0:
        min_years = None
    ats_keywords = [k for k in stage_a.get("ats_keywords", []) if isinstance(k, str)][:8]

    # ── STAGE B: penilaian per-item oleh LLM (non-skill; skill dinilai mesin) ──
    items_to_judge = []
    if min_years:
        items_to_judge.append({
            "req": f"Minimal {min_years} tahun pengalaman kerja relevan",
            "type": "experience",
        })
    if education_req:
        items_to_judge.append({"req": education_req, "type": "education"})
    if industry_req:
        items_to_judge.append({"req": f"Pengalaman industri {industry_req}", "type": "industry"})
    for o in other_reqs:
        items_to_judge.append({"req": o, "type": "other"})

    stage_b_prompt = f"""You are a strict but fair CV auditor.
You receive a CV and non-skill requirements extracted from a job posting.
Technical SKILLS are scored separately by machine, do NOT judge them here.

Tasks:
1. Estimate the candidate's total years of professional experience from the CV. "cv_years_estimate" MUST be a JSON NUMBER (e.g. 2.5), never a string. Internships count as 0.5.
2. List ALL concrete skills evidenced in the CV, in ANY domain or industry, including skills clearly implied by stated tools (Laravel implies PHP, React implies JavaScript). Include Indonesian terms exactly as written (e.g. "BPJS", "K3", "STR", "rekrutmen", "payroll", "penggajian") plus certifications, licenses, tools, and administrative skills. 5-20 items. NEVER invent a skill that has no textual basis in the CV.
3. Judge each item in "items_to_judge": status met/partial/missing based on CV evidence.
   - "req": quote or translate the requirement into natural Indonesian, keep it specific (never generic).
   - "detail": ONE sentence in Bahasa Indonesia citing concrete evidence from the CV.

CV:
{cv[:6000]}

items_to_judge:
{json.dumps(items_to_judge, ensure_ascii=False)}

Return ONLY valid JSON:
{{
  "cv_years_estimate": 1.5,
  "cv_skills": ["SQL", "Excel"],
  "seniority_level": "Entry Level|Mid Level|Senior|Lead",
  "seniority_fit": "satu kalimat Bahasa Indonesia membandingkan pengalaman CV dengan syarat lowongan",
  "items": [
    {{"req": "...", "type": "experience|education|industry|other", "status": "met|partial|missing", "detail": "..."}}
  ]
}}
If items_to_judge is empty, return an empty "items" list."""

    stage_b = await _groq_json([
        {"role": "system", "content": "Reply ONLY with valid JSON. No other text."},
        {"role": "user", "content": stage_b_prompt},
    ], max_tokens=2000, model=MODEL_JUDGE)
    if not stage_b:
        return None

    cv_years = stage_b.get("cv_years_estimate")
    if isinstance(cv_years, str):
        # LLM kadang balikin "2.5" atau "2,5 tahun" -> paksa jadi number
        try:
            cv_years = float(re.sub(r"[^0-9.,]", "", cv_years).replace(",", "."))
        except (ValueError, TypeError):
            cv_years = None
    if not isinstance(cv_years, (int, float)) or isinstance(cv_years, bool) or cv_years < 0:
        cv_years = None
    cv_skill_pool = list(dict.fromkeys(
        [s for s in stage_b.get("cv_skills", []) if isinstance(s, str)]
        + regex_extract_skills(cv)
    ))

    # ── STAGE C: skor dihitung kode (deterministik) ────────────────────────
    must_status = {s: _machine_skill_status(s, cv_skill_pool, cv) for s in must_skills}
    plus_status = {s: _machine_skill_status(s, cv_skill_pool, cv) for s in plus_skills}

    # pengalaman: pakai band tahun bila angka tersedia, else status LLM
    b_items = [i for i in stage_b.get("items", []) if isinstance(i, dict)]
    exp_items = [i for i in b_items if i.get("type") == "experience"]
    exp_score = _years_ratio_score(cv_years, min_years)
    if exp_score is None and exp_items:
        exp_score = {"met": 1.0, "partial": 0.5}.get(exp_items[0].get("status"), 0.0)
    if exp_score is None:
        exp_score = 0.5  # tidak ada data -> netral konservatif

    edu_items = [i for i in b_items if i.get("type") == "education"]
    edu_score = _items_pct([i.get("status") for i in edu_items])
    if edu_score is None:
        edu_score = 1.0  # tidak ada syarat edukasi -> netral penuh

    must_score = _items_pct(list(must_status.values()))
    if must_score is None:
        must_score = 1.0
    # keselarasan industri dihitung sebagai bobot wajib: pivot industri
    # (mis. sales analysis -> health analysis) harus menurunkan skor
    industry_items = [i for i in b_items if i.get("type") == "industry"]
    if industry_items:
        ind_score = _items_pct([i.get("status") for i in industry_items])
        if ind_score is not None:
            must_score = (must_score + ind_score) / 2
    plus_score = _items_pct(list(plus_status.values()))
    if plus_score is None:
        plus_score = 1.0

    combined = 0.25 * exp_score + 0.45 * must_score + 0.15 * plus_score + 0.15 * edu_score
    readiness = round(combined * 100)

    # hard filter: requirement keras yang jelas-jelas tidak terpenuhi
    hard_messages = []
    if (
        min_years and cv_years is not None
        and cv_years < 0.5 * float(min_years)
    ):
        readiness = min(readiness, 55)
        hard_messages.append(
            f"Syarat {min_years} tahun pengalaman belum terpenuhi (terbaca sekitar {cv_years:g} tahun di CV)."
        )
    if education_req and edu_items and all(i.get("status") == "missing" for i in edu_items):
        readiness = min(readiness, 60)
        hard_messages.append("Syarat pendidikan tidak terpenuhi.")

    # ── rakit requirements_check (skill dari mesin, lainnya dari LLM) ──────
    requirements_check = []

    def skill_item(skill: str, status: str, is_plus: bool) -> dict:
        label = f"{skill} (nilai plus)" if is_plus else skill
        if status == "met":
            detail = f"'{skill}' terbukti ada di CV kamu."
        elif status == "partial":
            detail = f"'{skill}' belum ada di CV, tapi skill terkait yang kamu punya bisa jadi modal transisi."
        else:
            detail = f"'{skill}' tidak ditemukan di CV kamu."
        return {"req": label, "status": status, "detail": detail}

    for i in b_items:
        if i.get("type") in ("experience", "education", "industry", "other"):
            requirements_check.append({
                "req": i.get("req", ""),
                "status": i.get("status", "missing"),
                "detail": i.get("detail", ""),
            })
    for s in must_skills:
        requirements_check.append(skill_item(s, must_status[s], is_plus=False))
    for s in plus_skills:
        requirements_check.append(skill_item(s, plus_status[s], is_plus=True))
    requirements_check = requirements_check[:12]

    matched = [s for s, st in must_status.items() if st == "met"][:10]
    matched_plus = [s for s, st in plus_status.items() if st == "met"][:8]
    missing_must = [s for s, st in must_status.items() if st != "met"]
    missing = (missing_must + [s for s, st in plus_status.items() if st == "missing"])[:8]

    # advice: dirakit dari data, bukan karangan LLM
    if hard_messages:
        verdict = "Belum layak apply dulu. " + " ".join(hard_messages)
        action = f"Prioritaskan menutup gap: {', '.join(missing_must[:3])}." if missing_must else "Bangun pengalaman yang diminta lowongan ini dulu."
    elif readiness >= 70:
        verdict = "Kamu cukup siap apply ke posisi ini."
        action = (
            f"Sebelum kirim, sisipkan keyword ATS: {', '.join(ats_keywords[:5])}."
            if ats_keywords else "Perkuat bagian CV yang paling relevan dengan lowongan ini."
        )
    elif readiness >= 45:
        verdict = "Layak dicoba, tapi perbaiki dulu sebelum apply."
        action = (
            f"Fokus tutup gap: {', '.join(missing_must[:3])}. " if missing_must else ""
        ) + (f"Sisipkan keyword ATS: {', '.join(ats_keywords[:5])}." if ats_keywords else "")
    else:
        verdict = "Jarak kamu dengan lowongan ini masih besar."
        action = (
            f"Prioritaskan belajar: {', '.join(missing_must[:3])}. " if missing_must else ""
        ) + "Pertimbangkan juga posisi serupa dengan level lebih junior."
    advice = f"{verdict} {action}".strip()

    # ── STAGE D: narasi manusiawi (verdict & skor SUDAH final dari mesin) ──
    # Mesin memutuskan, LLM hanya bercerita: detail per item + paragraf sintesis.
    # Gagal -> tetap pakai detail template (fallback), skor tidak tersentuh.
    synthesis = None
    if requirements_check:
        stage_d_prompt = f"""You are an honest senior career coach writing for an Indonesian job seeker.
You receive a CV and a FINAL list of requirement verdicts (statuses were decided by a machine audit).

Tasks:
1. For EACH requirement, write a natural 1-2 sentence explanation in Bahasa Indonesia that DISCUSSES the verdict in the context of the candidate's actual career story: their industry, their experience level, what transfers over and what does not.
2. Write one synthesis paragraph (2-3 sentences) that OPENS by framing the position naturally, e.g. "Lowongan ini mid-level di industri kesehatan, dan kamu hampir siap di sisi analisis...". Then name the candidate's real strengths, the main gap (industry direction? depth? tools?), and the bridge (what they already have that helps close it).

STYLE (this is the core of your job):
- DISCUSS, do not restate. Compare their background with what the role needs.
- GOOD, for a sales analyst missing healthcare industry: "Analisis data kamu sudah jalan di konteks sales, dan metodenya (SQL, Tableau, forecasting) tetap terpakai di healthcare. Yang belum kamu punya adalah cara kerja data klinis dan regulasi rumah sakit, itu yang perlu dipelajari duluan."
- BAD (forbidden, mere restatement): "Andi belum memiliki pengalaman di industri kesehatan."
- For career-pivot or industry-mismatch items, always name the transferable part first, then the gap.
- For 'met' items: one short confident sentence pointing at where it shows in their background.

STRICT RULES:
- The statuses are FINAL. NEVER contradict them and NEVER soften a 'missing' into something positive.
- Each detail under 320 characters. Synthesis under 500 characters.
- Use "kamu" (second person), not the candidate's name.
- "details" array must contain EXACTLY {len(requirements_check)} items in the same order as the requirements given.

Job: {job_title}

CV:
{cv[:4000]}

Requirements (final, in order):
{json.dumps([{"req": r["req"], "status": r["status"]} for r in requirements_check], ensure_ascii=False)}

Return ONLY valid JSON:
{{
  "synthesis": "...",
  "details": ["...", "..."]
}}"""

        stage_d = await _groq_json([
            {"role": "system", "content": "Reply ONLY with valid JSON. No other text."},
            {"role": "user", "content": stage_d_prompt},
        ], max_tokens=1600, model=MODEL_NARRATE)
        if stage_d:
            details = [d for d in stage_d.get("details", []) if isinstance(d, str)]
            if len(details) == len(requirements_check):
                for item, new_detail in zip(requirements_check, details):
                    if new_detail.strip():
                        item["detail"] = _plain_dashes(new_detail.strip())[:400]
            raw_synthesis = stage_d.get("synthesis")
            if isinstance(raw_synthesis, str) and raw_synthesis.strip():
                synthesis = _plain_dashes(raw_synthesis.strip())[:600]

    return {
        "readiness_score": readiness,
        "seniority_level": stage_b.get("seniority_level", ""),
        "seniority_fit": _plain_dashes(stage_b.get("seniority_fit", "")),
        "requirements_check": requirements_check,
        "matched_skills": matched,
        "matched_plus_skills": matched_plus,
        "missing_skills": missing,
        "ats_keywords": ats_keywords,
        "advice": advice,
        "synthesis": synthesis,
        "score_breakdown": {
            "experience": {"score": round(exp_score * 100), "weight": 25},
            "must_skills": {"score": round(must_score * 100), "weight": 45},
            "plus_skills": {"score": round(plus_score * 100), "weight": 15},
            "education": {"score": round(edu_score * 100), "weight": 15},
        },
        "hard_filter": {
            "triggered": bool(hard_messages),
            "message": " ".join(hard_messages) if hard_messages else None,
        },
        "cv_years_estimate": cv_years,
        "min_years_required": min_years,
        "scoring_version": 2,
    }


async def analyze_job_legacy(cv: str, job_title: str, job_desc: str) -> Optional[dict]:
    """Fallback satu-panggilan (arsitektur lama) kalau Stage A/B gagal."""
    prompt = f"""You are an AI Career Copilot. Analyze how well this candidate fits the job.

Job Title: {job_title}
Job Description:
{job_desc}

Candidate CV:
{cv}

YOUR TASK: You are a STRICT, LITERAL Auditor. Evaluate the candidate against the Job Description (JD).

STEP 1: Identify HARD requirements directly from the JD text. Do NOT infer or invent. Extract exact phrases for:
- Minimum years of experience (e.g. "3-5 years of experience")
- Specific domain knowledge (e.g. "NPL forecasting", "credit scoring development")
- Specific tools, platforms, or data sources (e.g. "SQL", "SLIK")
- Education or Languages (e.g. "Fluent in English")

STEP 2: Evaluate the CV against these exact requirements. Be brutally honest. If it's missing, say it's missing.

Return JSON with these fields:

1. "_thought_process": A brief string where you list the exact hard requirements you found in the text.
2. "readiness_score" (0-100): Overall honest fit score. Be harsh. If they lack the required years of experience, the score should be low (<60).
3. "seniority_level": A very short label indicating the seniority of the role (e.g. "Entry Level", "Mid Level", "Senior", "Lead").
4. "seniority_fit": ONE short sentence evaluating their years of experience vs the exact requirement. Use "Lowongan ini", DO NOT use the acronym "JD".
5. "requirements_check": Array of 5-7 MOST IMPORTANT HARD REQUIREMENTS.
   - "req": MUST BE A DIRECT TRANSLATION/QUOTE. (e.g., "3-5 tahun pengalaman financial analytics"). NEVER use generic words.
   - "status": "missing", "met", or "partial".
   - "detail": ONE sentence in Bahasa Indonesia explaining WHY based on the CV. Use "Lowongan ini" instead of "JD".

6. "matched_skills": Array of concrete technical tools (e.g., "SQL") EXPLICITLY MENTIONED that are ALSO in the CV.
7. "missing_skills": Array of concrete technical tools EXPLICITLY MENTIONED that are MISSING from the CV. NEVER list tools that are not requested. If none, return [].
8. "ats_keywords": 3-5 exact phrases for ATS screening.
9. "advice": 2-3 sentences in Bahasa Indonesia. Brutally honest advice about their gaps.

CRITICAL RULES:
- DO NOT use the acronym "JD" in your Indonesian response. Use "Lowongan ini" or "Posisi ini".
- If a tool/skill is in the CV but NOT requested, DO NOT put it in matched_skills.
- If a tool/skill is NOT in the JD, DO NOT put it in missing_skills.
- "req" MUST be literal requirements from the JD. Do not generalize (e.g., write "Credit scoring development" instead of "Pengalaman Data Analyst").


Reply ONLY in valid JSON:
{{
  "_thought_process": "Requires: 3-5 years financial analytics, credit scoring, SQL, SLIK. CV has: 1 year sales ops, SQL, no credit scoring.",
  "readiness_score": 40,
  "seniority_level": "Mid Level",
  "seniority_fit": "Lowongan ini mensyaratkan 3-5 tahun pengalaman, sedangkan kamu baru memiliki pengalaman sekitar 1 tahun.",
  "requirements_check": [
    {{"req": "3-5 tahun pengalaman financial analytics", "status": "missing", "detail": "Kamu belum memenuhi syarat 3-5 tahun pengalaman; CV-mu menunjukkan 1 tahun di sales operations."}},
    {{"req": "Pengalaman credit scoring development", "status": "missing", "detail": "Tidak ada rekam jejak pengembangan credit scoring di CV kamu."}},
    {{"req": "Profisiensi SQL", "status": "met", "detail": "SQL tercantum kuat dalam pengalaman kerjamu."}}
  ],
  "matched_skills": ["SQL"],
  "missing_skills": ["SLIK"],
  "ats_keywords": ["credit scoring", "NPL forecasting", "financial analysis"],
  "advice": "..."
}}"""

    ai_resp = await groq_request(
        [{"role": "system", "content": "Reply ONLY with valid JSON. No other text."},
         {"role": "user", "content": prompt}],
        response_format={"type": "json_object"}, max_tokens=1200,
        model=MODEL_EXTRACT,
    )
    if not ai_resp:
        return None
    parsed = _extract_json(ai_resp)
    if not parsed:
        logger.error("analyze_job_legacy: gagal parsing JSON")
        return None
    return parsed


@app.post("/analyze-job", tags=["Extension"])
@api_router.post("/analyze-job", tags=["Extension"])
@api_router_index.post("/analyze-job", tags=["Extension"])
async def analyze_job(req: AnalyzeJobRequest):
    # 8000 karakter: LinkedIn sering menaruh section Requirements di akhir
    # postingan; 4000 memotong syarat lowongan dan merusak ekstraksi Stage A.
    cv = req.cv_text[:8000]
    job_title = req.job_title[:200]
    job_desc = req.job_description[:8000]

    result = await analyze_job_v2(cv, job_title, job_desc)
    if result is None:
        logger.warning("analyze-job v2 gagal, fallback ke legacy prompt")
        result = await analyze_job_legacy(cv, job_title, job_desc)
    if result is None:
        return {
            "error": "Server AI sedang sibuk (kemungkinan kena limit sesaat). "
                     "Tunggu sekitar 30 detik lalu coba lagi."
        }

    # Log scan anonim untuk Skillsy Index: TANPA teks CV, tanpa identitas.
    # Fire-and-forget: tidak pernah memperlambat atau menggagalkan respons.
    try:
        asyncio.create_task(supabase_insert("scans", {
            "job_title": job_title[:200],
            "seniority": result.get("seniority_level") or None,
            "readiness_score": result.get("readiness_score"),
            "min_years_required": result.get("min_years_required"),
            "must_skills": [s.get("req") for s in (result.get("requirements_check") or [])][:12],
            "missing_skills": result.get("missing_skills") or [],
        }, ignore_dupes=True))
    except Exception as e:
        logger.warning(f"scan log skip: {e}")

    return result

class CoverLetterRequest(BaseModel):
    cv_text: str = Field(..., min_length=50, max_length=150000)
    job_title: str = Field(..., min_length=1, max_length=1000)
    job_description: str = Field(..., min_length=30, max_length=150000)
    company_name: str = ""

@app.post("/generate-cover-letter", tags=["Extension"])
@api_router.post("/generate-cover-letter", tags=["Extension"])
@api_router_index.post("/generate-cover-letter", tags=["Extension"])
async def generate_cover_letter(req: CoverLetterRequest):
    cv = req.cv_text[:3000]
    job_title = req.job_title[:200]
    job_desc = req.job_description[:2500]

    company_name = req.company_name.strip() or "perusahaan ini"

    prompt = f"""Tulis cover letter profesional dalam Bahasa Indonesia untuk posisi "{job_title}" di {company_name}.

CV Kandidat:
{cv}

Deskripsi Pekerjaan:
{job_desc}

ATURAN PENULISAN:
- Tulis dalam 3 paragraf yang mengalir natural:
  1. Pembuka: Sebut posisi dan perusahaan yang BENAR yaitu "{company_name}", tunjukkan antusias yang spesifik
  2. Isi: Highlight 2-3 skill/pengalaman dari CV yang paling relevan dengan JD
  3. Penutup: Call to action yang percaya diri
- CRITICAL: Jangan sebut nama perusahaan lain selain "{company_name}". Jangan mengarang nama perusahaan.
- Nada: Profesional, percaya diri, hangat
- Panjang: 180-230 kata, tidak lebih
- Gunakan "Saya" sebagai sapaan diri
- Jangan sebut nama kandidat atau nominal gaji
- Jangan pakai template generic

Tulis HANYA teks cover letter-nya langsung. Tidak ada label, tidak ada markdown."""

    messages = [
        {"role": "system", "content": "Kamu adalah career coach berpengalaman. Tulis cover letter langsung tanpa embel-embel."},
        {"role": "user", "content": prompt}
    ]

    result = await groq_request(messages, max_tokens=600, temperature=0.7, timeout=25)
    if not result:
        return {"error": "Gagal generate cover letter. Coba lagi."}

    return {"cover_letter": result}

# ── MAIN ──────────────────────────────────────────────────────────────────
app.include_router(api_router)
app.include_router(api_router_index)

# ── STATIC PAGES ──────────────────────────────────────────────────────────
# Semua route statis WAJIB methods GET+HEAD: crawler (Googlebot dsb.) mengirim
# HEAD dulu sebelum GET; @app.get saja tidak menerima HEAD di FastAPI, dan
# request jatuh ke catch-all 404 yang merusak indeksasi SEO.
def _serve_static(file_name: str, media_type: str = None):
    file_path = pathlib.Path(__file__).parent.parent / file_name
    if file_path.exists():
        return FileResponse(file_path, media_type=media_type) if media_type else FileResponse(file_path)
    return JSONResponse(status_code=404, content={"detail": f"{file_name} not found on disk"})

@app.api_route("/", methods=["GET", "HEAD"])
def serve_index():
    return _serve_static("index.html", media_type="text/html")

@app.api_route("/investor.html", methods=["GET", "HEAD"])
async def serve_investor():
    return _serve_static("investor.html", media_type="text/html")

@app.api_route("/privacy.html", methods=["GET", "HEAD"])
async def serve_privacy():
    return _serve_static("privacy.html", media_type="text/html")

@app.api_route("/demo.html", methods=["GET", "HEAD"])
async def serve_demo():
    return _serve_static("demo.html", media_type="text/html")

@app.api_route("/sigap-engine.html", methods=["GET", "HEAD"])
async def serve_engine():
    return _serve_static("sigap-engine.html", media_type="text/html")

@app.api_route("/og-1200x630.png", methods=["GET", "HEAD"])
def serve_og():
    return _serve_static("social/og-1200x630.png", media_type="image/png")

@app.api_route("/extension/pdf.min.js", methods=["GET", "HEAD"])
def serve_pdf_js():
    return _serve_static("extension/pdf.min.js", media_type="application/javascript")

@app.api_route("/extension/pdf.worker.min.js", methods=["GET", "HEAD"])
def serve_pdf_worker():
    return _serve_static("extension/pdf.worker.min.js", media_type="application/javascript")

@app.api_route("/logo.svg", methods=["GET", "HEAD"])
def serve_logo():
    return _serve_static("logo.svg", media_type="image/svg+xml")

@app.api_route("/screenshot.png", methods=["GET", "HEAD"])
def serve_screenshot():
    return _serve_static("screenshot.png", media_type="image/png")

@app.api_route("/robots.txt", methods=["GET", "HEAD"])
def serve_robots():
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Sitemap: https://skillsy.my.id/sitemap.xml\n"
    )
    return Response(content=content, media_type="text/plain")

@app.api_route("/sitemap.xml", methods=["GET", "HEAD"])
def serve_sitemap():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://skillsy.my.id/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>
  <url><loc>https://skillsy.my.id/investor.html</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.3</priority></url>
</urlset>"""
    return Response(content=xml, media_type="application/xml")

class WaitlistRequest(BaseModel):
    email: str

@app.post("/waitlist", tags=["Waitlist"])
@api_router.post("/waitlist", tags=["Waitlist"])
@api_router_index.post("/waitlist", tags=["Waitlist"])
async def join_waitlist(req: WaitlistRequest):
    email = req.email.strip().lower()
    if SUPABASE_ON:
        saved = await supabase_insert("waitlist", {"email": email}, ignore_dupes=True)
        if saved:
            logger.info(f"WAITLIST tersimpan di Supabase: {email}")
            return {"status": "success", "message": "Email added to waitlist"}
        logger.warning(f"WAITLIST gagal insert Supabase, fallback log: {email}")
    logger.info(f"WAITLIST (log saja, Supabase belum aktif): {email}")
    return {"status": "success", "message": "Email added to waitlist"}

@app.get("/api/ping", tags=["System"])
@api_router.get("/api/ping", tags=["System"])
@api_router_index.get("/api/ping", tags=["System"])
async def ping():
    """Dipanggil cron harian Vercel agar project Supabase free-tier tidak di-pause."""
    ok = await supabase_ping()
    return {"status": "ok", "supabase": ok}

@app.get("/google069a65fad361bad9.html", response_class=PlainTextResponse)
@api_router.get("/google069a65fad361bad9.html", response_class=PlainTextResponse)
@api_router_index.get("/google069a65fad361bad9.html", response_class=PlainTextResponse)
async def google_verification():
    return "google-site-verification: google069a65fad361bad9.html"

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"])
async def catch_all(path_name: str):
    if "google069a65fad361bad9" in path_name:
        return PlainTextResponse("google-site-verification: google069a65fad361bad9.html")
    return JSONResponse(
        status_code=404,
        content={"detail": f"Not Found in catch_all. Path received: {path_name}"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)