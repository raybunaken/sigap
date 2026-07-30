"""
SIGAP — Jobstreet Indonesia Scraper (HTML-based)
Mengambil data lowongan dari halaman search Jobstreet langsung.

URL pattern: https://id.jobstreet.com/{keyword}-jobs/in-Indonesia

Jalankan: python scraper.py
Output  : knowledge_base_scraped.json
"""

import json, asyncio, re, logging
from datetime import datetime
from collections import Counter
from typing import Optional
import httpx
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("sigap.scraper")

DELAY       = 2.0
OUTPUT_FILE = "knowledge_base_scraped.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Job titles → URL slug mapping untuk Jobstreet
JOB_TARGETS = {
    "Data Analyst":            "data-analyst",
    "Data Scientist":          "data-scientist",
    "Data Engineer":           "data-engineer",
    "Machine Learning Engineer": "machine-learning-engineer",
    "Backend Developer":       "backend-developer",
    "Frontend Developer":      "frontend-developer",
    "Full Stack Developer":    "full-stack-developer",
    "Mobile Developer":        "mobile-developer",
    "Software Engineer":       "software-engineer",
    "UI/UX Designer":          "ui-ux-designer",
    "Product Manager":         "product-manager",
    "Digital Marketing":       "digital-marketing",
    "Business Analyst":        "business-analyst",
    "Cloud Engineer":          "cloud-engineer",
    "DevOps Engineer":         "devops-engineer",
}

# Master skill list untuk deteksi dari teks
SKILLS = {
    "Python": [r"\bpython\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript": [r"\btypescript\b"],
    "Java": [r"\bjava\b(?! script)"],
    "Go": [r"\bgolang\b", r"\bgo lang\b"],
    "PHP": [r"\bphp\b"],
    "Kotlin": [r"\bkotlin\b"],
    "Dart": [r"\bdart\b"],
    "SQL": [r"\bsql\b", r"\bmysql\b", r"\bpostgresql\b"],
    "React": [r"\breact\b"],
    "Vue": [r"\bvue\b"],
    "Angular": [r"\bangular\b"],
    "Next.js": [r"\bnext\.?js\b"],
    "Flutter": [r"\bflutter\b"],
    "React Native": [r"\breact native\b"],
    "Node.js": [r"\bnode\.?js\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Django": [r"\bdjango\b"],
    "Laravel": [r"\blaravel\b"],
    "Spring": [r"\bspring boot\b"],
    "Machine Learning": [r"\bmachine learning\b"],
    "Deep Learning": [r"\bdeep learning\b"],
    "TensorFlow": [r"\btensorflow\b"],
    "PyTorch": [r"\bpytorch\b"],
    "Scikit-learn": [r"\bscikit\b"],
    "Pandas": [r"\bpandas\b"],
    "Tableau": [r"\btableau\b"],
    "Power BI": [r"\bpower bi\b"],
    "Google Analytics": [r"\bgoogle analytics\b"],
    "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b"],
    "MongoDB": [r"\bmongodb\b"],
    "Redis": [r"\bredis\b"],
    "AWS": [r"\baws\b", r"\bamazon web services\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle cloud\b"],
    "Azure": [r"\bazure\b"],
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "Git": [r"\bgit\b"],
    "Figma": [r"\bfigma\b"],
    "Excel": [r"\bexcel\b"],
    "REST API": [r"\brest api\b", r"\brestful\b"],
    "Statistik": [r"\bstatistics\b", r"\bstatistik\b"],
    "Komunikasi": [r"\bcommunication\b", r"\bkomunikasi\b"],
    "Problem Solving": [r"\bproblem solving\b"],
    "Bahasa Inggris": [r"\benglish\b"],
    "Agile/Scrum": [r"\bagile\b", r"\bscrum\b"],
    "Linux": [r"\blinux\b"],
    "CI/CD": [r"\bci/cd\b", r"\bgithub actions\b"],
    "Spark": [r"\bapache spark\b", r"\bpyspark\b"],
    "Kafka": [r"\bkafka\b"],
    "Airflow": [r"\bairflow\b"],
    "BigQuery": [r"\bbigquery\b"],
    "Microservices": [r"\bmicroservices\b"],
    "User Research": [r"\buser research\b"],
    "Prototyping": [r"\bprototyping\b"],
    "Wireframing": [r"\bwireframing\b"],
    "SEO": [r"\bseo\b"],
    "Google Ads": [r"\bgoogle ads\b"],
    "Meta Ads": [r"\bmeta ads\b", r"\bfacebook ads\b"],
}

def extract_skills(text: str) -> list:
    text = text.lower()
    found = []
    for skill, patterns in SKILLS.items():
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                found.append(skill)
                break
    return found

async def fetch_page(url: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient(
            headers=HEADERS, timeout=20,
            follow_redirects=True
        ) as client:
            r = await client.get(url)
            logger.info(f"  {r.status_code} → {url}")
            if r.status_code == 200:
                return r.text
            return None
    except Exception as e:
        logger.error(f"  Error: {e}")
        return None

def parse_jobstreet_html(html: str) -> list:
    """
    Parse hasil search Jobstreet dari HTML.
    Jobstreet render job list dalam tag article atau div dengan data-job-id.
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    # Coba berbagai selector yang Jobstreet pakai
    # Method 1: JSON-LD structured data (paling reliable)
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if item.get("@type") == "JobPosting":
                        jobs.append({
                            "title": item.get("title", ""),
                            "description": item.get("description", ""),
                        })
            elif isinstance(data, dict) and data.get("@type") == "JobPosting":
                jobs.append({
                    "title": data.get("title", ""),
                    "description": data.get("description", ""),
                })
        except:
            pass

    # Method 2: Next.js __NEXT_DATA__ (data yang dipakai Jobstreet React)
    if not jobs:
        next_data = soup.find("script", id="__NEXT_DATA__")
        if next_data:
            try:
                data = json.loads(next_data.string)
                # Navigate ke job results
                props = data.get("props", {}).get("pageProps", {})
                job_search = props.get("jobSearchQuery", {})
                results = (
                    props.get("jobs") or
                    props.get("jobSearch", {}).get("jobs") or
                    job_search.get("jobs") or
                    []
                )
                for job in results:
                    jobs.append({
                        "title": job.get("title", ""),
                        "description": " ".join([
                            job.get("teaser", ""),
                            " ".join(job.get("bulletPoints", [])),
                        ]),
                    })
            except Exception as e:
                logger.debug(f"  NEXT_DATA parse error: {e}")

    # Method 3: Fallback — ambil teks dari semua konten
    if not jobs:
        main = soup.find("main") or soup.body
        if main:
            text = main.get_text(separator=" ", strip=True)
            jobs.append({"title": "", "description": text[:5000]})

    return jobs

async def scrape_job(job_name: str, slug: str) -> Optional[dict]:
    logger.info(f"Scraping: {job_name}...")
    all_skills = []
    lokasi_set = set()

    for page in range(1, 4):  # 3 halaman = ~60 lowongan
        url = f"https://id.jobstreet.com/{slug}-jobs/in-Indonesia"
        if page > 1:
            url += f"?pg={page}"

        html = await fetch_page(url)
        if not html:
            break

        jobs = parse_jobstreet_html(html)
        if not jobs:
            logger.warning(f"  Tidak ada job terparse di halaman {page}")
            break

        for job in jobs:
            text = f"{job.get('title','')} {job.get('description','')}"
            skills = extract_skills(text)
            all_skills.extend(skills)

            # Cari lokasi dari teks
            for kota in ["Jakarta", "Bandung", "Surabaya", "Bali", "Remote", "Yogyakarta"]:
                if kota.lower() in text.lower():
                    lokasi_set.add(kota)

        logger.info(f"  Halaman {page}: {len(jobs)} jobs, skill terdeteksi: {len(set(all_skills))}")
        await asyncio.sleep(DELAY)

    if not all_skills:
        return None

    # Hitung frekuensi
    skill_count = Counter(all_skills)
    total = max(len(all_skills) // 5, 1)  # estimasi jumlah job

    skill_wajib = []
    skill_plus  = []
    for skill, count in skill_count.most_common(20):
        pct = count / total
        if pct >= 0.25 and len(skill_wajib) < 6:
            skill_wajib.append(skill)
        elif pct >= 0.10 and len(skill_plus) < 4:
            skill_plus.append(skill)

    lokasi_list = list(lokasi_set) or ["Jakarta"]
    if "Remote" not in lokasi_list:
        lokasi_list.append("Remote")

    logger.info(f"  ✓ Skill wajib: {skill_wajib}")
    return {
        "skill_wajib":     skill_wajib or ["Komunikasi", "Problem Solving"],
        "skill_plus":      skill_plus,
        "skill_frequency": dict(skill_count.most_common(10)),
        "lokasi":          lokasi_list[:4],
        "scraped_at":      datetime.now().isoformat(),
        "source":          f"https://id.jobstreet.com/{slug}-jobs/in-Indonesia",
    }

async def main():
    print("=" * 55)
    print("  SIGAP — Jobstreet Scraper (HTML-based)")
    print("  URL: id.jobstreet.com/{job}-jobs/in-Indonesia")
    print("=" * 55)

    results = {
        "scraped_at": datetime.now().isoformat(),
        "source": "Jobstreet Indonesia",
        "jobs": {}
    }

    success = 0
    for job_name, slug in JOB_TARGETS.items():
        data = await scrape_job(job_name, slug)
        if data:
            results["jobs"][job_name] = data
            success += 1
        else:
            logger.warning(f"  Skip {job_name} — tidak ada data")
        await asyncio.sleep(DELAY)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*55}")
    print(f"  ✓ {success}/{len(JOB_TARGETS)} berhasil")
    print(f"  ✓ Disimpan ke {OUTPUT_FILE}")
    if success == 0:
        print(f"\n  ⚠ Semua gagal — Jobstreet mungkin blokir scraping")
        print(f"  → Coba pakai VPN atau tunggu beberapa jam")
        print(f"  → Sistem tetap jalan dengan knowledge_base.py")
    print(f"{'='*55}")

if __name__ == "__main__":
    asyncio.run(main())