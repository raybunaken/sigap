# Open Questions & ZCode's Thoughts

Log berjalan pertanyaan, pikiran, dan usulan dari ZCode yang belum diputuskan
atau sedang menunggu. Tiap entri diperbarui saat user menjawab/memutuskan.
Yang sudah diputuskan pindah ke bagian "Decided" di bawah (tetap disimpan
untuk konteks berpikir).

Format: [STATUS] pertanyaan/pikiran -> jawaban/keputusan (kalau ada)

STATUS: OPEN (menunggu) | DECIDED (sudah diputuskan) | ACTION-USER (menunggu aksi user)

---

## OPEN

### Q1 - Lantai faktor domain pengalaman: 0.0 atau 0.25?
[OPEN - dibawa ke Gemini via PLAN-001 bagian 5]
Kandidat pivot lintas-domain: faktor pengalaman missing = 0.0 (kejujuran total,
pilihan ZCode) atau lantai 0.25 (pengalaman umum tetap dihargai sedikit)?
Terlihat di run-4: perawat vs data analyst = 30 (dengan 0.0). Gemini diminta
beri opini berbasis data 10 kasus.

### Q2 - Apakah mekanisme perkalian (band x faktor) perlu diterapkan ke kategori lain?
[OPEN - untuk diskusi berikutnya]
Saat ini faktor domain hanya mengalikan kategori Pengalaman. Pertanyaan jangka
panjang: apakah plus_skills atau edukasi juga perlu faktor relevansi, atau
cukup pengalaman saja? Pendapat ZCode: cukup pengalaman + skill wajib (yang
sudah dinilai mesin per-skill); menambah faktor ke semua kategori = kompleksitas
tanpa bukti masalah.

### Q3 - Varian judgment LLM pada kasus borderline (2A: 92 -> 80)
[OPEN - dicatat di DEVLOG-002 bagian 4]
Kasus jelas selaras (SRE vs SRE, 9 tahun) dinilai pengalaman "partial" pada
satu run dan "met" pada run lain -> skor bergeser 12 poin. Kandidat mitigasi:
parameter seed Groq untuk reproducibility, atau prompt dengan contoh borderline.
ZCode's thought: prioritas sedang — hanya kena kasus borderline, tapi kelihatan
oleh user yang teliti.

### Q4 - Skill dengan qualifier level: verifikasi e2e belum terpicu
[OPEN - dari eval run-3]
Fix "Flutter (beginner)" -> partial lulus unit test, tapi pada run-4 Stage B
kebetulan tidak menulis qualifier di daftar skill, jadi jalur e2e-nya tidak
teruji. Perlu CV uji yang eksplisit menulis qualifier.

### Q5 - PDF 1 halaman: trade-off zoom ekstrem
[OPEN - keputusan desain nanti]
Auto-fit menjamin 1 halaman, tapi CV sangat panjang (3+ halaman konten) akan
di-zoom-down sampai font mengecil. Kandidat solusi: prompt tailor membatasi
max 4-5 bullet per pengalaman (mengurangi sumber panjang). ZCode menunggu
data: seberapa sering user mencapai zoom ekstrem.

---

## ACTION-USER

### A1 - Vercel Analytics belum di-enable
[OPEN] Tinggal klik dashboard Vercel -> Analytics -> Enable (gratis). Tanpa ini
kita buta soal traffic homepage baru.

### A2 - Rotasi service key Supabase
[OPEN - saran keamanan] service key sempat lewat chat. Setelah stabil, rotate
dari Supabase dashboard lalu serahkan key baru untuk dipasang.

### A3 - Jalankan SQL tailor_log di Supabase
[OPEN - menunggu konfirmasi] Kuota 10 tailor/hari baru aktif setelah tabelnya
dibuat. SQL ada di supabase_schema.sql (blok tailor_log).

---

## DECIDED (arsip keputusan - konteks berpikir)

### D1 - Multi-key Groq dipilih, Cerebras di-drop [DECIDED]
ZCode awalnya mengusulkan provider kedua (Cerebras) sebagai failover.
Setelah dites: free tier Cerebras kini 402 (berbayar) untuk semua model
berguna. Multi-key Groq (2 akun) dipakai dengan rotasi otomatis; risiko ToS
multi-account disampaikan jujur ke user dan diterima sebagai risiko terukur.

### D2 - CV Tailor v2 keluarkan struktur lengkap [DECIDED]
User komplain v1 lossy (nama/kontak hilang, job digabung). Riset pembanding:
hasil Gemini dirasa lebih rapi. Solusi: schema blocks (header verbatim +
entry per perusahaan), PDF via tab baru, guard verbatim entry.

### D3 - Badge Alibaba Cloud disembunyikan [DECIDED]
User masuk Google hackathon. Badge di-comment (bukan dihapus), SVG utuh,
tinggal buka komentar untuk restore.

### D4 - Kerangka skor pengalaman: band x faktor [DECIDED -> dieksekusi]
Lihat PLAN-001 + DEVLOG-002. Lantai 0.0 dipilih.

### D5 - Posisi demo di homepage [DECIDED]
User menolak 3 tombol hero + demo "nyempil". Solusi: section khusus "Live
Demo" dengan narasi menjawab "kenapa demonya di web padahal extension".
