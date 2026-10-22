
import logging
import traceback

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.rules.models import MasterRule

from .parser.jalur_a_service import run_jalur_a
from .semantic.jalur_b_service import run_jalur_b
from .serializers import DocumentSerializer


logger = logging.getLogger(__name__)


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Validasi data upload.
        serializer = DocumentSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "detail": "Data dokumen tidak valid.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Simpan dokumen milik pengguna yang sedang login.
        document = serializer.save(user=request.user)

        try:
            # 3. Ambil aturan fisik aktif dari database.
            physical_rules = MasterRule.objects.filter(
                category=MasterRule.Category.PHYSICAL,
                active=True,
            )

            # 4. Jalankan Jalur A: parsing dan pemeriksaan fisik.
            jalur_a_result = run_jalur_a(
                document.file.path,
                rules=physical_rules,
            )

            # 5. Jalankan Jalur B: pemeriksaan semantik.
            # Jika Gemini gagal, hasil Jalur A tetap bisa disimpan.
            try:
                jalur_b_result = run_jalur_b(
                    jalur_a_result["parsed_document"],
                    document_type=document.document_type,
                )

            except Exception as exc:
                logger.exception(
                    "Jalur B gagal. Document ID: %s",
                    document.id,
                )

                jalur_b_result = {
                    "raw_response": "",
                    "findings": [],
                    "summary": {
                        "passed": 0,
                        "failed": 0,
                        "total": 0,
                    },
                    "error": str(exc),
                }

            # 6. Gabungkan temuan kedua jalur.
            findings_a = jalur_a_result.get("findings", [])
            findings_b = jalur_b_result.get("findings", [])

            all_findings = findings_a + findings_b

            summary = {
                "physical": jalur_a_result.get("summary", {}),
                "semantic": jalur_b_result.get("summary", {}),
                "total_findings": len(all_findings),
            }

            # 7. Simpan hasil pemeriksaan pada metadata.
            document.metadata = {
                **(document.metadata or {}),
                "jalur_a": jalur_a_result,
                "jalur_b": jalur_b_result,
                "summary": summary,
            }

            document.status = "completed"
            document.save(
                update_fields=[
                    "metadata",
                    "status",
                    "updated_at",
                ]
            )

            # 8. Kirim hasil pemeriksaan ke Flutter.
            return Response(
                {
                    "document": DocumentSerializer(document).data,
                    "jalur_a": jalur_a_result,
                    "jalur_b": jalur_b_result,
                    "findings": all_findings,
                    "summary": summary,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as exc:
            # 9. Catat error lengkap di terminal Django.
            logger.exception(
                "Pemeriksaan dokumen gagal. Document ID: %s",
                document.id,
            )

            traceback.print_exc()

            # 10. Tandai dokumen sebagai gagal.
            document.status = "failed"
            document.save(
                update_fields=["status", "updated_at"]
            )

            # 11. Kirim informasi error untuk proses debugging.
            return Response(
                {
                    "detail": "Pemeriksaan dokumen gagal.",
                    "error": str(exc),
                    "document_id": document.id,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
