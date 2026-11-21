"""
Prompt pemeriksaan semantik (Jalur B).

Instruksi tiap aspek disimpan di MasterRule (kategori "semantic") agar
admin bisa memperbaikinya dari Web Dashboard saat menemukan pola
kesalahan AI. DEFAULT_ASPECTS dipakai jika aturan belum ada di database
(isinya sama dengan prompt awal, dipecah per aspek).
"""

# Urutan = urutan aspek di prompt. key = kategori baku (SEMANTIC_CATEGORIES).
DEFAULT_ASPECTS = [
    {
        "key": "sitasi",
        "label": "Sitasi & kepustakaan",
        "instruction": (
            "Gaya sitasi dalam naskah mengikuti Harvard-APA, format \"(Nama, Tahun)\". "
            "Setiap sumber yang dikutip dalam naskah WAJIB ada di Daftar Pustaka, dan sebaliknya. "
            "Catatan kaki (footnote) hanya untuk keterangan tambahan/penjelas, bukan pengganti sitasi utama."
        ),
    },
    {
        "key": "daftar_isi",
        "label": "Daftar isi, tabel, gambar & lampiran",
        "instruction": (
            "Periksa kecocokan daftar isi, daftar tabel, daftar gambar, dan lampiran: "
            "penomoran harus berurutan dan konsisten dengan isi naskah."
        ),
    },
    {
        "key": "hierarki_bab",
        "label": "Hierarki & urutan bab",
        "instruction": (
            "Urutan bab baku: Pendahuluan -> Tinjauan Pustaka -> Metodologi -> (Hasil/Pembahasan) -> Daftar Pustaka. "
            "Judul bab wajib huruf kapital semua dan dicetak tebal (bold). "
            "Judul subbab: huruf kapital hanya di awal tiap kata (title case), bold bersifat opsional."
        ),
    },
    {
        "key": "abstrak",
        "label": "Abstrak",
        "instruction": (
            "Abstrak maksimal 250 kata, ditulis dalam SATU paragraf. "
            "Wajib memiliki 3-5 kata kunci."
        ),
    },
    {
        "key": "tata_bahasa",
        "label": "Tata bahasa & istilah asing",
        "instruction": (
            "Penulisan mengikuti kaidah KBBI/PUEBI. Istilah asing atau nama ilmiah (kata latin) "
            "yang belum ada padanan bahasa Indonesia-nya WAJIB dicetak miring (italic). "
            "Teks yang dicetak miring di dokumen asli ditandai _seperti ini_. Istilah asing "
            "yang sudah bertanda _..._ berarti SUDAH benar; laporkan hanya istilah asing yang "
            "tidak bertanda."
        ),
    },
    {
        "key": "benang_merah",
        "label": "Benang merah penelitian",
        "instruction": (
            "Periksa kelogisan benang merah penelitian: rumusan masalah -> tujuan -> "
            "pembahasan harus saling berkaitan."
        ),
    },
    {
        "key": "konsistensi_istilah",
        "label": "Konsistensi istilah teknis",
        "instruction": "Istilah teknis harus ditulis konsisten di seluruh naskah.",
    },
]


# Batas teks yang dikirim ke AI. Dokumen kampus rata-rata ±1.300 karakter
# per halaman, jadi 250.000 karakter ≈ 180-200 halaman: cukup untuk
# skripsi tebal, tetapi file yang luar biasa besar tidak menghabiskan kuota.
# (Dulu 12.000 = hanya ±9 halaman pertama, sehingga AI tidak pernah melihat
# BAB III maupun Daftar Pustaka dan hasilnya menebak-nebak.)
MAX_TEXT_CHARS = 250_000


def build_semantic_prompt(full_text, document_type=None, aspects=None, chapters=None):
    """
    Prompt pemeriksaan semantik sesuai Panduan Penulisan Karya Ilmiah
    Politeknik Negeri Lampung.

    aspects: daftar {"key", "label", "instruction"} yang aktif.
    Jika None, memakai DEFAULT_ASPECTS.
    chapters: nama bab hasil pembagian dokumen, agar AI menyebut bab
    tempat setiap masalah (kesalahan ditampilkan per bab).
    """
    doc_label = document_type or "karya tulis ilmiah"
    aspects = DEFAULT_ASPECTS if aspects is None else aspects

    rules = "\n\n".join(
        f"{number}. {aspect['label'].upper()} (category: \"{aspect['key']}\")\n"
        f"{aspect['instruction'].strip()}"
        for number, aspect in enumerate(aspects, start=1)
    )
    categories = " / ".join(f"\"{aspect['key']}\"" for aspect in aspects)

    text = full_text[:MAX_TEXT_CHARS]
    truncated_note = (
        "\nCatatan: dokumen ini sangat panjang, sehingga teks di bawah hanya "
        "bagian awalnya. Jangan laporkan bagian yang tidak terlihat (mis. "
        "Daftar Pustaka di akhir) sebagai tidak ada.\n"
        if len(full_text) > MAX_TEXT_CHARS
        else ""
    )
    chapter_names = ", ".join(f'"{name}"' for name in chapters or [])
    chapter_rule = (
        f"Bab dalam dokumen ini (urut): {chapter_names}.\n"
        "Isi \"chapter\" dengan SATU nama bab dari daftar itu (tulis persis), "
        "\"Halaman sampul\" atau \"Halaman awal\" untuk bagian sebelum bab pertama, "
        "atau \"Seluruh dokumen\" jika masalahnya menyeluruh/tidak di satu bab."
        if chapter_names
        else "Isi \"chapter\" dengan nama bab tempat masalah (mis. \"BAB I PENDAHULUAN\"), "
        "atau \"Seluruh dokumen\" jika masalahnya menyeluruh."
    )

    return f"""
Kamu adalah pemeriksa format {doc_label} yang mengacu PERSIS pada Panduan
Penulisan Karya Ilmiah Politeknik Negeri Lampung. Gunakan aturan berikut
sebagai acuan saat memeriksa (bukan aturan umum/standar kampus lain).

Catatan teks: setiap baris adalah satu paragraf. Bagian yang dicetak
miring (italic) di dokumen asli ditandai dengan garis bawah, _seperti ini_.

Periksa teks terhadap {len(aspects)} aspek berikut beserta aturannya:

{rules}

Balas HANYA dalam format JSON (tanpa teks tambahan di luar JSON).
Untuk SETIAP aspek di atas, berikan SATU entri berstatus "passed"
(jika sesuai) atau SATU/LEBIH entri berstatus "failed" (jika ada masalah).
Jangan melewatkan aspek apa pun, agar skor dapat dihitung secara adil.
Nilai "category" WAJIB persis salah satu dari: {categories}.
Untuk entri "failed", isi "severity" sesuai beratnya kesalahan:
- "ringan": kesalahan kecil/sedikit (mis. 1-2 istilah asing belum dimiringkan, salah ketik)
- "sedang": kesalahan yang cukup sering atau mengganggu (mis. istilah tidak konsisten di beberapa tempat, sisa tulisan draf)
- "berat": aturan utama dilanggar atau bagian wajib tidak ada (mis. gaya sitasi salah total, daftar isi tidak ada)
Jika satu aspek punya beberapa masalah berbeda, buat entri terpisah untuk setiap masalah.
{chapter_rule}
{{
  "findings": [
    {{
      "category": {categories},
      "issue": "deskripsi singkat; untuk status failed sebutkan aturan Polinela yang dilanggar",
      "chapter": "nama bab tempat masalah (lihat aturan di atas)",
      "location": "bagian/kalimat yang bermasalah (kutip singkat) atau \\"Lokasi tidak diketahui\\"",
      "status": "passed" atau "failed",
      "severity": "ringan" / "sedang" / "berat" (hanya untuk status failed)
    }}
  ]
}}

{truncated_note}
Teks yang akan diperiksa:
{text}
"""
