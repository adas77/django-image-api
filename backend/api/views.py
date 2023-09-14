from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .utils.upload import Uploader

from .serializers import ImageSerializer


class ImageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ImageSerializer

    def get(self, request):
        user = request.user.uid
        return Response(f'Hi {user}')

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            file_ = serializer.validated_data['file']
            filename_content_type = file_.content_type

            try:
                Uploader.validate_extensions(filename_content_type)
            except Exception as e:
                return Response(
                    str(e),
                    status=status.HTTP_400_BAD_REQUEST
                )

            Uploader.handle_save_for_particular_tier(request.user, serializer)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
