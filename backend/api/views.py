
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Image
from .serializers import ImageSerializer
from .utils import Uploader


class ImageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ImageSerializer

    def get(self, request):
        images = Image.objects.filter(creator=request.user.pk)
        serializer = self.serializer_class(data=images, many=True)
        # FIXME:
        if serializer.is_valid():
            print("ddd")
        print(serializer.data)

        return Response(serializer.data)

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

            data = Uploader.handle_save_for_particular_tier(
                request.user, serializer)

            return Response(
                data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
