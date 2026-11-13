"""
Isi aturan semantik (instruksi AI per aspek) dengan instruksi bawaan,
agar admin bisa mengeditnya dari Web Dashboard. Hanya menambah aturan
yang belum ada; aturan yang sudah ada tidak diubah.
"""

from django.db import migrations

# Disalin dari apps/documents/semantic/prompts.py (DEFAULT_ASPECTS) saat
# migration dibuat, agar migration tidak berubah jika kode berubah.
ASPECTS = [
    ("sitasi", "Sitasi & kepustakaan",
     "Gaya sitasi dalam naskah mengikuti Harvard-APA, format \"(Nama, Tahun)\". "
     "Setiap sumber yang dikutip dalam naskah WAJIB ada di Daftar Pustaka, dan sebaliknya. "
     "Catatan kaki (footnote) hanya untuk keterangan tambahan/penjelas, bukan pengganti sitasi utama."),
    ("daftar_isi", "Daftar isi, tabel, gambar & lampiran",
     "Periksa kecocokan daftar isi, daftar tabel, daftar gambar, dan lampiran: "
     "penomoran harus berurutan dan konsisten dengan isi naskah."),
    ("hierarki_bab", "Hierarki & urutan bab",
     "Urutan bab baku: Pendahuluan -> Tinjauan Pustaka -> Metodologi -> (Hasil/Pembahasan) -> Daftar Pustaka. "
     "Judul bab wajib huruf kapital semua dan dicetak tebal (bold). "
     "Judul subbab: huruf kapital hanya di awal tiap kata (title case), bold bersifat opsional."),
    ("abstrak", "Abstrak",
     "Abstrak maksimal 250 kata, ditulis dalam SATU paragraf. Wajib memiliki 3-5 kata kunci."),
    ("tata_bahasa", "Tata bahasa & istilah asing",
     "Penulisan mengikuti kaidah KBBI/PUEBI. Istilah asing atau nama ilmiah (kata latin) "
     "yang belum ada padanan bahasa Indonesia-nya WAJIB dicetak miring (italic). "
     "Karena cetak miring tidak terbaca dari teks polos, anggap istilah teknis berbahasa "
     "Inggris seperti \"database\" atau \"framework\" sebagai kandidat yang perlu dicek "
     "manual oleh pengguna."),
    ("benang_merah", "Benang merah penelitian",
     "Periksa kelogisan benang merah penelitian: rumusan masalah -> tujuan -> "
     "pembahasan harus saling berkaitan."),
    ("konsistensi_istilah", "Konsistensi istilah teknis",
     "Istilah teknis harus ditulis konsisten di seluruh naskah."),
]


def forwards(apps, schema_editor):
    MasterRule = apps.get_model("rules", "MasterRule")
    for key, label, instruction in ASPECTS:
        exists = MasterRule.objects.filter(
            category="semantic", document_type="", rule_key=key,
        ).exists()
        if not exists:
            MasterRule.objects.create(
                category="semantic",
                document_type="",
                rule_key=key,
                rule_value={"label": label, "instruction": instruction},
                description=f"Instruksi AI untuk aspek {label}",
                active=True,
            )


def backwards(apps, schema_editor):
    MasterRule = apps.get_model("rules", "MasterRule")
    MasterRule.objects.filter(
        category="semantic",
        document_type="",
        rule_key__in=[key for key, _, _ in ASPECTS],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rules", "0003_ruleversion"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
