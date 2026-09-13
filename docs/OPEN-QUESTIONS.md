# Open Questions & ZCode's Thoughts

Log berjalan pertanyaan, pikiran, dan usulan dari ZCode yang belum diputuskan
atau sedang menunggu. Tiap entri diperbarui saat user menjawab/memutuskan.
Yang sudah diputuskan pindah ke bagian "Decided" di bawah (tetap disimpan
untuk konteks berpikir).

Format: [STATUS] pertanyaan/pikiran -> jawaban/keputusan (kalau ada)

STATUS: OPEN (menunggu) | DECIDED (sudah diputuskan) | ACTION-USER (menunggu aksi user)

---

## OPEN

### Q1 - Lantai faktor domain pengalaman: 0.0 atau 0.25? -> [DECIDED: 0.0]
[DECIDED oleh user setelah penjelasan ZCode, 13 Sep 2026]
Argumen yang diterima: 0.0 gampang dijelaskan ("pengalaman di bidang lain tidak
dihitung untuk lowongan ini") dan 30 vs 36 praktis tidak mengubah keputusan user
(dua-duanya bilang skip). Dampak nyata lantai 0.25 cuma +/-6 poin di kasus pivot.
Skor tetap terkirim ke Gemini untuk opini kedua, tapi keputusan tidak menunggu.

### Q2 - Apakah mekanisme perkalian (band x faktor) perlu diterapkan ke kategori lain? -> [DECIDED: tidak]
[DECIDED oleh user setelah penjelasan ZCode, 13 Sep 2026]
Faktor domain cukup di kategori Pengalaman saja. Alasan: skill wajib sudah
dinilai per-skill terhadap CV (yang tidak punya = 0), jadi mengalikan faktor
domain lagi = hukuman ganda untuk hal yang sama. Pengalaman spesial karena
satu-satunya kategori yang menghitung "tahun" secara buta domain.

### Q3 - Varian judgment LLM pada kasus borderline (2A: 92 -> 80) -> [RESOLVED]
[FIXED 13 Sep 2026 - lihat DEVLOG-003]
Solusi: seed deterministik per isi prompt (Groq mendukung seed) + aturan pita
kesesuaian domain eksplisit + gap tidak mengurangi tahun. Hasil: 3 run
beruntun identik 88/88/88, spread 12 -> 0 poin.

### Q4 - Skill dengan qualifier level: verifikasi e2e -> [RESOLVED]
[VERIFIED 13 Sep 2026 - lihat DEVLOG-003]
Stage B kini wajib menyalin qualifier verbatim ("Flutter (beginner)", "SQL
(dasar)"). Production 2 run beruntun: score 92/92, Flutter partial konsisten.

### Q5 - PDF 1 halaman: trade-off zoom ekstrem
[OPEN - keputusan desain nanti]
Auto-fit menjamin 1 halaman, tapi CV sangat panjang (3+ halaman konten) akan
di-zoom-down sampai font mengecil. Kandidat solusi: prompt tailor membatasi
max 4-5 bullet per pengalaman (mengurangi sumber panjang). ZCode menunggu
data: seberapa sering user mencapai zoom ekstrem.

---

## ACTION-USER

### E1 - Konvensi re-run eval setelah tiap perubahan engine (baru)
[OPEN - usulan ZCode, menunggu kesepakatan]
Seed Groq itu best-effort: kalau Groq mengubah infrastruktur inferensi,
varian bisa kembali tanpa kita sadari. Satu-satunya penangkal: jalankan ulang
internal_testset (10 kasus, ~3 menit) setiap kali prompt/formula diubah, dan
sekali sebulan sebagai deteksi dini. Belum dibakukan sebagai checklist.

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
