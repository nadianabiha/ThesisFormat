"""
Letak nomor halaman tidak dinilai (keputusan tim).

Pedoman Polinela 2018 (1.5.1 c-d) menulis nomor halaman "di tepi kanan
halaman satu spasi di bawah/atas margin", yang tidak tegas menjelaskan
posisinya. Agar mahasiswa tidak kehilangan poin karena tafsiran, yang
dinilai hanya yang jelas: ada nomor halaman, halaman depan memakai angka
romawi kecil, dan halaman isi memakai angka Arab. Letak (atas/bawah,
kiri/kanan) diset "Tidak dicek" dan bisa diaktifkan lagi oleh admin.
"""

from django.db import migrations

NOTE = "Nomor halaman: letak tidak dinilai (pedoman ambigu), hanya format romawi/Arab"


def forwards(apps, schema_editor):
    MasterRule = apps.get_model("rules", "MasterRule")
    RuleVersion = apps.get_model("rules", "RuleVersion")

    changes = []
    for rule in MasterRule.objects.filter(category="physical", rule_key="page_number"):
        value = dict(rule.rule_value) if isinstance(rule.rule_value, dict) else {}
        before = value.get("value") or {}
        after = {
            group: {**(before.get(group) or {}), "vertical": None, "horizontal": None}
            for group in ("front", "body")
        }
        if after == before:
            continue
        value["value"] = after
        rule.rule_value = value
        rule.save(update_fields=["rule_value", "updated_at"])
        changes.append({
            "rule_id": rule.pk, "rule_key": "page_number", "category": "physical",
            "document_type": rule.document_type,
            "before": {"value": before, "active": rule.active},
            "after": {"value": after, "active": rule.active},
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
            value = dict(rule.rule_value) if isinstance(rule.rule_value, dict) else {}
            value["value"] = change["before"]["value"]
            rule.rule_value = value
            rule.save(update_fields=["rule_value", "updated_at"])
        version.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("rules", "0008_abstrak_per_jenis"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
