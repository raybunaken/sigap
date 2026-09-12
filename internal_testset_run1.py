# -*- coding: utf-8 -*-
# Internal test set run 1: 5 CV x 2 JD (aligned / misaligned)
import json, urllib.request, time, sys

BASE = "https://skillsy.my.id/api/analyze-job"

def run(label, cv, jd, title):
    body = json.dumps({"cv_text": cv, "job_title": title, "job_description": jd}).encode()
    req = urllib.request.Request(BASE, data=body, headers={"Content-Type": "application/json", "X-Skillsy-Client": "internal-testset-1"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read())
    dt = time.time() - t0
    if d.get("error"):
        print(f"[{label}] ERROR: {d['error'][:70]}")
        return None
    print(f"[{label}] score={d['readiness_score']} yr={d.get('cv_years_estimate')}/{d.get('min_years_required')} hard={d['hard_filter']['triggered']} sen={d.get('seniority_level')}")
    print(f"    matched: {d.get('matched_skills')}")
    print(f"    missing: {d.get('missing_skills')}")
    bd = d.get("score_breakdown") or {}
    print(f"    breakdown: exp={bd.get('experience',{}).get('score')} must={bd.get('must_skills',{}).get('score')} plus={bd.get('plus_skills',{}).get('score')} edu={bd.get('education',{}).get('score')}")
    return d

CV1 = """ANDI PRASETYO
Embedded Systems Engineer
andi.pras@protonmail.com | Bandung | +62 812-3456-7890

SUMMARY
Embedded engineer with 6 years of experience shipping firmware for
industrial IoT devices. Comfortable from schematic review to OTA update
pipeline.

EXPERIENCE
Firmware Engineer - PT Sensorik Nusantara (2021 - Present)
- Developed bare-metal firmware on STM32F4 (C, FreeRTOS) for vibration
  monitoring sensors deployed in 400+ factories
- Cut device boot time by 60% by moving drivers from polling to
  DMA + interrupt architecture
- Built OTA update system over LoRaWAN with signed firmware (AES-128)

Embedded Developer - PT Otomasi Prima (2019 - 2021)
- Programmed PLC-adjacent gateways (Modbus RTU/TCP, RS-485) bridging
  legacy factory machines to MQTT brokers
- Wrote I2C/SPI drivers for custom sensor boards; reduced BOM cost 15%

EDUCATION
D4 Teknik Elektro - Politeknik Negeri Bandung (2015 - 2019)

SKILLS
C, C++, FreeRTOS, STM32, ESP32, Modbus, MQTT, LoRaWAN, I2C, SPI,
KiCad (basic), Git, Python (tooling)"""

JD1A = """Embedded Firmware Engineer - PT Telemetri
Requirements:
- 4+ years embedded firmware development experience
- Strong C/C++ on STM32 or ESP32, FreeRTOS experience
- Experience with wireless protocols (LoRaWAN, MQTT)
- Bachelor degree in Electrical Engineering or related
Nice to have: KiCad, OTA update systems"""

JD1B = """Senior Frontend Engineer - PT Webkreatif
Requirements:
- 3+ years React and TypeScript experience
- Strong CSS and responsive design skills
- Experience with REST API integration
Bachelor degree related field"""

CV2 = """BAYU ANTONI
Site Reliability Engineer
bayu.antoni@gmail.com | Surabaya | WA 0812-9999-8888

SUMMARY
8 years in infrastructure: started as network admin, now SRE. I break
big outages into small runbooks.

EXPERIENCE
SRE - TokoKilat e-commerce (2022 - Present)
- Own Kubernetes (EKS) for 40+ services; cut p99 checkout latency 35%
  by fixing HPA misconfig and connection pool exhaustion
- Built observability stack: Prometheus, Loki, Grafana; on-call MTTR
  down from 90 to 25 minutes
- Wrote Terraform modules now used by 4 squads

Network & System Administrator - PT Telekomunikasi Cabang Jatim
(2016 - 2022)
- Managed 200+ switches/routers (Cisco, Mikrotik), BGP peering with 2 IXs
- Automated config backup with Ansible, saving ~10 engineer-hours/week

GAP
2023: 1 year family care leave (documented), kept skills sharp via
home lab (Proxmox, k3s)

CERTIFICATIONS
CKA (2022), CCNA (2017)

EDUCATION
S1 Teknik Informatika - Universitas Negeri Surabaya (2012 - 2016)

SKILLS
Kubernetes, Terraform, Ansible, AWS (EKS, VPC, IAM), Prometheus,
Grafana, Cisco/Mikrotik, BGP, Bash, Python"""

JD2A = """Site Reliability Engineer - PT Cloudmega
Requirements:
- 5+ years infrastructure/SRE experience
- Strong Kubernetes (EKS) and Terraform skills
- Observability: Prometheus, Grafana
- Relevant certification (CKA preferred)"""

JD2B = """Junior Graphic Designer - PT Kreatif Media
Requirements:
- 1+ year experience with Figma and Adobe Illustrator
- Strong sense of branding and layout
Portfolio required"""

CV3 = """CITRA DEWI
Game Developer | Learning Mobile
citra.dewi.dev@gmail.com | Yogyakarta

RINGKASAN
Game dev 4 tahun dengan Unity (C#). Terakhir bikin game mobile casual
2 juta download. Sekarang fokus pindah ke pengembangan aplikasi mobile
(Flutter sedang dipelajari).

PENGALAMAN
Game Programmer - Studio Gameplay Lokal, Yogyakarta (2022 - Sekarang)
- Nge-code gameplay core 3 game mobile (Unity, C#), total 2 juta+
  download, rating rata-rata 4.5
- Optimasi performa: draw call turun 40%, ukuran build dari 180MB
  jadi 95MB
- Kolaborasi sama artist & desainer level pakai Git + Plastic SCM

Junior Game Dev - PT Disket Interaktif (2020 - 2022)
- Bikin fitur UI/UX in-game, sistem save/load, dan integrasi iklan
  (Unity Ads, AdMob)

PROYEK PRIBADI
Aplikasi mobile tracker keuangan pribadi (Flutter, masuk tahap beta
testing 30 pengguna)

PENDIDIKAN
S1 Informatika - Universitas Atma Jaya Yogyakarta (2016 - 2020)

SKILL
C#, Unity, Flutter (beginner), Git, AdMob, performa optimization,
mobile 2D game"""

JD3A = """Unity Game Developer - Studio Nusantara Games
Requirements:
- 3+ years Unity development with C#
- Shipped mobile games to production
- Performance optimization experience
D3/S1 Informatika atau sederajat"""

JD3B = """Flutter Mobile App Developer - PT Aplikasi Cerdas
Requirements:
- 2+ years professional Flutter development
- Experience publishing apps to Play Store
- REST API integration skills"""

CV4 = """DEWI LESTARI, S.Kep
Perawat Junior (memiliki STR aktif)
dewilestari.kep@gmail.com | Bekasi | 0857-1111-2222

RINGKASAN
Perawat dengan 3 tahun pengalaman di ruang rawat inap dan IGD. Terbiasa
asuhan keperawatan holistik, dokumentasi VIKOR, dan kerja shift.

PENGALAMAN
Perawat Ruang Rawat Inap - RS Umum Kota Bekasi (2022 - Sekarang)
- Merawat 40-60 pasien per shift bersama tim 12 perawat
- Melakukan asuhan keperawatan (askep) lengkap: assessment sampai
  evaluasi, dokumentasi e-OMR
- Anggota tim kredensial rumah sakit; verifikasi STR dan sertifikat
  kompetensi (PPNI) tiap periode
- Menangani pasien BPJS dan umum, koordinasi serah terima shift 3x sehari

Perawat IGD - RSIA Bunda Harapan (2021 - 2022)
- Triage pasien gawat darurat, rata-rata 30 pasien per shift
- Assist dokter jaga saat tindakan darurat (kateter, infus, EKG)

PENDIDIKAN
S1 Keperawatan - Universitas Indonesia Maju (2017 - 2021)
IPK 3.41 | Lulus 100% peserta UKOM

SERTIFIKAT
STR DKI Jakarta (aktif s.d. 2027), Sertifikat PPNI (2022),
Pelatihan PPGD Dasar

KEAHLIAN
Asuhan keperawatan, VIKOR/e-OMR, TTV & EKG, kateterisasi,
komunikasi pasien, kerja shift, Microsoft Office"""

JD4A = """Perawat Ruang Rawat Inap - RS Harapan Sehat
Requirements:
- Minimal 2 tahun pengalaman sebagai perawat
- STR aktif wajib
- Mampu asuhan keperawatan lengkap dan dokumentasi
- Siap kerja shift"""

JD4B = """Data Analyst - PT Analitika Digital
Requirements:
- 2+ years experience in data analysis
- Strong SQL and Python skills
- Experience with Tableau or Power BI dashboards"""

CV5 = """ERWIN SAPUTRA
Store Operations Supervisor
erwin.saputra.id@yahoo.co.id | Depok | 0813-2222-3333

PROFIL
9 tahun di ritel modern dan UMKM. Pernah handle 3 cabang sekaligus
dengan total 25 karyawan. Praktis, suka angka, pengin pindah ke
operasional e-commerce atau fulfillment.

PENGALAMAN
Store Supervisor - Minimarket Sejahtera (2020 - Sekarang)
- Ngelola 2 cabang, omzet gabungan Rp 380 juta/bulan, 18 staf
- Stock opname akurat 99.2% (sebelumnya 94%) setelah bikin sistem
  audit harian pakai Google Sheets
- Training 12 staf baru; 3 sudah naik jadi shift leader

Assistant Store Manager - Swalayan Raya (2017 - 2020)
- Handle operasional harian: penerimaan barang, display, promo
  mingguan, jadwal shift 15 orang
- Turunkan barang expired 30% lewat sistem FEFO sederhana

Kasir & Staf Gudang - Toko Bangunan Jaya Abadi (2015 - 2017)

PENDIDIKAN
SMK Administrasi Perkantoran - SMKN 1 Depok (2012 - 2015)

KEAHLIAN
Operasional toko, stock opname, jadwal shift, training staf,
Google Sheets, Excel dasar, customer handling, FEFO"""

JD5A = """Area Retail Supervisor - Jaringan Minimart Sejahtera
Requirements:
- Minimal 5 tahun pengalaman operasional toko ritel
- Berpengalaman training dan memimpin tim toko
- Paham stock opname dan pengendalian barang expired
- Pendidikan SMK/D3/S1, pengalaman yang utama"""

JD5B = """Fulfillment Staff - PT Logistik Digital
Requirements:
- S1 semua jurusan, IPK minimal 3.00
- 1+ year experience in e-commerce fulfillment operations
- Familiar dengan WMS (warehouse management system)"""

CASES = [
    ("1A aligned", CV1, JD1A, "Embedded Firmware Engineer"),
    ("1B pivot", CV1, JD1B, "Senior Frontend Engineer"),
    ("2A aligned", CV2, JD2A, "Site Reliability Engineer"),
    ("2B pivot", CV2, JD2B, "Junior Graphic Designer"),
    ("3A aligned", CV3, JD3A, "Unity Game Developer"),
    ("3B pivot", CV3, JD3B, "Flutter Mobile App Developer"),
    ("4A aligned", CV4, JD4A, "Perawat Ruang Rawat Inap"),
    ("4B pivot", CV4, JD4B, "Data Analyst"),
    ("5A aligned", CV5, JD5A, "Area Retail Supervisor"),
    ("5B semi", CV5, JD5B, "Fulfillment Staff"),
]

out = []
for label, cv, jd, title in CASES:
    try:
        d = run(label, cv, jd, title)
        if d:
            out.append({"label": label, "score": d["readiness_score"], "seniority": d.get("seniority_level"),
                        "matched": d.get("matched_skills"), "missing": d.get("missing_skills"),
                        "synthesis": (d.get("synthesis") or "")[:200]})
    except Exception as e:
        print(f"[{label}] FAILED: {e}")
    time.sleep(2)

print()
print("=== REKAP ===")
for o in out:
    print(f"{o['label']:12} {o['score']:3} | {o['seniority']}")

json.dump(out, open("internal_testset_results.json", "w"), ensure_ascii=False, indent=1)
print("tersimpan: internal_testset_results.json")
