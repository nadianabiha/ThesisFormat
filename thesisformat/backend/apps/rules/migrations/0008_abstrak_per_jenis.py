"""
Pemeriksaan abstrak per jenis dokumen (keputusan tim, mengacu Pedoman
Penulisan Karya Ilmiah Polinela 2018: abstrak adalah bagian karya ilmiah
seperti tugas akhir dan makalah, bukan proposal/laporan praktik/PKL).

  Jenis dokumen            Cek abstrak
  Proposal Penelitian      Tidak  (aturan khusus, Nonaktif)
  Laporan Praktik          Tidak  (aturan khusus, Nonaktif)
  Laporan PKL/Magang       Tidak  (aturan khusus, Nonaktif)
  Proposal Pengabdian      Bisa diatur admin (aturan khusus, Aktif)
  Tugas Akhir/Skripsi      Ya     (aturan umum)
  Makalah Ilmiah           Ya     (aturan umum)

Disimpan di Master Rules (bukan di kode), sehingga admin bisa mengubahnya
dari web -> Aturan. Dicatat sebagai satu versi aturan (RuleVersion).
"""

from django.db import migrations

NOT_CHECKED = ("proposal_penelitian", "praktik", "pkl")
ADMIN_CHOICE = ("proposal_pengabdian",)

NOTE = "Abstrak per jenis dokumen: tidak dicek untuk proposal penelitian, laporan praktik, dan PKL"
LABEL = "Abstrak"


def forwards(apps, schema_editor):
    MasterRule = apps.get_model("rules", "MasterRule")
    RuleVersion = apps.get_model("rules", "RuleVersion")

    general = MasterRule.objects.filter(
        category="semantic", rule_key="abstrak", document_type="",
    ).first()
    if general is None:
        return
    value = general.rule_value if isinstance(general.rule_value, dict) else {}
    rule_value = {"label": value.get("label") or LABEL, "instruction": value.get("instruction", "")}

    changes = []
    for document_type in NOT_CHECKED + ADMIN_CHOICE:
        if MasterRule.objects.filter(
            category="semantic", rule_key="abstrak", document_type=document_type,
        ).exists():
            continue
        active = document_type in ADMIN_CHOICE
        rule = MasterRule.objects.create(
            category="semantic",
            document_type=document_type,
            rule_key="abstrak",
            rule_value=rule_value,
            description=(
                "Abstrak untuk jenis dokumen ini dapat diaktifkan/dinonaktifkan admin"
                if active else "Jenis dokumen ini tidak wajib memiliki abstrak"
            ),
            active=active,
        )
        changes.append({
            "rule_id": rule.pk, "rule_key": "abstrak", "category": "semantic",
            "document_type": document_type, "before": None,
            "after": {"instruction": rule_value["instruction"], "active": active},
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
        ("rules", "0007_layout_rules"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
