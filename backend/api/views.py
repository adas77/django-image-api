from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UploadSerializer

# TODO: upload


class UploadViewSet(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UploadSerializer

    def get(self, request):
        return Response("GET")

    def post(self, request):
        file_uploaded = request.FILES.get('file_uploaded')
        content_type = file_uploaded.content_type
        response = f'POST:{content_type}'
        return Response(response)
