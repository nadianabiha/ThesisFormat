"""
Sesuaikan aturan dengan Pedoman Penulisan Karya Ilmiah Politeknik
Negeri Lampung 2018. Dicatat sebagai SATU versi aturan (RuleVersion) agar
kinerja sebelum & sesudah bisa dibandingkan di halaman "Kinerja AI".

Aturan format (Jalur A):
  * Ukuran font, perataan, dan spasi hanya dicek pada TEKS ISI
    (judul bab 14 pt/tebal/rata tengah dan tabel 10 pt memang berbeda, 1.4).
  * Tambah aturan margin: atas 3, bawah 3, kanan 3, kiri 4 cm (1.4.3).

Instruksi AI (Jalur B):
  * Susunan bab mengikuti garis besar tiap jenis dokumen (Contoh 28-33),
    sebagai aturan khusus per jenis dokumen.
"""

from django.db import migrations

GUIDE = "Pedoman Penulisan Karya Ilmiah Polinela 2018"

# ---------------------------------------------------------------------------
# Aturan format (Jalur A)
# ---------------------------------------------------------------------------

BODY_SCOPED = ("font_size", "alignment", "line_spacing")

MARGIN = {"top_margin": 3, "right_margin": 3, "bottom_margin": 3, "left_margin": 4}

# ---------------------------------------------------------------------------
# Instruksi AI (Jalur B): susunan bab per jenis dokumen
# ---------------------------------------------------------------------------

FORMAT_BAB = (
    " Format judul (2.2.2): judul bab seluruhnya huruf kapital, dicetak tebal, "
    "di tengah (nomor bab angka romawi besar I, II, III bersifat opsional). "
    "Judul subbab: huruf pertama setiap kata kapital kecuali kata penghubung "
    "(penomoran 1.1). Judul sub-subbab: huruf kapital hanya di awal kalimat "
    "(penomoran 1.1.1). Penomoran paling dalam sampai sub-subbab."
)

ONLY_THIS_TYPE = (
    " Nilai susunan bab HANYA berdasarkan garis besar jenis dokumen ini; "
    "jangan menuntut bab milik jenis dokumen lain."
)

GENERAL_HIERARKI = (
    "Susunan bab mengikuti garis besar penulisan sesuai jenis dokumen pada "
    f"{GUIDE} (Contoh 28-33). Umumnya: PENDAHULUAN -> bab isi/metode -> "
    "HASIL DAN PEMBAHASAN -> KESIMPULAN (DAN SARAN) -> DAFTAR PUSTAKA -> "
    "LAMPIRAN (jika ada)." + FORMAT_BAB
)

HIERARKI_PER_TYPE = {
    "praktik": (
        "Laporan Praktik Mahasiswa (Contoh 33). Halaman judul memuat judul, "
        "nama penulis, NPM, logo, nama institusi, kota, dan tahun. Susunan bab: "
        "I. PENDAHULUAN; II. TUJUAN PRAKTIKUM; III. METODE PELAKSANAAN; "
        "IV. HASIL PENGAMATAN DAN PEMBAHASAN; V. KESIMPULAN; DAFTAR PUSTAKA; "
        "LAMPIRAN (jika ada). Laporan praktik TIDAK wajib memiliki bab Tinjauan "
        "Pustaka, abstrak, atau halaman pengesahan."
    ),
    "pkl": (
        "Laporan PKL/Magang (Contoh 32). Halaman pemula: judul luar, judul dalam, "
        "pengesahan, kata pengantar, daftar isi, daftar tabel/gambar (jika ada). "
        "Susunan bab: I. PENDAHULUAN (1.1 Latar Belakang, 1.2 Tujuan, 1.3 Waktu "
        "dan Tempat Pelaksanaan, 1.4 Metode Pelaksanaan); II. KEADAAN UMUM "
        "(2.1 Letak Geografis, 2.2 Sejarah Singkat, 2.3 Organisasi); "
        "III. PELAKSANAAN KEGIATAN; IV. HASIL DAN PEMBAHASAN; V. KESIMPULAN DAN "
        "SARAN; DAFTAR PUSTAKA; LAMPIRAN (jika ada). Laporan PKL TIDAK wajib "
        "memiliki bab Tinjauan Pustaka."
    ),
    "tugas_akhir": (
        "Laporan Tugas Akhir Mahasiswa (Contoh 31). Halaman pemula: judul luar, "
        "judul dalam, pengesahan, abstrak, riwayat hidup, persembahan, motto "
        "(jika ada), kata pengantar, daftar isi, daftar tabel/gambar/lampiran "
        "(jika ada). Susunan bab: I. PENDAHULUAN (1.1 Latar Belakang dan Masalah, "
        "1.2 Tujuan, 1.3 Kerangka Pemikiran, 1.4 Hipotesis jika diperlukan, "
        "1.5 Kontribusi); II. TINJAUAN PUSTAKA; III. METODE PELAKSANAAN (3.1 Tempat "
        "dan Waktu, 3.2 Bahan dan Alat, 3.3 Perancangan Percobaan dan Analisis Data, "
        "3.4 Prosedur Kerja, 3.5 Pengamatan); IV. HASIL DAN PEMBAHASAN; "
        "V. KESIMPULAN DAN SARAN; DAFTAR PUSTAKA; LAMPIRAN (jika ada)."
    ),
    "proposal_penelitian": (
        "Usul/Proposal Penelitian (Contoh 29A). Halaman pemula: judul luar, judul "
        "dalam, pengesahan, kata pengantar, daftar isi, daftar tabel/gambar (jika "
        "ada). Susunan bab: I. PENDAHULUAN (Latar Belakang, Tujuan Penelitian, "
        "Kerangka Pemikiran, Hipotesis, Kontribusi Penelitian); II. TINJAUAN "
        "PUSTAKA; III. METODE PELAKSANAAN (Tempat dan Waktu, Bahan dan Alat, "
        "Rancangan Penelitian, Pelaksanaan Penelitian, Pengamatan, Jadwal "
        "Penelitian, Personalia Penelitian); IV. RENCANA ANGGARAN BIAYA PENELITIAN; "
        "DAFTAR PUSTAKA; LAMPIRAN. Jika dokumen ternyata LAPORAN penelitian "
        "(Contoh 29B), bab IV dan seterusnya: IV. HASIL DAN PEMBAHASAN; "
        "V. KESIMPULAN; DAFTAR PUSTAKA; LAMPIRAN (jika ada)."
    ),
    "proposal_pengabdian": (
        "Usul/Proposal Pengabdian kepada Masyarakat (Contoh 30A). Halaman pemula: "
        "judul luar, judul dalam, pengesahan, kata pengantar, daftar isi, daftar "
        "tabel/gambar (jika ada). Susunan bab: I. PENDAHULUAN (1.1 Analisis Situasi, "
        "1.2 Identifikasi dan Perumusan Masalah, 1.3 Kerangka Pemecahan Masalah, "
        "1.4 Tujuan Kegiatan, 1.5 Manfaat Kegiatan); II. TINJAUAN PUSTAKA; "
        "III. METODE PENGABDIAN (Tempat dan Waktu, Khalayak Sasaran dan Cara "
        "Pelaksanaan, Rancangan Evaluasi Keberhasilan Pengabdian, Organisasi "
        "Pelaksana, Jadwal Pengabdian); IV. RENCANA ANGGARAN BIAYA; DAFTAR PUSTAKA; "
        "LAMPIRAN. Jika dokumen ternyata LAPORAN pengabdian (Contoh 30B), bab IV dan "
        "seterusnya: IV. HASIL DAN PEMBAHASAN; V. KESIMPULAN DAN SARAN; DAFTAR "
        "PUSTAKA; LAMPIRAN."
    ),
    "makalah_ilmiah": (
        "Makalah Ilmiah (Contoh 28). JUDUL dan nama penulis ditulis simetris dengan "
        "notasi superscript yang dijelaskan sebagai catatan kaki; ABSTRAK; "
        "I. PENDAHULUAN (1.1 Latar Belakang, 1.2 Tujuan); II. METODOLOGI; "
        "III. HASIL DAN PEMBAHASAN (jika hasil penelitian); IV. KESIMPULAN DAN "
        "SARAN/PENUTUP; V. UCAPAN TERIMA KASIH (jika ada); DAFTAR PUSTAKA; "
        "LAMPIRAN (opsional). Makalah TIDAK wajib memiliki bab Tinjauan Pustaka."
    ),
}

HIERARKI_LABEL = "Hierarki & urutan bab"

NOTE = (
    f"Penyesuaian {GUIDE}: format dicek pada teks isi, margin 4-3-3-3 cm, "
    "susunan bab per jenis dokumen"
)


def _value(rule):
    return dict(rule.rule_value) if isinstance(rule.rule_value, dict) else {"value": rule.rule_value}


def forwards(apps, schema_editor):
    MasterRule = apps.get_model("rules", "MasterRule")
    RuleVersion = apps.get_model("rules", "RuleVersion")

    # ----- Aturan format -----
    changes_a = []
    for rule in MasterRule.objects.filter(
        category="physical", document_type="", rule_key__in=BODY_SCOPED,
    ):
        value = _value(rule)
        if value.get("scope") == "body":
            continue
        before = {"value": value.get("value"), "scope": value.get("scope", "all")}
        value["scope"] = "body"
        rule.rule_value = value
        rule.save(update_fields=["rule_value", "updated_at"])
        changes_a.append({
            "rule_id": rule.pk, "rule_key": rule.rule_key, "category": "physical",
            "document_type": "", "before": before,
            "after": {"value": value.get("value"), "scope": "body"},
        })

    if not MasterRule.objects.filter(category="physical", rule_key="margin").exists():
        rule = MasterRule.objects.create(
            category="physical",
            document_type="",
            rule_key="margin",
            rule_value={"value": MARGIN},
            description="Batas tepi pengetikan (Pedoman 1.4.3)",
            active=True,
        )
        changes_a.append({
            "rule_id": rule.pk, "rule_key": "margin", "category": "physical",
            "document_type": "", "before": None, "after": {"value": MARGIN, "active": True},
        })

    # ----- Instruksi AI: susunan bab per jenis dokumen -----
    changes_b = []
    general = MasterRule.objects.filter(
        category="semantic", document_type="", rule_key="hierarki_bab",
    ).first()
    if general is not None:
        value = _value(general)
        if value.get("instruction") != GENERAL_HIERARKI:
            before = value.get("instruction", "")
            value["instruction"] = GENERAL_HIERARKI
            general.rule_value = value
            general.save(update_fields=["rule_value", "updated_at"])
            changes_b.append({
                "rule_id": general.pk, "rule_key": "hierarki_bab", "category": "semantic",
                "document_type": "", "before": {"instruction": before},
                "after": {"instruction": GENERAL_HIERARKI},
            })

    for document_type, outline in HIERARKI_PER_TYPE.items():
        if MasterRule.objects.filter(
            category="semantic", document_type=document_type, rule_key="hierarki_bab",
        ).exists():
            continue
        instruction = outline + ONLY_THIS_TYPE + FORMAT_BAB
        rule = MasterRule.objects.create(
            category="semantic",
            document_type=document_type,
            rule_key="hierarki_bab",
            rule_value={"label": HIERARKI_LABEL, "instruction": instruction},
            description=f"Susunan bab khusus jenis dokumen ini ({GUIDE})",
            active=True,
        )
        changes_b.append({
            "rule_id": rule.pk, "rule_key": "hierarki_bab", "category": "semantic",
            "document_type": document_type, "before": None,
            "after": {"instruction": instruction, "active": True},
        })

    # Satu versi untuk seluruh penyesuaian Pedoman.
    if changes_a or changes_b:
        RuleVersion.objects.create(note=NOTE, changes=changes_a + changes_b)


def backwards(apps, schema_editor):
    MasterRule = apps.get_model("rules", "MasterRule")
    RuleVersion = apps.get_model("rules", "RuleVersion")

    for version in RuleVersion.objects.filter(note=NOTE):
        for change in version.changes or []:
            rule = MasterRule.objects.filter(pk=change["rule_id"]).first()
            if rule is None:
                continue
            before = change.get("before")
            if before is None:
                rule.delete()  # aturan yang dibuat oleh migration ini
                continue
            value = _value(rule)
            if "instruction" in before:
                value["instruction"] = before["instruction"]
            if "scope" in before:
                value.pop("scope", None)
            rule.rule_value = value
            rule.save(update_fields=["rule_value", "updated_at"])
        version.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rules", "0004_seed_semantic_aspects"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
