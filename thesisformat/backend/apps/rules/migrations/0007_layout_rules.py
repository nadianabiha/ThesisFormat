"""
Aturan tata letak dari Pedoman Penulisan Karya Ilmiah Polinela 2018
(sesuai Laporan Perancangan, Jalur A):
  * paper_size  : kertas A4, 21 x 29,7 cm (1.2.1)
  * page_number : halaman awal angka romawi kecil di kanan bawah, bagian
                  isi angka Arab di kanan atas mulai Pendahuluan (1.5.1)
  * logo_size   : logo sampul 4 x 3,6 cm (1.3.4)
  * cover       : sampul memuat logo, nama & NPM, institusi, tahun (1.3)
Nilainya bisa diubah admin lewat Master Rules. Dicatat sebagai satu versi
aturan (RuleVersion).
"""

from django.db import migrations

GUIDE = "Pedoman Penulisan Karya Ilmiah Polinela 2018"

RULES = [
    (
        "paper_size",
        {"value": {"width_cm": 21, "height_cm": 29.7, "tolerance_cm": 0.2}},
        "Ukuran kertas A4 21 x 29,7 cm (Pedoman 1.2.1)",
    ),
    (
        "page_number",
        {"value": {
            "front": {"format": "roman_lower", "vertical": "bottom", "horizontal": "right"},
            "body": {"format": "arabic", "vertical": "top", "horizontal": "right"},
        }},
        "Nomor halaman: halaman awal romawi kecil kanan bawah, isi angka Arab "
        "kanan atas mulai Pendahuluan (Pedoman 1.5.1)",
    ),
    (
        "logo_size",
        {"value": {"width_cm": 4, "height_cm": 3.6, "tolerance_cm": 0.3}},
        "Ukuran logo Polinela di sampul 4 x 3,6 cm (Pedoman 1.3.4)",
    ),
    (
        "cover",
        {"value": {
            "required": ["logo", "npm", "institusi", "tahun"],
            "institution": "POLITEKNIK NEGERI LAMPUNG",
        }},
        "Kelengkapan sampul: logo, nama & NPM, institusi, tahun (Pedoman 1.3)",
    ),
]

NOTE = f"Aturan tata letak {GUIDE}: ukuran kertas, nomor halaman, ukuran logo, kelengkapan sampul"


def forwards(apps, schema_editor):
    MasterRule = apps.get_model("rules", "MasterRule")
    RuleVersion = apps.get_model("rules", "RuleVersion")

    changes = []
    for key, value, description in RULES:
        if MasterRule.objects.filter(category="physical", rule_key=key).exists():
            continue
        rule = MasterRule.objects.create(
            category="physical",
            document_type="",
            rule_key=key,
            rule_value=value,
            description=description,
            active=True,
        )
        changes.append({
            "rule_id": rule.pk, "rule_key": key, "category": "physical",
            "document_type": "", "before": None, "after": {**value, "active": True},
        })

    if changes:
        RuleVersion.objects.create(note=NOTE, changes=changes)


def backwards(apps, schema_editor):
    MasterRule = apps.get_model("rules", "MasterRule")
    RuleVersion = apps.get_model("rules", "RuleVersion")

    for version in RuleVersion.objects.filter(note=NOTE):
        for change in version.changes or []:
            MasterRule.objects.filter(pk=change["rule_id"]).delete()
        version.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rules", "0006_tata_bahasa_italic"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
