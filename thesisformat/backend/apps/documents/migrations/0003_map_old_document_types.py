from django.db import migrations

# Jenis dokumen lama -> jenis baru (Panduan Polinela).
# "laporan" tidak dipetakan karena dulu dipakai untuk beberapa jenis sekaligus.
OLD_TO_NEW = {
    "skripsi": "tugas_akhir",
    "proposal": "proposal_penelitian",
}


def forwards(apps, schema_editor):
    Document = apps.get_model("documents", "Document")
    for old, new in OLD_TO_NEW.items():
        Document.objects.filter(document_type=old).update(document_type=new)


def backwards(apps, schema_editor):
    Document = apps.get_model("documents", "Document")
    for old, new in OLD_TO_NEW.items():
        Document.objects.filter(document_type=new).update(document_type=old)


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0002_alter_document_document_type"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
