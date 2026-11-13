"""
Buat catatan AIRun untuk dokumen yang diunggah sebelum fitur
"Kinerja AI" ada, dari hasil Jalur B yang tersimpan di metadata.
Hanya menambah data; dokumen yang sudah punya AIRun dilewati.
"""

from django.db import migrations


def _error_type(message):
    text = (message or "").lower()
    if "503" in text or "unavailable" in text:
        return "unavailable"
    if "504" in text or "deadline" in text or "timeout" in text or "timed out" in text:
        return "timeout"
    if "429" in text or "resource_exhausted" in text:
        return "quota"
    if "getaddrinfo" in text or "connect" in text:
        return "connection"
    if "tidak ada teks" in text:
        return "no_text"
    if "json" in text or "format" in text:
        return "invalid_response"
    return "other"


def forwards(apps, schema_editor):
    Document = apps.get_model("documents", "Document")
    AIRun = apps.get_model("audits", "AIRun")

    for document in Document.objects.all().iterator():
        if AIRun.objects.filter(document=document).exists():
            continue
        jalur_b = (document.metadata or {}).get("jalur_b")
        if not isinstance(jalur_b, dict):
            continue

        error = jalur_b.get("error")
        findings = jalur_b.get("findings") or []
        failed = bool(error) or not findings

        run = AIRun.objects.create(
            document=document,
            trigger="upload",
            status="failed" if failed else "success",
            error_type=_error_type(error) if failed else "",
            error_message=(error or "")[:2000] if failed else "",
            rule_version=0,
            findings=[
                {
                    "source": "semantic",
                    "category": f.get("category") or "",
                    "status": "passed" if f.get("status") == "passed" else "failed",
                    "detail": f.get("issue", ""),
                    "location": f.get("location", ""),
                }
                for f in findings
                if isinstance(f, dict)
            ],
        )
        # Samakan waktu dengan waktu upload aslinya.
        AIRun.objects.filter(pk=run.pk).update(created_at=document.uploaded_at)


def backwards(apps, schema_editor):
    # Tidak bisa membedakan data hasil backfill dengan data baru secara pasti;
    # biarkan (tabel AIRun dihapus oleh migration sebelumnya jika di-rollback).
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("audits", "0003_airun_findingfeedback"),
        ("documents", "0003_map_old_document_types"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
