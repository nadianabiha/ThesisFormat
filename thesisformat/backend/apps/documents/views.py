import logging
import traceback

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document
from .pipeline import check_document
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
            # 3-7. Jalur A (fisik) + Jalur B (AI) -> skor -> simpan.
            # Logikanya ada di pipeline.py agar sama dengan "Analisis ulang"
            # di Web Dashboard, dan setiap analisis AI tercatat (AIRun).
            checked = check_document(document, user=request.user)

            # 8. Kirim hasil ke Flutter.
            return Response(
                {
                    "document": DocumentSerializer(document).data,
                    "jalur_a": checked["jalur_a"],
                    "jalur_b": checked["jalur_b"],
                    "findings": checked["findings"],
                    "summary": checked["summary"],
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
