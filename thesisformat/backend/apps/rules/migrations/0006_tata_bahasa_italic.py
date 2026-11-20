"""
Instruksi AI "Tata bahasa & istilah asing": AI kini menerima penanda huruf
miring (_..._) dari dokumen, jadi instruksi lama ("cetak miring tidak
terbaca dari teks polos") diganti. Hanya diubah jika admin belum mengubah
instruksinya sendiri. Dicatat sebagai satu versi aturan (RuleVersion).
"""

from django.db import migrations

NOTE = "AI menerima penanda huruf miring: istilah asing yang sudah dimiringkan tidak dilaporkan lagi"

OLD_INSTRUCTION = (
    "Penulisan mengikuti kaidah KBBI/PUEBI. Istilah asing atau nama ilmiah (kata latin) "
    "yang belum ada padanan bahasa Indonesia-nya WAJIB dicetak miring (italic). "
    "Karena cetak miring tidak terbaca dari teks polos, anggap istilah teknis berbahasa "
    "Inggris seperti \"database\" atau \"framework\" sebagai kandidat yang perlu dicek "
    "manual oleh pengguna."
)

NEW_INSTRUCTION = (
    "Penulisan mengikuti kaidah KBBI/PUEBI. Istilah asing atau nama ilmiah (kata latin) "
    "yang belum ada padanan bahasa Indonesia-nya WAJIB dicetak miring (italic). "
    "Teks yang dicetak miring di dokumen asli ditandai _seperti ini_. Istilah asing "
    "yang sudah bertanda _..._ berarti SUDAH benar; laporkan hanya istilah asing yang "
    "tidak bertanda."
)


def forwards(apps, schema_editor):
    MasterRule = apps.get_model("rules", "MasterRule")
    RuleVersion = apps.get_model("rules", "RuleVersion")

    changes = []
    for rule in MasterRule.objects.filter(category="semantic", rule_key="tata_bahasa"):
        value = dict(rule.rule_value or {})
        if (value.get("instruction") or "").strip() != OLD_INSTRUCTION:
            continue  # sudah diubah admin: jangan ditimpa
        value["instruction"] = NEW_INSTRUCTION
        rule.rule_value = value
        rule.save(update_fields=["rule_value", "updated_at"])
        changes.append({
            "rule_id": rule.pk, "rule_key": "tata_bahasa", "category": "semantic",
            "document_type": rule.document_type,
            "before": {"instruction": OLD_INSTRUCTION},
            "after": {"instruction": NEW_INSTRUCTION},
        })

    if changes:
        RuleVersion.objects.create(note=NOTE, changes=changes)


def backwards(apps, schema_editor):
    MasterRule = apps.get_model("rules", "MasterRule")
    RuleVersion = apps.get_model("rules", "RuleVersion")

    for version in RuleVersion.objects.filter(note=NOTE):
        for change in version.changes or []:
            rule = MasterRule.objects.filter(pk=change["rule_id"]).first()
            if rule is None:
                continue
            value = dict(rule.rule_value or {})
            value["instruction"] = change["before"]["instruction"]
            rule.rule_value = value
            rule.save(update_fields=["rule_value", "updated_at"])
        version.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rules", "0005_pedoman_polinela_2018"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
