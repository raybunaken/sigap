# PLAN-003 - Global Taxonomy Layer (ESCO/Lightcast) + Semantic Tier

- **Status:** PROPOSED - MENUNGGU KEPUTUSAN (User menyetujui arah, menunggu eksekusi)
- **Penulis:** ZCode — untuk cross-review oleh Gemini advisor
- **Latar:** Diskusi arah matching setelah user menyatakan ketakutan "endless fix per pekerjaan", diperkuat pandangan Gemini bahwa kamus sinonim manual adalah "warisan Generasi 1"

---

## 1. Latar: Dua Identifikasi Masalah yang Saling Melengkapi

**Gemini advisor:** kamus sinonim manual di `knowledge_base.py` adalah warisan
Generasi 1 - tidak scalable, memicu reflex "ketik sinonim baru" tiap ketemu
domain baru (retail, CRM, kesehatan...), dan akan tidak pernah selesai.

**ZCode (eval run-1 s/d run-4):** dua isu konkret terukur -
(a) konsep abstrak JD tidak terjembatani ke istilah CV ("Team Leadership" vs
"training staf"), (b) istilah non-IT Indonesia tidak ada di kamus ("stock
opname", "askep", "STR").

Kesimpulan bersama: **hentikan penambahan kamus manual; naikkan matching ke
arsitektur standar industri** (pola LinkedIn/Lightcast/Textkernel):
standardisasi + semantic matching + evidence, dua tingkat.

## 2. Framing Industri (kenapa ini bukan jalan aneh sendiri)

Semua pemain serius memakai pola sama: **lapis cepat literal/normalisasi +
lapis semantik di atasnya**, di atas taksonomi skill yang dirawat.

- LinkedIn: Skills Graph ~40rb node, semua penyebutan skill di-standardize
- Lightcast: Open Skills Taxonomy ~32rb skill (open data)
- Textkernel/RChilli (parser API): fast-path rules + semantic slow-path
- Eightfold: sama, tapi moat-nya data volume (ratusan juta profil) - tidak
  bisa kita salin; kita bangun data sendiri via Skillsy Index

Perbedaan kita: verbatim evidence guard (LLM mengutip bukti, mesin verifikasi)
- lebih ketat dari embeddings standar yang tidak bisa menjawab "kenapa match".

## 3. Arsitektur yang Diusulkan: 4 Lapis Matching

```
Lapis 0: exact + normalisasi                     (sudah ada)
Lapis 1: kamus lokal Indonesia                   (sudah ada, DIPANGKAS:
                                                  hanya istilah lokal: stock
                                                  opname, BPJS, askep, STR...)
Lapis 2: BARU - ESCO/Lightcast lookup            (label + alt-labels persis
                                                  -> met; relasi related ->
                                                  maksimal partial)
Lapis 3: BARU - LLM semantic tier (PLAN-003)     (LLM mengusulkan padanan
                                                  semantik + kutip bukti
                                                  verbatim dari CV; mesin
                                                  verifikasi; maksimal partial)
```

Aturan prioritas: met hanya dari Lapis 0-2. Lapis 3 maksimal partial.
Fallback chain: Lapis 1 -> 2 -> 3, berhenti di yang pertama match.

## 4. Sumber Taksonomi

| | ESCO | Lightcast Open Skills |
|---|---|---|
| Pemilik | Uni Eropa (resmi, terbuka) | Lightcast (open data) |
| Cakupan | ~14rb skill + ~3rb knowledge + relasi hierarki + related-skill + pemetaan okupasi | ~32rb skill + alt labels |
| Bahasa | 27 bahasa Eropa - **Indonesian tidak ada** | Inggris |
| Format | CSV/RDF + API publik gratis | Dataset unduhan |
| Lisensi | Gratis + atribusi (EU reuse policy) | Terbuka - verifikasi lisensi saat eksekusi |
| Relasi antar skill | ADA (broader/narrower/related) - bahan transferable credit otomatis | Terbatas |
| Pemetaan okupasi | ADA - fondasi alami pivot suggestions nanti | Tidak |

Keputusan sumber: ESCO sebagai primer (relasi + okupasi + API), Lightcast
sebagai suplemen. Keduanya di-bundle OFFLINE ke deployment (beberapa MB) -
bukan API live - supaya determinisme dan privasi terjaga.

## 5. Risiko dan Penangkal (disepakati user)

| Risiko | Penangkal |
|---|---|
| **Gravity arsitektur** (terjerumus jadi "kulit ESCO") | ESCO hanya LAPISAN LOOKUP. Dilarang menyentuh formula skor, bobot, hard filter, filosofi verdict. Semua keputusan nilai tetap milik SIGAP Engine. |
| **Drift skor diam-diam** (over-credit via relasi "related" yang luas) | Label/alt-label persis -> boleh met. Relasi "related" -> maksimal partial. Rerun 10 test set sebagai GERBANG: kasus selaras tidak boleh bergeser dari 80-92. |
| **Ketergantungan & non-determinisme** (API live) | Dataset di-bundle offline, versi data terkunci, update ESCO = keputusan eksplisit + rerun eval. |
| **Lisensi** | ESCO gratis + atribusi. Lightcast: cek lisensi persisnya sebelum dipakai. |
| **Coverage bahasa Indonesia** | Tidak ada di ESCO/Lightcast - karena itu kamus lokal Indonesia TETAP ADA sebagai Lapis 1 (dipangkas jadi istilah lokal saja), dan Lapis 3 (LLM) menangani parafrasa bilingual. |

## 6. Pertanyaan Terbuka untuk Gemini Advisor

1. **Ukuran tier:** apakah ESCO related-skill relation terlalu luas untuk
   dipakai sebagai sumber partial credit? Alternatif: hanya broader/narrower
   (hierarki langsung) yang dihitung partial, related diabaikan.
2. **Urutan lapis:** apakah ESCO lookup sebaiknya SEBELUM atau SESUDAH kamus
   lokal Indonesia? Pendapat ZCode: sesudah (istilah lokal lebih spesifik
   untuk pasar kita, ESCO menangani sisanya yang global).
3. **ESCO okupasi mapping:** layakkah dipakai sebagai dasar fitur pivot
   suggestions (okupasi Eropa vs pasar Indonesia), atau cukup skill relation
   saja dulu?
4. **Verifikasi bukti Lapis 3:** LLM mengutip bukti verbatim dari CV, mesin
   cek keberadaannya. Apakah cukup, atau perlu cek tambahan (mis. token
   overlap minimum antara bukti dan skill)?

## 7. Rencana Implementasi (setelah persetujuan final)

1. **Feasibility check (30 menit):** unduh ESCO CSV, grep istilah gagal kita
   (root-cause analysis, team leadership, stocktaking, FEFO) - ukur coverage.
   Angka ini memutuskan layak/tidaknya lanjut.
2. **Import script:** ESCO CSV -> JSON ringkas (label, alt-labels, related,
   broader) di-bundle ke deployment.
3. **Integrasi matcher:** lapis 2 di `_machine_skill_status` (setelah kamus
   lokal, sebelum LLM semantic). Setiap verdict mencatat lapisan mana yang
   mencocokkan (metadata transparansi).
4. **Kamus lokal dipangkas** ke istilah lokal Indonesia saja.
5. **Semantic tier (PLAN-003)**: LLM mengusulkan padanan + bukti verbatim,
   mesin verifikasi, maksimal partial.
6. **Rerun 10 test set + kasus nyata Sales Ops** (target: 5A naik, kasus
   Sales Ops naik, kasus lain tidak bergeser) -> DEVLOG-005.
7. **Kamuskat audit:** verdict metadata (lapisan mana yang match) masuk
   respons untuk transparansi "AI that shows its work".

Estimasi: 1 hari (feasibility 30 menit + import 2 jam + integrasi 2 jam +
rerun/verifikasi 1 jam).

## 8. Definisi "Selesai Endless Fix"

Bukan "tidak ada bug lagi". Melainkan: perbaikan berhenti berbentuk kode
(ngetik kamus) dan berubah bentuk menjadi data + evaluasi:
- domain baru bermasalah? -> tambah KASUS TEST (5 menit, tanpa kode), lapis
  2-3 yang menanganinya
- perubahan engine? -> rerun 10 kasus, lolos/tidak lolos berdasarkan target
- sisanya: feedback produk dari beta tester
