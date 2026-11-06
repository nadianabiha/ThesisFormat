import logging
import traceback

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.rules.models import MasterRule
from .models import Document
from .parser.jalur_a_service import run_jalur_a
from .semantic.jalur_b_service import run_jalur_b
from apps.audits.models import AuditResult
from .scoring import build_result
from .serializers import DocumentSerializer, get_document_result


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

            # 4. Jalankan pemeriksaan fisik (Jalur A).
            jalur_a_result = run_jalur_a(
                document.file.path,
                rules=physical_rules,
            )

            # 5. Jalankan pemeriksaan semantik (Jalur B).
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

            # 6. Gabungkan temuan dari kedua jalur.
            findings_a = jalur_a_result.get("findings", [])
            findings_b = jalur_b_result.get("findings", [])
            all_findings = findings_a + findings_b

            summary = {
                "physical": jalur_a_result.get("summary", {}),
                "semantic": jalur_b_result.get("summary", {}),
                "total_findings": len(all_findings),
            }

            # 7. Simpan hasil pemeriksaan.
            document.metadata = {
                **(document.metadata or {}),
                "jalur_a": jalur_a_result,
                "jalur_b": jalur_b_result,
                "summary": summary,
            }

            # 7b. Hitung skor di backend dan simpan ke AuditResult.
            result = build_result(jalur_a_result, jalur_b_result)

            AuditResult.objects.update_or_create(
                document=document,
                defaults={
                    "physical_score": result["format_score"],
                    "semantic_score": result["semantic_score"],
                    "final_score": result["total_score"],
                    "findings": result["findings"],
                    "recommendations": {
                        "has_format_score": result["has_format_score"],
                        "has_semantic_score": result["has_semantic_score"],
                    },
                },
            )

            document.status = "completed"
            document.save(
                update_fields=[
                    "metadata",
                    "status",
                    "updated_at",
                ]
            )

            # 8. Kirim hasil ke Flutter.
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
            logger.exception(
                "Pemeriksaan dokumen gagal. Document ID: %s",
                document.id,
            )
            traceback.print_exc()

            document.status = "failed"
            document.save(
                update_fields=["status", "updated_at"]
            )

            return Response(
                {
                    "detail": "Pemeriksaan dokumen gagal.",
                    "error": str(exc),
                    "document_id": document.id,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DocumentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Hanya ambil dokumen milik akun yang sedang login.
        documents = Document.objects.filter(
            user=request.user
        ).order_by("-uploaded_at")

        serializer = DocumentSerializer(
            documents,
            many=True,
        )

        return Response(
            {
                "documents": serializer.data,
                "count": documents.count(),
            },
            status=status.HTTP_200_OK,
        )


class DocumentResultView(APIView):
    """GET /api/v1/documents/<id>/result/ - hasil pemeriksaan satu dokumen."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        document = Document.objects.filter(pk=pk, user=request.user).first()

        if document is None:
            return Response(
                {"detail": "Dokumen tidak ditemukan."},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = get_document_result(document)

        if result is None:
            return Response(
                {"detail": "Hasil pemeriksaan belum tersedia."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "document_id": document.id,
                "file_name": document.title,
                "document_type": document.document_type,
                **result,
            },
            status=status.HTTP_200_OK,
        )
