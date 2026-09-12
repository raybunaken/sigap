# DEVLOG-003 - Deterministic Seed + Judgment Rules (Q3 & Q4 dituntaskan)

- **Tanggal:** 13 September 2026
- **Status:** SELESAI & LIVE di production
- **Menutup:** OPEN-QUESTIONS.md Q3 dan Q4
- **Dikerjakan oleh:** ZCode — direview: pending, untuk Gemini advisor

---

## 1. Apa yang Diubah

### 1.1 Seed deterministik per isi prompt (fix Q3 - varian antar-run)
`groq_request` kini mengirim parameter `seed` ke Groq, diturunkan dari hash
CRC32 isi messages:

```
seed = zlib.crc32(json.dumps(messages)) & 0x7FFFFFFF
```

Input sama -> seed sama -> sampling sama. Seed diterima Groq (bukan 400) dan
teruji: 3x panggilan seed sama = output identik.

### 1.2 Aturan judgment Stage B (perkuat kasus borderline)
- Hitung SEMUA tahun profesional untuk `cv_years_estimate` - gap kerja tidak
  mengurangi (gap adalah peristiwa hidup, bukan pengalaman hilang).
- Pita kesesuaian domain didefinisikan eksplisit: domain SAMA + tahun cukup
  = MET; domain BERDEKATAN = PARTIAL; domain TIDAK BERKAITAN = MISSING.

### 1.3 Qualifier skill dipertahankan (fix Q4)
Stage B diperintahkan menyalin nama skill PERSIS termasuk qualifier level:
"Flutter (beginner)" tetap tertulis begitu, tidak dipangkas jadi "Flutter".
Guard mesin kemudian menurunkannya jadi partial.

---

## 2. Bukti Efek

### Q3 - Varian skor kasus borderline (SRE 9 tahun vs syarat 5 tahun)
| | Sebelum (run-3 vs run-4) | Sesudah (3 run beruntun) |
|---|---|---|
| Skor | 92 lalu 80 (spread 12) | 88 / 88 / 88 (spread 0) |
| Item pengalaman | met <-> partial (goyah) | partial stabil |

### Q4 - Qualifier skill
Production, 2 run beruntun: score 92/92, Flutter = partial (konsisten).
D3 diterima untuk syarat informatika, unit test lulus semua.

---

## 3. Catatan Jujur

- Seed Groq itu best-effort (bukan jaminan keras seperti klaim OpenAI), tapi
  empirisnya menghapus varian pada kasus-kasus yang kami uji.
- Cross-seed (42 vs 777) pada prompt trivia menghasilkan output sama - tidak
  bisa dipakai membuktikan apakah seed berbeda menghasilkan beda; yang penting
  bagi kami adalah same-input stabil, dan itu tercapai.
- Angka skor bisa berubah di masa depan jika prompt dievolusi - itulah fungsi
  eval harness: setiap perubahan diukur ulang terhadap 10 kasus.

## 4. Status Isu Terbuka (update)

1. Pengalaman buta domain - FIXED (DEVLOG-002)
2. Varians ekstraksi antar-run - **FIXED** (dokumen ini; spread 12 -> 0)
3. Sinonim konsep bocor sebagian - TERBUKA (retail tercakup; Team Leadership
   & Expiration Control masih perlu dipetakan)
4. Verifikasi qualifier e2e - **SELESAI** (dokumen ini)
