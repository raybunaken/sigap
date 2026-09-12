# PLAN-001 - Memperbaiki "Pengalaman Buta Domain"

- **Status:** DISETUJUI & DIIMPLEMENTASI - lihat [DEVLOG-002](DEVLOG-002-experience-domain-factor.md) untuk bukti. Keputusan lantai: memakai skala global 0.0/0.5/1.0 (tanpa lantai 0.25).
- **Penulis:** ZCode — untuk cross-review oleh Gemini advisor
- **Terkait:** DEVLOG-001 (temuan dari eval baseline 10 kasus)

---

## 1. Masalah

Formula pengalaman saat ini hanya menghitung rasio tahun (`tahun CV ÷ syarat tahun`), tanpa mempertimbangkan **relevansi bidang**. Akibat terukur dari eval baseline:

- Perawat 3 tahun (skill relevan dengan data analyst: NOL) vs lowongan Data Analyst -> skor 55
- SRE 8 tahun vs Junior Graphic Designer -> skor 40
- Game Dev (Flutter level beginner) vs Flutter Developer -> skor 70

Penyebab teknis: Stage B (LLM) sebenarnya SUDAH menilai relevansi item pengalaman (met/partial/missing dengan bukti CV), tetapi formula mengabaikan verdict itu - angka numeric selalu menang.

## 2. Mekanisme yang Diusulkan

```
exp_score = band_tahun × faktor_domain
```

- `band_tahun` = angka numeric eksisting (rasio tahun: >=1.0 -> 1.0, >=0.7 -> 0.6, >=0.4 -> 0.3, sisanya 0)
- `faktor_domain` = verdict Stage B atas item pengalaman: met -> 1.0, partial -> 0.5, missing -> 0.0

**Nol panggilan API tambahan** (data sudah dihasilkan Stage B setiap scan, selama ini dibuang). Perubahan kode ~10 baris + penajaman prompt.

## 3. Proyeksi Dampak ke 10 Kasus Eval

| Kasus | Skor saat ini | Proyeksi | Alasan |
|---|---|---|---|
| 1A Embedded vs Embedded | 92 | 92 (tetap) | Domain selaras |
| 2A SRE vs SRE | 92 | 92 (tetap) | Selaras |
| 3A GameDev vs Unity | 85 | 85 (tetap) | Selaras |
| 4A Perawat vs Perawat | 89 | 89 (tetap) | Selaras |
| 5A Retail vs Retail | 78 | ~78 (tetap) | Selaras |
| 1B Embedded vs Frontend senior | 66 | ~47 | Pengalaman embedded tidak dipakai di frontend |
| 2B SRE vs Graphic Designer | 55 | ~27 | Faktor 0 - infra skill tidak relevan di desain |
| 3B GameDev vs Flutter | 70 | ~51 | 6 tahun game dev bukan 2 tahun Flutter profesional |
| 4B Perawat vs Data Analyst | 55 | ~30 | Faktor 0 - verdict jujur: skip |
| 5B Retail vs Fulfillment (wajib S1) | 40 | ~28 | Adjacent (parsial) + cap S1 |

Pola: **kasus selaras tidak bergerak; semua pivot turun ke wilayah jujur.**

## 4. Trade-off yang Disadari

1. Kasus pivot terlihat "kejam" (30-50). Pesan ke user bukan larangan, tapi diarahkan lewat advice: "energimu lebih efektif di lowongan X/Y".
2. Item pengalaman jadi penentu besar di kasus pivot (bobot 25% x faktor). Varian antar-run LLM bisa menggeser ~12 poin. Mitigasi: prompt Stage B diperjelas (nilai RELEVANSI bidang + kutip bukti) dan verbatim evidence wajib.
3. Skala faktor konsisten dengan skala global mesin (met 1.0 / partial 0.5 / missing 0.0) supaya tidak ada dua bahasa.

## 5. Pertanyaan Terbuka untuk Gemini Advisor

*UPDATE 13 Sep 2026: Q1 dan Q2 di bawah sudah DIPUTUSKAN oleh user tanpa
menunggu - lantai 0.0 dipilih (argumen: mudah dijelaskan, dampak praktis
kecil), dan faktor domain cukup di kategori Pengalaman saja (skill wajib
sudah dihukum per-skill; faktor ulang = hukuman ganda). Pendapat Gemini
tetap dipersilakan sebagai review setelah keputusan.*

1. **Lantai faktor:** missing domain = 0.0 (kejujuran total, pilihan penulis) atau diberi lantai 0.25 (pengalaman umum tetap dihargai sedikit)? Trade-off: 0.0 lebih tegas tapi kasus pivot jadi terlihat "hampir tidak punya peluang".
2. **Apakah perkalian ini berisiko "double punishment"?** Kandidat pivot sudah kena skill wajib 0 - apakah pengalaman 0 membuat mereka patah semangat? (Catatan penulis: pivot suggestions + learning roadmap adalah jalur bantuan mereka.)
3. **Perlu tidaknya ditampilkan ke user** angka faktor domain secara eksplisit di breakdown (transparansi vs kompleksitas UI).
4. **Alternatif yang ditolak penulis:** minta LLM mengestimasi "tahun pengalaman RELEVAN" (bukan total). Ditolak karena estimasi angka oleh LLM lebih halusinasi-prone daripada verdict kategori dengan bukti.

## 6. Rencana Implementasi (setelah disetujui)

1. Prompt Stage B: perjelas "item pengalaman dinilai RELEVANSI bidang lowongan, kutip bukti dari CV"
2. Formula Stage C: ambil status item experience -> faktor -> kalikan band
3. Breakdown UI: catatan faktor saat < 1.0 (transparan)
4. Rerun 10 test set -> bukti before/after -> buat DEVLOG-002

Estimasi: setengah hari.
