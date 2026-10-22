def build_semantic_prompt(full_text, document_type=None):
    """
    Prompt pemeriksaan semantik sesuai Panduan Penulisan Karya Ilmiah
    Politeknik Negeri Lampung.
    """
    doc_label = document_type or "karya tulis ilmiah"

    return f"""
Kamu adalah pemeriksa format {doc_label} yang mengacu PERSIS pada Panduan
Penulisan Karya Ilmiah Politeknik Negeri Lampung. Gunakan aturan berikut
sebagai acuan saat memeriksa (bukan aturan umum/standar kampus lain):

ATURAN RUJUKAN:
- Gaya sitasi dalam naskah mengikuti Harvard-APA, format "(Nama, Tahun)".
- Setiap sumber yang dikutip dalam naskah WAJIB ada di Daftar Pustaka, dan sebaliknya.
- Catatan kaki (footnote) hanya untuk keterangan tambahan/penjelas, bukan pengganti sitasi utama.

ATURAN STRUKTUR & HIERARKI BAB:
- Urutan bab baku: Pendahuluan -> Tinjauan Pustaka -> Metodologi -> (Hasil/Pembahasan) -> Daftar Pustaka.
- Judul bab wajib huruf kapital semua dan dicetak tebal (bold).
- Judul subbab: huruf kapital hanya di awal tiap kata (title case), bold bersifat opsional.

ATURAN ABSTRAK:
- Abstrak maksimal 250 kata, ditulis dalam SATU paragraf.
- Wajib memiliki 3-5 kata kunci.

ATURAN TATA BAHASA:
- Istilah asing atau nama ilmiah (kata latin) yang belum ada padanan bahasa Indonesia-nya
  WAJIB dicetak miring (italic). Jika dalam teks ada istilah asing yang ditulis tanpa
  penanda miring (tidak bisa dideteksi langsung dari teks polos, maka asumsikan istilah
  teknis berbahasa Inggris seperti "database", "framework", dsb sebagai kandidat yang
  perlu dicek manual oleh pengguna).
- Penulisan mengikuti kaidah KBBI/PUEBI.

Periksa teks berikut terhadap SEMUA aturan di atas, mencakup 7 aspek:
1. Validasi sitasi & kepustakaan (format "(Nama, Tahun)", konsistensi dengan daftar pustaka)
2. Kecocokan daftar isi/tabel/gambar/lampiran (penomoran berurutan & konsisten)
3. Validasi hierarki & urutan bab sesuai struktur baku di atas
4. Kelengkapan & kepatuhan abstrak (maksimal 250 kata, 1 paragraf, 3-5 kata kunci)
5. Tata bahasa sesuai KBBI/PUEBI, dan istilah asing/ilmiah
6. Kelogisan benang merah penelitian (rumusan masalah -> tujuan -> pembahasan nyambung)
7. Konsistensi istilah teknis di seluruh naskah

Balas HANYA dalam format JSON (tanpa teks tambahan di luar JSON):
{{
  "findings": [
    {{
      "category": "sitasi" / "struktur" / "hierarki_bab" / "abstrak" / "tata_bahasa" / "benang_merah" / "konsistensi_istilah",
      "issue": "deskripsi singkat masalahnya, sebutkan aturan Polinela mana yang dilanggar",
      "location": "bagian/kalimat yang bermasalah (kutip singkat)",
      "status": "failed"
    }}
  ]
}}

Jika semua aspek sudah sesuai pedoman, balas dengan:
{{"findings": []}}

Teks yang akan diperiksa:
{full_text[:3000]}
"""