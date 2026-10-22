from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .parser.jalur_a_service import run_jalur_a
from .semantic.jalur_b_service import run_jalur_b
from .serializers import DocumentSerializer


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)

        if serializer.is_valid():
            document = serializer.save(user=request.user)

            jalur_a_result = run_jalur_a(document.file.path, rules=None)
            jalur_b_result = run_jalur_b(
                jalur_a_result["parsed_document"],
                document_type=document.document_type,
            )

            return Response(
                {
                    "document": DocumentSerializer(document).data,
                    "jalur_a": jalur_a_result,
                    "jalur_b": jalur_b_result,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )