# DEVLOG 001 - Eval Baseline + 4 Engine Fixes

- **Tanggal:** 13 September 2026
- **Status:** SELESAI & LIVE di production
- **Dikerjakan oleh:** ZCode (Claude) — direview: pending, untuk Gemini advisor
- **Scope:** Membangun test set evaluasi pertama, menemukan 4 bug dari hasil pengukuran, memperbaiki, membuktikan dengan angka

---

## 1. Konteks (baca ini dulu)

Skillsy = Chrome extension yang menganalisis lowongan kerja (LinkedIn/JobStreet/dll) vs CV user, menghasilkan skor kecocokan. Mesinnya ("SIGAP Engine") adalah pipeline 4 stage:

1. **Stage A** (gpt-oss-20b): ekstraksi struktur lowongan (min tahun, skill wajib, edukasi, dll)
2. **Stage B** (gpt-oss-120b): baca CV (estimasi tahun, daftar skill, nilai requirement non-skill)
3. **Stage C** (kode murni, 0 LLM): hitung skor = 25% pengalaman + 45% skill wajib + 15% plus + 15% edukasi, dengan hard filter
4. **Stage D** (gpt-oss-20b): narasi bahasa Indonesia, verdict dikunci mesin

Prinsip desain: **mesin memutuskan, LLM menceritakan.** LLM tidak pernah menghasilkan angka verdict.

Infrastruktur: Vercel serverless (Python FastAPI), Groq inference (2 API key dengan rotasi otomatis, kuota 8k token/menit per key per model), Supabase (waitlist + log scan anonim).

---

## 2. Yang Dibangun: Test Set Evaluasi Pertama

File: `internal_testset_run1.py` (juga run2/run3 varian)

5 CV sintetis x 2 JD per CV (1 selaras + 1 melenceng) = **10 kasus uji**, tiap kasus menjalankan engine production asli. Tujuan: baseline terukur sebelum menambah fitur apa pun.

| CV | Hook pengujian |
|---|---|
| 1. Embedded Engineer (EN) | Jargon niche (RTOS, Modbus), token "C/C++" |
| 2. SRE dengan gap 1 tahun + sertifikasi | Gap karier, CKA |
| 3. Game Dev pivot ke mobile | Transferable credit, kualifikasi "beginner" |
| 4. Perawat dengan STR (ID penuh) | Kosakata non-IT, medis |
| 5. Retail Supervisor SMK (tanpa S1) | Education null, angka Rupiah, konsep abstrak |

---

## 3. Hasil Baseline (Run 1) - Masalah yang Ditemukan

| Kasus | Run-1 | Harusnya | Vonis |
|---|---|---|---|
| 1A Embedded vs Embedded | 60 | ~90 | SALAH: dihukum 2 bug |
| 1B Embedded vs Frontend | 51 | ~30-40 | Kebanyakan |
| 2A SRE vs SRE | 100 | 100 | Benar |
| 2B SRE vs Graphic Designer | 40 | ~25 | Kebanyakan |
| 3A GameDev vs Unity | 89 | 90-95 | Benar |
| 3B GameDev vs Flutter | 70 | ~45 | Kebanyakan |
| 4A Perawat vs Perawat | 89 | 95 | Benar |
| 4B Perawat vs Data Analyst | 55 | ~20 | KEBANYAKAN PARAH |
| 5A Retail vs Retail | 68 | ~95 | SALAH: 4 false negative |
| 5B Retail SMK vs Fulfillment (wajib S1) | 40 | 40 | Benar (hard filter) |

Ranking relasi selalu benar (selaras > melenceng), tapi skor absolut pivot terlalu murah hati.

### 4 Bug yang teridentifikasi:

1. **Pengalaman buta domain** — band pengalaman hanya menghitung tahun, tidak relevansi bidang. Perawat 3 tahun vs Data Analyst dapat 25 poin "gratis" dari pengalaman yang tidak relevan. (BELUM DIPERBAIKI - butuh keputusan desain)
2. **Pendidikan D4 dinilai salah** — D4 Teknik Elektro vs "Bachelor in Electrical Engineering or related" dinilai missing semua -> hard filter + edu 0 -> skor dipangkas ~30 poin. (FIXED)
3. **Kosakata retail/ops tidak terjembatani** — "stock opname" tidak dikenali sebagai "Stocktaking". (SEBAGIAN FIXED)
4. **Dua bug kecil** — "C/C++" gagal match ke "C, C++" (token slash pendek); "Flutter (beginner)" dihitung met penuh padahal qualifier level diabaikan. (FIXED)

---

## 4. Perbaikan yang Diterapkan (commits 53e75cc, dst)

### Fix A - Pendidikan (api/index.py, prompt Stage B)
Aturan baru di prompt penilaian: D4/Sarjana Terapan SETARA S1; "or related field"/"sederajat" dinilai longgar (bidang bersambungan = met, bersebelahan = partial); SMK hanya dihitung jika lowongan eksplisit membolehkan.

### Fix B - Sinonim retail/ops (api/knowledge_base.py)
4 grup sinonim baru: `retail operations` (operasional toko, store operations...), `stocktaking` (stock opname...), `team leadership` (memimpin tim...), `expired goods control` (fefo, barang expired...).

### Fix C - Split token slash (api/index.py, `_sanitize_skill_list`)
"C/C++" dipecah jadi "C" + "C++" saat ekstraksi (pemicu: ada bagian 1 huruf). "CI/CD" tetap utuh (semua bagian >=2 huruf).

### Fix D - Kualifikasi level (api/index.py, `_machine_skill_status`)
Skill CV yang ditulis dengan qualifier level (cth "Flutter (beginner)", "dasar", "pemula") dinilai PARTIAL, bukan MET.

---

## 5. Bukti Efek (Run 1 vs Run 3, engine yang sama)

**PENTING - metodologi:** Run 2 tidak valid karena perbaikan belum di-commit saat tes (kesalahan prosedur, diakui). Run 3 = satu-satunya perbandingan sah (perbaikan sudah ter-deploy).

| Kasus | Run-1 | Run-3 | Delta |
|---|---|---|---|
| 1A aligned | 60 | **92** | **+32** (C, C++ kena; edu 0->100; hard filter tidak nyala lagi) |
| 5A Retail aligned | 68 | **78** | +10 (Retail Operations + Stocktaking kena) |
| 1B pivot | 51 | 66 | +15 (dari fix edukasi, bukan issue #1) |
| 2A | 100 | 92 | -8 (varians ekstraksi) |
| 3A | 89 | 85 | -4 (varians) |
| 4A | 89 | 89 | 0 |
| Rata-rata SELARAS | 81.2 | **87.2** | +6 |
| Rata-rata PIVOT | 51.2 | 57.2 | +6 (dari fix edukasi) |

Unit test tambahan (semua lulus): stock opname <-> Stocktaking, FEFO <-> Expired Goods Control, C/C++ split dengan CI/CD tetap utuh, Flutter (beginner) = partial, Flutter = met.

---

## 6. Temuan Baru yang Belum Diperbaiki (untuk didiskusikan)

1. **Pengalaman buta domain (bug terbesar, sengaja ditunda)** - opsi desain: saat Stage B menilai item pengalaman "partial/missing karena domain beda", formula mengalikan band tahun dengan faktor relevansi itu. Risiko: mengubah skor semua user; perlu diskusi sebelum implement.
2. **Varians ekstraksi antar-run** - input identik, Stage A bisa mengeluarkan skill berbeda ("Expired Goods Control" vs "Expiration Control") -> skor geser +-5-10. Klaim determinisme kita presisinya: "skor stabil MENGIKUTI ekstraksi yang sama". Kandidat fix: parameter `seed` di Groq (belum dicek dukungannya) + prompt "pakai nama skill standar".
3. **Sinonim masih whack-a-mole jangka pendek** - solusi jangka panjang tetap: tumbuh dari data scan (Skillsy Index).
4. **Dua verifikasi pending** - "Flutter (beginner)" e2e belum terpicu; skill inline ("dokumentasi e-OMR") belum masuk daftar Stage B.

---

## 7. Keputusan yang Sudah Diambil (konteks untuk advisor)

- Multi-key Groq (2 akun) dipilih daripada multi-account melampaui kuota: ToS aman + redundansi key mati. Cerebras dievaluasi dan di-drop (free tier sekarang 402 berbayar semua).
- CV Tailor v2 keluarkan header lengkap + struktur per-perusahaan (feedback user: v1 lossy) + PDF via tab baru (window.print di side panel tidak andal).
- Guard anti-fabrikasi tailor ditagakkan di kode (angka/skill wajib terlacak ke CV), bukan cuma prompt.
- Badge partner Alibaba disembunyikan sementara (user masuk Google hackathon).

## 8. Roadmap Terbuka

Eval harness resmi (bakukan 10 kasus + skor target) -> fix varians ekstraksi -> diskusi faktor relevansi pengalaman -> persiapan Chrome Web Store -> PWA mobile.

---

*Cara pakai file ini: berikan ke AI advisor untuk cross-review keputusan teknis. Semua angka adalah hasil pengukuran nyata terhadap production engine (skillsy.my.id), bukan estimasi.*
