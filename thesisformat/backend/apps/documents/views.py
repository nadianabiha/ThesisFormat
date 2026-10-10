from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .parser.jalur_a_service import run_jalur_a
from .serializers import DocumentSerializer


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)

        if serializer.is_valid():
            document = serializer.save(user=request.user)

            jalur_a_result = run_jalur_a(document.file.path, rules=None)

            return Response(
                {
                    "document": DocumentSerializer(document).data,
                    "jalur_a": jalur_a_result,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )