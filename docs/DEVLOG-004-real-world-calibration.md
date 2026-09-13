# DEVLOG-004 - Real-World Calibration (PLAN-002 dieksekusi)

- **Tanggal:** 13 September 2026
- **Status:** SELESAI (sebagian) & LIVE - hasil 16 -> 32, di bawah proyeksi 40-55
- **Mengeksekusi:** [PLAN-002-real-world-calibration.md](PLAN-002-real-world-calibration.md)
- **Dikerjakan oleh:** ZCode — direview: pending, untuk Gemini advisor

---

## 1. Pemicu

Tes nyata pertama lewat demo page: CV Data Strategy (pendiri Skillsy sendiri)
vs lowongan "Sales Operations Specialist" B2B -> skor 16%, padahal kandidat
adalah Sales Operations Analyst yang melamar peran Sales Operations.
Penilaian manusia jujur: 60-70. Empat akar masalah ditemukan (lihat PLAN-002).

---

## 2. Perubahan yang Diterapkan

### Fix A - Domain dari JD saat judul kosong [JALAN]
Judul kosong/placeholder ("Lowongan") -> item pengalaman memakai frasa
"bidang lowongan ini" dan Stage B disuruh menyimpulkan bidang dari isi JD.
Teks rusak "bidang Lowongan" tidak ada lagi.

### Fix B - Aturan tool family + sinonim CRM [SEBAGIAN - lihat catatan]
Stage A diberi aturan: tool induk = must_skill, fitur turunan = plus.
Sinonim grup CRM baru (crm platforms/systems/architecture).
Terverifikasi run ini: "Microsoft Excel" met.
TIDAK konsisten: pada run yang sama Stage A tetap mengekstrak
"Pivot Tables" dan "Power Query" sebagai must terpisah (varian LLM).

### Fix C - Plus-item lift berbasis bukti [JALAN]
Stage B menghasilkan plus_evidence (status max partial + kutipan bukti).
Mesin-missing naik ke partial jika LLM menunjuk bukti terkait di CV.
Terverifikasi: plus 0 -> 100 pada kasus nyata (B2B/root-cause/problem-id
dipromosikan ke partial dengan kutipan).
Anti-fabrikasi terjaga: LLM tidak bisa mengangkat ke met.

### Fix D - Lantai band domain cocok [JALAN]
Band 0 + domain met/partial -> band 0.25.

---

## 3. Bukti Efek

Kasus pemicu (CV Data Strategy vs Sales Ops B2B):
- Run sebelum: **16%** (exp=0, must=20, plus=0, edu=50)
- Run sesudah: **32%** (exp=0, must=20, plus=100, edu=50)
- Plus-item: root-cause analysis & problem identification terangkat partial
  dengan bukti; Excel tetap met; Salesforce/SAP tetap missing (jujur)

---

## 4. Jujur: Di Bawah Proyeksi (40-55) dan Kenapa

1. **Aturan tool family tidak konsisten antar-run.** Seed menstabilkan
   output untuk input identik, tapi CV/JD nyata berbeda per user - variasi
   phrasing membuat Stage A kadang mengikuti aturan tool family, kadang
   mengekstrak fitur turunan sebagai must terpisah.
2. **Judgment domain untuk tahun-pendek-domain-sama masih harsh.** Sales Ops
   Analyst vs Sales Ops Specialist dinilai missing (karena tahun 0.5 < 2)
   -> faktor 0, padahal domain sama persis. PLAN-001 faktor hanya
   membedakan cross-domain; kasus same-domain-short-years butuh perlakuan
   tersendiri (band parsial, bukan nol).

## 5. Status Isu (update dari DEVLOG-002/003)

1. Pengalaman buta domain (cross-domain) - FIXED (DEVLOG-002)
2. Varian antar-run pada input identik - FIXED (DEVLOG-003, seed)
3. Varian ekstraksi pada INPUT BERBEDA (phrasing LLM) - **TERBUKA, isu
   aktif utama** - kandidat fix: validasi output Stage A terhadap schema
   lebih ketat, atau 2-pass extraction (extract lalu normalisasi)
4. Same-domain-short-years dinilai missing - **TERBUKA** - kandidat: band
   parsial untuk domain cocok (0.25-0.4) alih-alih 0, atau Stage B instruksinya
   dipisah antara "tahun" dan "relevansi"
5. Sinonim retail/konsep - TERBUKA (sebagian tercakup)

## 6. Rencana Verifikasi Berikutnya

Rerun kasus nyata ini + test set 10 kasus setelah isu 3 & 4 ditangani.
Target: kasus ini 45-55 tanpa menggeser kasus selaras dari 80-92.
