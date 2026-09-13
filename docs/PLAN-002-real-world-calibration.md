# PLAN-002 - Real-World Calibration: 4 Fixes dari Tes CV Nyata Pertama

- **Status:** DIIMPLEMENTASI SEBAGIAN - 16 -> 32 (di bawah proyeksi 40-55); isu tersisa di [DEVLOG-004](DEVLOG-004-real-world-calibration.md)
- **Penulis:** ZCode — untuk cross-review oleh Gemini advisor
- **Pemicu:** Tes nyata pertama lewat demo page (CV Data Strategy vs lowongan "Sales Operations Specialist" B2B) -> skor 16%, padahal penilaian manusia jujur menempatkan kandidat ini 60-70 (dia literalnya Sales Operations Analyst yang melamar Sales Operations Specialist, hanya kurang tool spesifik)

---

## 1. Bukti Masalah (tes nyata, bukan sintetis)

Breakdown hasil: exp=0, must=20, plus=0, edu=50 -> 16%.

Yang dinilai BENAR oleh engine: Salesforce missing, SAP missing, Excel met, sintesis adil nadanya, sanitasi jalan.

Yang SALAH (4 akar masalah):

### Masalah A - Bug placeholder domain
Judul lowongan dibiarkan kosong di demo -> item pengalaman menjadi
"pengalaman kerja yang relevan dengan bidang **Lowongan**" (teks rusak).
Stage B pun bingung menilai relevansi terhadap "bidang" yang tidak jelas.

### Masalah B - Tool induk + fitur turunan dipecah jadi syarat terpisah
JD: "Proficiency in Microsoft Excel, **including** Pivot Tables, XLOOKUP,
Power Query" -> Stage A mengekstrak Excel, Power Query, XLOOKUP sebagai
TIGA skill wajib terpisah. Kandidat kuat di Excel kena tiga hitungan gagal,
padahal rekuter membacanya sebagai satu kompetensi dengan bukti kedalaman.

Pola yang sama terjadi di "CRM platforms (Salesforce preferred) and ERP
systems": kandidat punya pengalaman CRM Architecture, tapi yang diekstrak
"Salesforce" (missing) - padahal syarat induknya "CRM platforms" terpenuhi.

### Masalah C - Konsep vs label pada plus-item
Plus-item "root-cause analysis" dinilai missing, padahal CV menunjukkan
perilakunya ("menganalisis 8.000+ data lead... mengidentifikasi pola
konversi"). Mesin buta terhadap parafrasa konsep.

### Masalah D - Pengalaman pendek tapi relevan = 0 total
~6 bulan di peran Sales Operations (domain TEPAT) + syarat 2 tahun ->
band 0 -> dikali faktor apapun tetap 0. Rekuter manusia memberi kredit
parsial untuk pengalaman yang relevan meski pendek.

---

## 2. Perbaikan yang Diusulkan (4 mekanisme)

### Fix A - Domain dari isi JD saat judul kosong (bug fix)
Jika job_title kosong/placeholder, item pengalaman memakai frasa
"bidang lowongan ini" DAN prompt Stage B diperintah menyimpulkan bidang
dari isi job description. Jika judul ada, tetap seperti sekarang.

### Fix B - Aturan "tool induk + fitur turunan" di Stage A
Aturan ekstraksi baru: jika requirement menyebut tool induk beserta
fiturnya ("X, including A, B"), ekstrak TOOL INDUK sebagai must_skill,
dan fitur turunan masuk plus_skills (bukti kedalaman, bukan syarat
terpisah). Efek kasus ini: Excel tetap wajib (met), Power Query &
XLOOKUP turun kelas jadi plus. Untuk CRM: tambah grup sinonim
"crm platforms" (crm systems, crm architecture, crm software) supaya
pengalaman CRM Architecture kandidat terbaca memenuhi syarat induk.

### Fix C - Plus-item dapat kredit parsial berbasis bukti LLM
Stage B mendapat tugas tambahan: untuk setiap plus_skill, nilai apakah CV
menunjukkan bukti TERKAIT (meski dengan nama berbeda) -> output
evidence: met / partial / missing dengan kutipan. Stage C: status plus =
MAKSIMUM(status mesin, status LLM tapi dibatasi partial). Artinya:
- mesin bilang met -> tetap met
- mesin bilang missing tapi LLM menunjuk bukti terkait -> partial (0.5)
- tidak ada bukti sama sekali -> missing
Anti-fabrikasi terjaga: LLM tidak pernah bisa mengangkat missing ke met,
hanya ke partial, dan wajib mengutip bukti.

### Fix D - Lantai band untuk domain yang cocok
Jika faktor domain > 0 (domain met/partial) dan band = 0 (tahun di bawah
40% syarat), band dinaikkan ke 0.25. Hanya berlaku saat bidang cocok.
Kasus ini: exp = 0.25 x 0.5 (partial) = 0.125 -> +3 poin, dan pesan ke
user menjadi "pengalaman relevanmu dihitung, walau belum 2 tahun".

---

## 3. Proyeksi (jujur, bukan janji)

Dengan 4 fix, kasus ini diproyeksikan naik dari 16 ke kisaran **40-55**:
- must: 20 -> ~33 (Excel tetap met; Power Query/XLOOKUP turun ke plus)
- plus: 0 -> ~20 (root-cause & problem-id dapat partial via bukti)
- exp: 0 -> ~12 (lantai 0.25 x faktor partial 0.5)
- edu: 50 (tetap)

Yang TETAP missing oleh desain: Salesforce, SAP, WMS-style tools yang
memang tidak ada di CV. Skor akhir tetap di bawah 60 - jujur bahwa
kandidat junior dengan tool-gap masih bukan kandidat kuat, tapi bukan
lagi 16% yang terasa menghakimi.

Risiko: proyeksi bisa meleset karena setiap fix mengubah perilaku LLM.
Verifikasi wajib: rerun kasus nyata ini + 10 kasus test set (regresi).

---

## 4. Pertanyaan Terbuka untuk Gemini Advisor

1. **Fix B:** apakah aturan "tool induk = wajib, fitur turunan = plus" benar,
   atau rekuter justru menganggap XLOOKUP/Power Query sebagai syarat hard
   tersendiri di pasar B2B?
2. **Fix C:** apakah kredit partial dari LLM untuk plus-item berisiko
   digaming (user menulis CV yang "menyiratkan" banyak hal)? Pembatas
   saat ini: maksimal 0.5 + wajib kutipan bukti.
3. **Fix D:** apakah lantai 0.25 untuk domain yang cocok konsisten dengan
   keputusan lantai 0.0 untuk domain yang tidak cocok (PLAN-001)?

## 5. Rencana Implementasi

1. Stage A prompt: aturan tool induk + fitur turunan (Fix B)
2. knowledge_base.py: grup sinonim CRM (Fix B lanjutan)
3. Stage B prompt: tugas evidence_map untuk plus_skill + aturan domain
   dari JD saat judul kosong (Fix A + C)
4. Stage C: gabungkan status plus (maks mesin/LLM-partial) + lantai band
   (Fix C + D)
5. Verifikasi: rerun kasus nyata ini (target 40-55) + 10 kasus test set
   (regresi: selaras tetap 80-92, pivot tetap 30-58)
6. DEVLOG-004 + update PLAN-002 status

Estimasi: setengah hari.
