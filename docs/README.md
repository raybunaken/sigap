# Docs Index - Skillsy Decision Log

Dua seri dokumen untuk jejak keputusan teknis Skillsy:

- **`PLAN-00X-*.md`** — proposal & desain SEBELUM dieksekusi (status: proposed/decided)
- **`DEVLOG-00X-*.md`** — perubahan yang SUDAH diterapkan + efek + bukti pengukuran

## Daftar

| File | Status | Ringkas |
|---|---|---|
| [DEVLOG-001-eval-baseline-and-4-fixes.md](DEVLOG-001-eval-baseline-and-4-fixes.md) | Selesai | Test set 10 kasus pertama; 4 bug ditemukan & diperbaiki; selaras 81.2 -> 87.2 |
| [PLAN-001-domain-blind-experience.md](PLAN-001-domain-blind-experience.md) | Diimplementasi | Pengalaman buta domain: band tahun x faktor relevansi |
| [DEVLOG-002-experience-domain-factor.md](DEVLOG-002-experience-domain-factor.md) | Selesai | Bukti eksekusi PLAN-001: selaras netral, pivot -17 rata-rata ke arah jujur |
| [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) | Berjalan | Log pertanyaan, pikiran, dan keputusan ZCode + status aksi user |

## Konvensi

- Semua angka di dokumen ini adalah hasil pengukuran nyata terhadap production engine, bukan estimasi.
- Test set ada di root: `internal_testset_run*.py` (5 CV x 2 JD per CV).
- Dokumen ditulis agar bisa dibaca AI advisor tanpa konteks percakapan.
- Setiap kali ZCode menyelesaikan sesuatu -> buat DEVLOG baru. Setiap ada proposal/diskusi desain -> buat PLAN baru. Setiap pertanyaan/pikiran terbuka -> catat di OPEN-QUESTIONS.md dan update statusnya saat terjawab.
