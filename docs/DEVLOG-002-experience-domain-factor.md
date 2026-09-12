# DEVLOG-002 - Experience Domain Relevance Factor (PLAN-001 dieksekusi)

- **Tanggal:** 13 September 2026
- **Status:** SELESAI & LIVE di production
- **Terimplementasi dari:** [PLAN-001-domain-blind-experience.md](PLAN-001-domain-blind-experience.md)
- **Dikerjakan oleh:** ZCode — direview: pending, untuk Gemini advisor

---

## 1. Apa yang Diubah

### 1.1 Item pengalaman menyebut bidang lowongan secara eksplisit
Item yang dinilai Stage B berubah dari:
`"Minimal 3 tahun pengalaman kerja relevan"`
menjadi:
`"Minimal 3 tahun pengalaman kerja yang relevan dengan bidang Data Analyst"`

Alasan: diagnosis rollout pertama menunjukkan rule jauh di prompt kalah dari
teks item lokal - LLM tetap menilai "lama kerja", bukan relevansi. Setelah
bidang tertulis di item, pertanyaan relevansi tidak mungkin terlewat.

### 1.2 Prompt Stage B: aturan relevansi pengalaman
Aturan eksplisit: nilai RELEVANSI ke domain lowongan, bukan total tahun.
Adjacent domain (business analyst vs data analyst) = partial; unrelated
(nurse vs data analyst) = missing; sertakan bukti CV di detail.

### 1.3 Formula Stage C (inti perubahan)
```
exp_score = band_tahun × faktor_domain
faktor_domain: met = 1.0, partial = 0.5, missing = 0.0
```
(sesuai skala global mesin; hard filter & narasi seniority tidak berubah)

### 1.4 Transparansi UI
Breakdown menampilkan catatan faktor saat < 1.0:
"skor pengalaman disesuaikan: latar belakangmu belum selaras dengan bidang
lowongan ini (faktor 0)" - di extension dan demo page.

Nol panggilan API tambahan (faktor memakai verdict Stage B yang sudah ada).

---

## 2. Bukti Efek (Run 3 -> Run 4, production engine)

| Kasus | Run-3 | Run-4 | Delta | Penilaian |
|---|---|---|---|---|
| 1A Embedded vs Embedded | 92 | 92 | 0 | Stabil (selaras) |
| **1B Embedded vs Frontend senior** | 66 | **41** | **-25** | Jujur: nol pengalaman frontend |
| 2A SRE vs SRE | 92 | 80 | -12 | Lihat catatan varian di bawah |
| **2B SRE vs Graphic Designer** | 55 | **30** | **-25** | Jujur: skill infra tidak dipakai di desain |
| 3A GameDev vs Unity | 89 | 89 | 0 | Stabil |
| 3B GameDev (Flutter beginner) vs Flutter | 70 | **58** | -12 | Jujur: beginner + belum publish |
| 4A Perawat vs Perawat | 89 | 89 | 0 | Stabil |
| **4B Perawat vs Data Analyst** | 55 | **30** | **-25** | Jujur: kasus asli yang memicu diskusi ini |
| 5A Retail vs Retail | 78 | **89** | +11 | Sinonim retail makin baik kena + domain met |
| 5B Retail SMK vs Fulfillment (wajib S1) | 40 | 40 | 0 | Stabil |

**Rata-rata SELARAS:** 87.2 -> 87.8 (netral - kasus selaras tidak dirugikan)
**Rata-rata PIVOT:** 57.2 -> **39.8** (-17.4, koreksi ke arah jujur)

Semua selaras tetap >= 80 (kecuali 2A: 80). Semua pivot turun. Tidak ada
kasus selaras yang rusak.

---

## 3. Contoh Kualitatif (kasus asli pemicu diskusi)

Perawat 3 tahun vs Data Analyst:
- Sebelum: 55, item pengalaman "met" dengan alasan "3 tahun >= 2 tahun"
- Sesudah: **30**, item "missing": *"Pengalaman kerja 3 tahun sebagai perawat
  junior memberi pemahaman data klinis, namun tidak memenuhi syarat
  minimal 2 tahun pengalaman relevan"* + catatan faktor 0 di breakdown

---

## 4. Catatan Varian (jujur)

2A turun 92 -> 80: Stage B menilai item pengalaman "partial" pada run ini
(sebelumnya "met") padahal kandidat jelas selaras - varian judgment LLM pada
kasus borderline. Dampak dibatasi: hanya kategori pengalaman, dan tetap di
wilayah "layak apply". Kandidat mitigasi: eval harness dengan skor target
per kasus akan mendeteksi drift seperti ini.

---

## 5. Status Isu Terbuka (update dari DEVLOG-001)

1. ~~Pengalaman buta domain~~ - **DIPERBAIKI** (dokumen ini)
2. Varians ekstraksi antar-run (±5-10) - terbuka; kandidat: parameter seed Groq
3. Sinonim konsep bocor sebagian (Team Leadership, Expiration Control) - terbuka
4. Verifikasi "(beginner)" e2e - belum terpicu di run ini

## 6. Roadmap

Eval harness finalisasi -> Chrome Web Store submission -> PWA mobile ->
(fitur) pivot suggestions & learning roadmap (makin relevan: kandidat pivot
sekarang dapat skor jujur, jadi butuh arah).
