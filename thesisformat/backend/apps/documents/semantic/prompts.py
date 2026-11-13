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
            "Karena cetak miring tidak terbaca dari teks polos, anggap istilah teknis berbahasa "
            "Inggris seperti \"database\" atau \"framework\" sebagai kandidat yang perlu dicek "
            "manual oleh pengguna."
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


def build_semantic_prompt(full_text, document_type=None, aspects=None):
    """
    Prompt pemeriksaan semantik sesuai Panduan Penulisan Karya Ilmiah
    Politeknik Negeri Lampung.

    aspects: daftar {"key", "label", "instruction"} yang aktif.
    Jika None, memakai DEFAULT_ASPECTS.
    """
    doc_label = document_type or "karya tulis ilmiah"
    aspects = DEFAULT_ASPECTS if aspects is None else aspects

    rules = "\n\n".join(
        f"{number}. {aspect['label'].upper()} (category: \"{aspect['key']}\")\n"
        f"{aspect['instruction'].strip()}"
        for number, aspect in enumerate(aspects, start=1)
    )
    categories = " / ".join(f"\"{aspect['key']}\"" for aspect in aspects)

    return f"""
Kamu adalah pemeriksa format {doc_label} yang mengacu PERSIS pada Panduan
Penulisan Karya Ilmiah Politeknik Negeri Lampung. Gunakan aturan berikut
sebagai acuan saat memeriksa (bukan aturan umum/standar kampus lain).

Periksa teks terhadap {len(aspects)} aspek berikut beserta aturannya:

{rules}

Balas HANYA dalam format JSON (tanpa teks tambahan di luar JSON).
Untuk SETIAP aspek di atas, berikan SATU entri berstatus "passed"
(jika sesuai) atau SATU/LEBIH entri berstatus "failed" (jika ada masalah).
Jangan melewatkan aspek apa pun, agar skor dapat dihitung secara adil.
Nilai "category" WAJIB persis salah satu dari: {categories}.
{{
  "findings": [
    {{
      "category": {categories},
      "issue": "deskripsi singkat; untuk status failed sebutkan aturan Polinela yang dilanggar",
      "location": "bagian/kalimat yang bermasalah (kutip singkat) atau \\"Lokasi tidak diketahui\\"",
      "status": "passed" atau "failed"
    }}
  ]
}}

Teks yang akan diperiksa:
{full_text[:12000]}
"""
