import logging
import os
import traceback

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audits.models import AIRun

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
            # Pesan file (format/ukuran) ditampilkan langsung di aplikasi.
            file_errors = serializer.errors.get("file") or []
            return Response(
                {
                    "detail": str(file_errors[0]) if file_errors else "Data dokumen tidak valid.",
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


class DocumentRecheckView(APIView):
    """
    POST /api/v1/documents/<id>/recheck/ - cek ulang dokumen yang sudah
    diunggah tanpa unggah ulang. Opsional: {"document_type": "..."} untuk
    mengganti jenis dokumen sebelum dicek. Hasil lama ditimpa.
    Hanya pemilik dokumen yang boleh.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        document = Document.objects.filter(pk=pk, user=request.user).first()
        if document is None:
            return Response(
                {"detail": "Dokumen tidak ditemukan."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not document.file or not os.path.exists(document.file.path):
            return Response(
                {"detail": "File dokumen tidak ditemukan di server. Silakan unggah ulang."},
                status=status.HTTP_409_CONFLICT,
            )

        document_type = request.data.get("document_type")
        if document_type:
            valid_types = {value for value, _ in Document._meta.get_field("document_type").choices}
            if document_type not in valid_types:
                return Response(
                    {"detail": "Jenis dokumen tidak valid."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if document_type != document.document_type:
                document.document_type = document_type
                document.save(update_fields=["document_type", "updated_at"])

        try:
            check_document(document, trigger=AIRun.Trigger.RECHECK, user=request.user)
        except Exception as exc:
            logger.exception("Cek ulang gagal. Document ID: %s", document.id)
            return Response(
                {"detail": f"Cek ulang gagal: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        document.refresh_from_db()
        return Response(
            {
                "document_id": document.id,
                "file_name": document.title,
                "document_type": document.document_type,
                **get_document_result(document),
            },
            status=status.HTTP_200_OK,
        )
